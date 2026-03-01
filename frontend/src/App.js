import React, { useState, useEffect, useRef, useCallback } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [status, setStatus] = useState("Ready");
  const [dataStatus, setDataStatus] = useState({});
  const recognitionRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition =
      window.SpeechRecognition || window.webkitSpeechRecognition;
    recognitionRef.current = new SpeechRecognition();
    recognitionRef.current.continuous = false;
    recognitionRef.current.interimResults = false;
    recognitionRef.current.lang = "en-US";

    recognitionRef.current.onresult = (event) => {
      const command = event.results[0][0].transcript.toLowerCase();
      setTranscript(command);

      // Visual feedback for EVERY command
      setStatus(`🗣️ Heard: "${command}"`);

      // Process command
      handleCommand(command);
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
      recognitionRef.current.start();
      setIsListening(true);
      setStatus("🎤 Listening... speak now!");
    }
  }, [isListening]);

  const stopListening = () => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const handleCommand = async (command) => {
    // IMMEDIATE visual feedback
    if (command.includes("upload")) {
      setStatus("📁 Upload section activated!");
      document.getElementById("file-upload").click(); // Auto-trigger
    } else if (command.includes("status")) {
      setStatus("🔄 Checking data status...");
      try {
        const res = await axios.get("http://localhost:8000/data/status");
        setDataStatus(res.data);
        setStatus(`✅ ${res.data.filename || "No data loaded"}`);
      } catch {
        setStatus("❌ Backend error - check localhost:8000");
      }
    } else if (command.includes("remove")) {
      setStatus("🧹 Removing duplicates...");
    } else {
      setStatus(`❓ Unknown: "${command}" - Try "upload data" or "status"`);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    setStatus(`📤 Uploading ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);

    try {
      await axios.post("http://localhost:8000/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setStatus(`✅ ${file.name} uploaded! Say "status"`);
    } catch (error) {
      setStatus(`❌ Upload failed: ${error.message}`);
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
            id="file-upload"
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={handleFileUpload}
            style={{ display: "block" }}
          />
        </div>

        {/* Status */}
        {Object.keys(dataStatus).length > 0 && (
          <pre className="data-status">
            {JSON.stringify(dataStatus, null, 2)}
          </pre>
        )}

        <div className="commands">
          <h4>Say:</h4>
          <ul>
            <li>"upload data" → Auto upload</li>
            <li>"status" → Check data</li>
            <li>"remove duplicates" → Clean data</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
