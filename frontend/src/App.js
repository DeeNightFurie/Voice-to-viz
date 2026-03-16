import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [status, setStatus] = useState("Ready");
  const [dataStatus, setDataStatus] = useState({});
  const [previewRows, setPreviewRows] = useState([]);
  const [previewColumns, setPreviewColumns] = useState([]);
  const [charts, setCharts] = useState({});
  const recognitionRef = useRef(null);
  const fileInputRef = useRef(null);

  // --- Voice setup ---
  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setStatus("❌ Voice recognition not supported in this browser");
      return;
    }

    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = "en-US";

    recognitionRef.current.onresult = (event) => {
      const command = event.results[0][0].transcript.toLowerCase().trim();
      setTranscript(command);
      setStatus(`🗣️ Heard: "${command}"`);
      handleVoiceCommand(command);
    };

    recognitionRef.current.onerror = () => {
      setIsListening(false);
      setStatus("Error - click to retry");
    };

    recognitionRef.current.onend = () => {
      setIsListening(false);
    };
  }, []);

  const startListening = useCallback(() => {
    if (recognitionRef.current && !isListening) {
      try {
        recognitionRef.current.start();
        setIsListening(true);
        setStatus("🎤 Listening... speak now!");
      } catch {
        setStatus("❌ Could not start microphone");
      }
    }
  }, [isListening]);

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
      setStatus("Stopped. Click 🎤 to listen again.");
    }
  };

  // --- Helper: fetch status ---
  const fetchStatus = async () => {
    setStatus("🔄 Checking data status...");
    const res = await fetch("http://localhost:8000/data/status");
    const data = await res.json();
    setDataStatus(data);
    if (data.loaded) {
      setStatus(
        `✅ Data loaded: ${data.filename} (${data.shape?.[0] || 0} rows)`,
      );
    } else {
      setStatus('📭 No data loaded yet. Say "upload data" first.');
    }
  };

  // --- Helper: fetch preview ---
  const fetchPreview = async () => {
    const res = await fetch("http://localhost:8000/data/preview");
    const data = await res.json();
    if (data.success) {
      setPreviewRows(data.rows);
      setPreviewColumns(data.columns || []);
      setStatus("👀 Showing cleaned data preview");
    } else {
      setStatus(data.message || "No data to preview");
    }
  };

  // --- Helper: visualize data (all charts) ---
  const visualizeAll = async () => {
    setStatus("📊 Generating all charts...");
    const res = await fetch("http://localhost:8000/visualize", {
      method: "POST",
    });
    const data = await res.json();
    if (data.success) {
      setCharts(data.charts || {});
      setStatus("✅ All charts generated! Scroll down to see.");
    } else {
      setStatus(data.message || "Visualization failed");
    }
  };

  // --- Helper: download cleaned data ---
  const downloadCleaned = async () => {
    try {
      setStatus("⬇️ Preparing cleaned data download...");
      const res = await fetch("http://localhost:8000/data/download");
      if (!res.ok) {
        const err = await res.json();
        setStatus(`❌ ${err.message || "Download failed"}`);
        return;
      }
      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "cleaned_data.csv";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setStatus("✅ Cleaned data downloaded");
    } catch (err) {
      setStatus(`❌ Download error: ${err.message}`);
    }
  };

  // --- Voice command handler ---
  const handleVoiceCommand = async (command) => {
    const c = command.toLowerCase();
    setStatus(`Processing: "${c}"`);

    try {
      // 1) UPLOAD DATA
      if (c.includes("upload") && c.includes("data")) {
        setStatus('📁 "upload data" detected → choose a file');
        fileInputRef.current?.click();
        return;
      }

      // 2) STATUS
      if (
        c.includes("status") ||
        c.includes("check data") ||
        c.includes("check status")
      ) {
        await fetchStatus();
        return;
      }

      // 3) REMOVE DUPLICATES
      if (c.includes("remove") && c.includes("duplicates")) {
        setStatus("🧹 Removing duplicates...");
        const res = await fetch(
          "http://localhost:8000/clean/remove-duplicates",
          { method: "POST" },
        );
        const result = await res.json();
        if (result.success) {
          setStatus(
            `✅ Removed ${result.removed || 0} duplicates. Saying "status" and showing preview.`,
          );
          await fetchStatus();
          await fetchPreview();
        } else {
          setStatus(`❌ ${result.message || "Clean failed"}`);
        }
        return;
      }

      // 4) REPRESENT DATA (visualize all)
      if (c.includes("represent") && c.includes("data")) {
        await visualizeAll(); // generate bar, line, pie, scatter, histogram
        await fetchPreview(); // refresh preview
        return;
      }

      setStatus(
        `❓ Unknown command "${c}". Try: "upload data", "status", "remove duplicates", "represent data".`,
      );
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
    }
  };

  // --- File upload handler ---
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setStatus(`📤 Uploading ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      const result = res.data;

      if (result.auto_loaded) {
        setStatus(
          `✅ ${file.name} uploaded & loaded! Saying "status" and showing preview.`,
        );
        await fetchStatus();
        await fetchPreview();
      } else {
        setStatus(
          `✅ ${file.name} uploaded. Now say "status" to check and "represent data" to visualize.`,
        );
      }
    } catch (error) {
      setStatus(`❌ Upload failed: ${error.message}`);
    } finally {
      event.target.value = "";
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎤 Voice Data Viz</h1>

        {/* Voice Control */}
        <div className="voice-control">
          <button
            onClick={isListening ? stopListening : startListening}
            className={isListening ? "listening" : ""}
          >
            {isListening ? "🛑 STOP" : "🎤 LISTEN"}
          </button>
          <div className="status">{status}</div>
          <div className="transcript">Heard: "{transcript}"</div>
        </div>

        {/* Upload */}
        <div className="upload-section">
          <h3>📁 Upload CSV/Excel</h3>
          <input
            ref={fileInputRef}
            id="file-upload"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileUpload}
            style={{ display: "block" }}
          />
        </div>

        {/* Data Status */}
        {Object.keys(dataStatus).length > 0 && (
          <div className="data-status">
            <h3>Data Status</h3>
            <pre>{JSON.stringify(dataStatus, null, 2)}</pre>
          </div>
        )}

        {/* Cleaned Data Preview */}
        {previewRows.length > 0 && (
          <div className="preview">
            <h3>Cleaned Data Preview</h3>
            <table>
              <thead>
                <tr>
                  {previewColumns.map((col) => (
                    <th key={col}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {previewRows.map((row, idx) => (
                  <tr key={idx}>
                    {previewColumns.map((col) => (
                      <td key={col}>{row[col]}</td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Visualization gallery: bar, line, pie, scatter, histogram */}
        {Object.keys(charts).length > 0 && (
          <div className="charts-gallery">
            <h3>📊 All Visualizations</h3>
            <div className="chart-grid">
              {Object.entries(charts).map(([type, url]) => (
                <div key={type} className="chart-item">
                  <h4>{type.charAt(0).toUpperCase() + type.slice(1)}</h4>
                  <iframe
                    src={`http://localhost:8000${url}`}
                    title={`${type} chart`}
                    width="100%"
                    height="250"
                    frameBorder="0"
                    style={{ borderRadius: "8px" }}
                  />
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Download button */}
        <div style={{ marginTop: "20px" }}>
          <button onClick={downloadCleaned}>
            ⬇️ Download Cleaned Data (CSV)
          </button>
        </div>

        {/* Help */}
        <div className="commands">
          <h4>Say:</h4>
          <ul>
            <li>"upload data" → Upload & load</li>
            <li>"status" → Check data status</li>
            <li>"remove duplicates" → Clean data & refresh preview</li>
            <li>"represent data" → Bar, line, pie, scatter, histogram</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
