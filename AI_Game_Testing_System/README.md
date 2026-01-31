# PROJECTX - AI Game Testing System

## Project Title
**PROJECTX - Autonomous Agentic Verification System**

## Brief Description

PROJECTX is an intelligent, AI-powered game testing system that leverages Reinforcement Learning (RL) algorithms to autonomously test video games. The system uses advanced machine learning techniques to explore game states, detect crashes, and identify bugs without human intervention.

### Key Features:
- 🤖 **Autonomous Testing**: Uses RL agents to automatically test games
- 🎮 **Multi-Genre Support**: Supports Platformer, FPS, Racing, and RPG games
- 🧠 **Multiple RL Algorithms**: Implements PPO, DQN, SAC, and HRL algorithms
- 📊 **Real-time Analytics**: Live metrics dashboard with coverage tracking and crash detection
- 🖥️ **Web-based Interface**: Modern React dashboard for monitoring and control
- 📈 **Test History**: Persistent storage and retrieval of test results
- 🎯 **State Coverage**: Tracks unique game states discovered during testing
- ⚠️ **Crash Detection**: Automatically detects game crashes and freezes

### How It Works:
1. The system captures the game screen in real-time
2. RL agents analyze the current state and decide on actions
3. Actions are executed automatically (keyboard/mouse inputs)
4. The system tracks coverage, detects crashes, and calculates rewards
5. Agents learn from experience to improve testing strategies
6. Results are displayed in a real-time dashboard

---

## Technologies Used

### Backend
- **Python 3.9+**: Core programming language
- **FastAPI**: Modern, fast web framework for building APIs
- **Uvicorn**: ASGI server for running FastAPI
- **Stable-Baselines3**: Reinforcement Learning library
- **Gymnasium**: RL environment interface (formerly OpenAI Gym)
- **PyTorch**: Deep learning framework
- **OpenCV**: Computer vision and image processing
- **MSS (Multi-Screen Shot)**: Fast screen capture library
- **PyAutoGUI**: Automated GUI interaction (keyboard/mouse control)
- **psutil**: System and process utilities
- **pywin32**: Windows API integration (optional, for enhanced window detection)
- **Pydantic**: Data validation using Python type annotations
- **pytest**: Testing framework

### Frontend
- **React 19.2**: Modern JavaScript library for building user interfaces
- **Vite**: Next-generation frontend build tool
- **Tailwind CSS**: Utility-first CSS framework
- **Recharts**: Composable charting library for React
- **Axios**: Promise-based HTTP client
- **Framer Motion**: Animation library for React
- **Lucide React**: Icon library

### Development Tools
- **Git**: Version control
- **ESLint**: JavaScript linter
- **pytest-asyncio**: Async testing support

### Data Storage
- **JSON Files**: Test history and configuration storage
- **localStorage/sessionStorage**: Client-side authentication storage

---

## Student Information

**Student Name:** Rahul Rajeev

**Contact Details:**
- **Email:** rajeevrahul818@gmail.com
- **Phone:** 6282548654
- **Institution:** Saintgits College Of Engineering
- **Department:** Department of Computer Applications

---

## Project Guide

**Guide Name:** Dr.Sundandha Rajagopal

**Guide Designation:** [Designation/Title]

**Contact Details:**
- **Email:** [guide.email@example.com]
- **Department:** [Department Name]

---

## Project Structure

```
AI_Game_Testing_System/
├── backend/                 # Python FastAPI backend
│   ├── controllers/        # Business logic controllers
│   ├── services/           # Core services
│   │   ├── agents/       # RL agent implementations
│   │   ├── env/           # Game environment components
│   │   └── analytics/     # Analytics and tracking
│   ├── routes/            # API route definitions
│   ├── models/            # Data models and schemas
│   ├── utils/             # Utility functions
│   ├── config/             # Configuration settings
│   └── tests/              # Test suite
│
└── frontend/               # React + Vite frontend
    ├── src/
    │   ├── components/    # React components
    │   ├── services/      # API service functions
    │   └── utils/         # Utility functions
    └── package.json        # Node.js dependencies
```

---

## Quick Start

### Prerequisites
- Python 3.9 or higher
- Node.js 18+ and npm
- Windows OS (for game testing)

### Backend Setup
```bash
cd AI_Game_Testing_System/backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn app:app --reload
```

### Frontend Setup
```bash
cd AI_Game_Testing_System/frontend
npm install
npm run dev
```

### Access the Application
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

---

## Key Modules

### Reinforcement Learning Agents
- **PPO (Proximal Policy Optimization)**: Default algorithm, stable and sample-efficient
- **DQN (Deep Q-Network)**: Value-based method for discrete actions
- **SAC (Soft Actor-Critic)**: Actor-critic method for continuous actions
- **HRL (Hierarchical Reinforcement Learning)**: Two-level hierarchy for complex scenarios

### Game Environment
- **Screen Capture**: Real-time game screen capture using MSS
- **Action Execution**: Automated keyboard/mouse input via PyAutoGUI
- **State Processing**: Image preprocessing, frame stacking, normalization
- **Reward Engine**: Multi-objective reward calculation

### Analytics
- **Coverage Tracker**: Tracks unique game states discovered
- **Crash Detector**: Detects game crashes and freezes
- **Metrics Collector**: Aggregates and stores performance metrics

---

## API Endpoints

### Main API
- `POST /api/start-test`: Start a new test session
- `POST /api/stop-test`: Stop current test session
- `GET /api/metrics`: Get current metrics
- `POST /api/reset-status`: Reset system status

### History API
- `GET /api/history`: Get all test history
- `GET /api/history/{test_id}`: Get specific test result
- `DELETE /api/history/{test_id}`: Delete test result
- `GET /api/history/statistics`: Get test statistics

### Windows API
- `GET /api/windows`: Get active game windows
- `GET /api/windows/{hwnd}/focused`: Check window focus status

---

## Documentation

For detailed setup and usage instructions, see:
- **Setup Guide**: `SETUP_AND_RUN.md`
- **Quick Start**: `QUICK_START.md`
- **API Documentation**: Available at `/docs` endpoint when server is running

---

## License

[Specify your license here, e.g., MIT, Apache 2.0, or Educational Use Only]

---

## Acknowledgments

- Stable-Baselines3 team for the excellent RL library
- FastAPI team for the modern web framework
- React team for the powerful UI library
- All open-source contributors whose libraries made this project possible

---

## Future Enhancements

- Database integration (PostgreSQL/MongoDB)
- Multi-game parallel testing
- Advanced HRL with more levels
- Cloud deployment support
- CI/CD pipeline integration
- Mobile game testing support

---

**Last Updated:** [Current Date]

**Version:** 1.0.0

