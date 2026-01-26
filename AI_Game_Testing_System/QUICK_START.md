# Quick Start Guide

## 🚀 Fast Setup (5 minutes)

### 1. Backend Setup

```bash
cd AI_Game_Testing_System/backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Frontend Setup

```bash
cd AI_Game_Testing_System/frontend

# Install dependencies
npm install
```

### 3. Run Application

**Terminal 1 - Backend:**
```bash
cd AI_Game_Testing_System/backend
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd AI_Game_Testing_System/frontend
npm run dev
```

### 4. Open Browser

Navigate to: **http://localhost:5173**

---

## 📋 Prerequisites

- Python 3.9+
- Node.js 18+
- npm (comes with Node.js)

---

## 🔧 Common Commands

### Backend
```bash
# Run server
python app.py

# Run tests
pytest

# Check API docs
# Visit http://localhost:8000/docs
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## ⚙️ Configuration

Optional: Create `backend/.env`:
```env
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:5173
```

---

## 🆘 Troubleshooting

**Port in use?**
- Backend: Change `API_PORT` in `.env`
- Frontend: Vite auto-finds next port

**Import errors?**
- Ensure virtual environment is activated
- Reinstall: `pip install -r requirements.txt`

**CORS errors?**
- Check backend is running on port 8000
- Verify `CORS_ORIGINS` includes frontend URL

---

For detailed instructions, see **SETUP_AND_RUN.md**

