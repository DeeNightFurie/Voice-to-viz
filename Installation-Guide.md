# Voice Data Visualization App - Installation Guide

A voice-controlled web application for uploading, cleaning, and visualizing data using CSV/Excel files.

## 📋 Table of Contents
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Backend Setup](#backend-setup)
- [Frontend Setup](#frontend-setup)
- [Running the Application](#running-the-application)
- [Testing the Application](#testing-the-application)
- [Voice Commands](#voice-commands)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software
- **Python 3.8+** - [Download Python](https://www.python.org/downloads/)
- **Node.js 16+** and **npm** - [Download Node.js](https://nodejs.org/)
- **Git** - [Download Git](https://git-scm.com/downloads)

### Verify Installation
Open your terminal and run:
```bash
python --version
# Should show: Python 3.8.x or higher

node --version
# Should show: v16.x.x or higher

npm --version
# Should show: 8.x.x or higher
```

---

## Project Structure

```
voice-data-viz/
├── backend/
│   ├── main.py                 # FastAPI app entry point
│   ├── models.py               # Pydantic data models
│   ├── auth.py                 # JWT authentication (optional)
│   ├── data_processor.py       # Data cleaning logic
│   ├── visualizer.py           # Plotly chart generation
│   ├── upload_handler.py       # File upload handler
│   ├── requirements.txt        # Python dependencies
│   ├── uploads/                # Uploaded files (auto-created)
│   ├── processed_data/         # Cleaned data (auto-created)
│   └── visualizations/         # Generated charts (auto-created)
│
└── frontend/
    ├── public/
    │   └── index.html          # React entry HTML
    ├── src/
    │   ├── App.js              # Main React component
    │   ├── App.css             # Styling
    │   └── index.js            # React entry point
    └── package.json            # Node dependencies
```

---

## Backend Setup

### Step 1: Clone the Repository
```bash
git clone https://github.com/YOUR_USERNAME/voice-data-viz.git
cd voice-data-viz
```

### Step 2: Navigate to Backend Directory
```bash
cd backend
```

### Step 3: Create Python Virtual Environment (Recommended)
```bash
# On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

# On Windows:
python -m venv .venv
.venv\Scripts\activate
```

You should see `(.venv)` in your terminal prompt.

### Step 4: Install Python Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (ASGI server)
- Pandas (data processing)
- Plotly (visualizations)
- Python-Jose & Passlib (authentication)
- And other required packages

### Step 5: Verify Backend Installation
```bash
python -c "import fastapi, pandas, plotly; print('✅ All imports successful')"
```

If you see `✅ All imports successful`, the backend is ready!

---

## Frontend Setup

### Step 1: Navigate to Frontend Directory
Open a **new terminal window** (keep backend terminal open) and run:
```bash
cd voice-data-viz/frontend
```

### Step 2: Install Node Dependencies
```bash
npm install
```

This installs:
- React 18
- Axios (HTTP client)
- Plotly.js (chart library)
- React Scripts (development server)

**Note:** This may take 2-5 minutes depending on your internet speed.

### Step 3: Verify Frontend Installation
```bash
npm list react react-dom axios
```

You should see the installed versions without errors.

---

## Running the Application

### Terminal 1: Start Backend Server
```bash
cd backend
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [12345] using WatchFiles
INFO:     Application startup complete.
```

**✅ Backend is now running at:** `http://localhost:8000`

**API Documentation:** Open `http://localhost:8000/docs` in your browser to see interactive API docs.

---

### Terminal 2: Start Frontend Server
In a **new terminal window**:
```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!

You can now view voice-data-viz-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

**✅ Frontend is now running at:** `http://localhost:3000`

Your browser should automatically open to `http://localhost:3000`.

---

## Testing the Application

### Step 1: Open the Application
Navigate to `http://localhost:3000` in your browser (Chrome/Edge/Safari recommended for best voice recognition support).

### Step 2: Test File Upload
1. **Click the file input** or say **"upload data"**
2. Choose a CSV or Excel file (e.g., `iris.csv`, sales data, etc.)
3. Wait for confirmation: `✅ filename.csv uploaded successfully!`

### Step 3: Check Data Status
1. **Click the 🎤 microphone button** to start listening
2. Say **"check data"** or **"status"**
3. You should see data information displayed (rows, columns, filename)

### Step 4: Clean Data
1. Click 🎤 and say **"remove duplicates"**
2. Wait for result: `✅ Removed X duplicates`
3. Say **"status"** again to verify updated data

### Step 5: Test Backend API Directly
Open `http://localhost:8000/docs` and test endpoints:
- `POST /upload` - Upload a test file
- `GET /data/status` - Check loaded data
- `POST /clean/remove-duplicates` - Clean data

---

## Voice Commands

The application supports these voice commands (must click 🎤 button first):

| Voice Command | Action |
|--------------|--------|
| **"upload data"** / **"upload file"** | Opens file picker for CSV/Excel upload |
| **"status"** / **"check data"** / **"check"** | Shows current data status (rows, columns, filename) |
| **"remove duplicates"** | Removes duplicate rows from loaded data |
| **"load"** | Shows list of uploaded files |

### Voice Recognition Tips:
- **Speak clearly** and at normal pace
- Use **exact phrases** listed above for best results
- Wait for status feedback before next command
- **Browser must support Web Speech API** (Chrome, Edge, Safari on macOS)
- Firefox may have limited support

---

## Troubleshooting

### Backend Issues

#### Error: `Could not import module "main"`
**Solution:** Make sure you're running uvicorn from inside the `backend/` directory:
```bash
cd backend
uvicorn main:app --reload --port 8000
```

#### Error: `No module named 'fastapi'` or similar
**Solution:** Activate virtual environment and reinstall:
```bash
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Error: `500 Internal Server Error` on upload
**Solution:** Check backend terminal for detailed error. Common fixes:
```bash
# Missing pandas import
pip install pandas

# Re-run backend
uvicorn main:app --reload --port 8000
```

#### Port 8000 already in use
**Solution:**
```bash
# Find and kill the process using port 8000
# macOS/Linux:
lsof -ti:8000 | xargs kill -9

# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

### Frontend Issues

#### Error: `react-scripts: command not found`
**Solution:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

#### Error: `Port 3000 is already in use`
**Solution:** Kill existing process or use different port:
```bash
# Kill process on port 3000
# macOS/Linux:
lsof -ti:3000 | xargs kill -9

# Or start on different port:
PORT=3001 npm start
```

#### Voice recognition not working
**Solution:**
- **Use Chrome or Edge** (best support)
- **Allow microphone permissions** when browser asks
- **Use HTTPS** in production (localhost HTTP is fine for dev)
- Check browser console for errors (F12 → Console tab)

#### Upload returns 404 or CORS error
**Solution:** Verify backend is running on port 8000:
```bash
curl http://localhost:8000/data/status
```

If this fails, restart backend server.

---

### Common File Issues

#### Uploaded file not loading
**Solution:** Check the file format and path:
1. File must be `.csv` or `.xlsx`
2. Check `backend/uploads/` folder has the file
3. Try loading manually via API docs: `http://localhost:8000/docs`

#### "File too large" error
**Solution:** Default limit is 10MB. To increase:

Edit `backend/upload_handler.py`:
```python
self.max_file_size = 50 * 1024 * 1024  # Change to 50MB
```

---

## Environment Variables (Optional)

For production deployment, create a `.env` file in the `backend/` directory:

```bash
# backend/.env
SECRET_KEY=your-secure-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Generate a secure SECRET_KEY:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Development Workflow

### Making Changes to Backend
1. Edit Python files in `backend/`
2. **No restart needed** - Uvicorn auto-reloads on file changes
3. Check terminal for any import errors

### Making Changes to Frontend
1. Edit files in `frontend/src/`
2. **No restart needed** - React auto-reloads on save
3. Check browser console (F12) for errors

---

## Stopping the Application

### Stop Backend
In backend terminal, press **Ctrl+C**

### Stop Frontend
In frontend terminal, press **Ctrl+C**

### Deactivate Python Virtual Environment
```bash
deactivate
```

---

## Next Steps

Once installation is complete:
1. ✅ Upload sample CSV files (try Kaggle datasets)
2. ✅ Test all voice commands
3. ✅ Explore API documentation at `/docs`
4. 🚀 Add new features (custom cleaning operations, more chart types)
5. 🚀 Deploy to production (Heroku, AWS, Docker)

---

## Support & Contributing

- **Issues:** Open an issue on GitHub if you encounter problems
- **Documentation:** See additional docs in `/docs` folder
- **Contributing:** Pull requests are welcome!

---

## License

[Add your license here - MIT, Apache 2.0, etc.]

---

## Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend framework
- [Plotly](https://plotly.com/) - Data visualization
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API) - Voice recognition

---

**Happy Data Visualizing! 🎤📊**