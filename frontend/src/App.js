import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [status, setStatus] = useState("Ready");
  const [dataStatus, setDataStatus] = useState({});
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
            `✅ Removed ${result.removed || 0} duplicates. Say "status" to check.`,
          );
        } else {
          setStatus(`❌ ${result.message || "Clean failed"}`);
        }
        return;
      }

      // Unknown command
      setStatus(
        `❓ Unknown command "${c}". Try: "upload data", "status", "remove duplicates".`,
      );
    } catch (err) {
      setStatus(`❌ Error: ${err.message}`);
    }
  };

  // --- File upload handler (upload + auto-load in backend) ---
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
          `✅ ${file.name} uploaded & loaded! Say "status" to check the data.`,
        );
      } else {
        setStatus(
          `✅ ${file.name} uploaded. Now call "status" to see if data loaded.`,
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

        {/* Status JSON */}
        {Object.keys(dataStatus).length > 0 && (
          <pre className="data-status">
            {JSON.stringify(dataStatus, null, 2)}
          </pre>
        )}

        <div className="commands">
          <h4>Say:</h4>
          <ul>
            <li>"upload data" → Open file picker & upload</li>
            <li>"status" → Check data status</li>
            <li>"remove duplicates" → Clean data</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
