# AI-Powered Business Wargame System

A hybrid AI-powered strategic wargame system for business decision-making using multi-agent simulation and MaxN algorithm.

## 🎯 Project Overview

This system helps businesses make strategic decisions by simulating competitive scenarios using AI agents. It employs a MaxN algorithm to explore decision trees and recommends optimal strategies based on multi-player game theory.

### Key Features

- 🤖 **AI-Powered Strategy Generation**: Uses Google's Gemini AI to generate and evaluate strategic moves
- 🌳 **Decision Tree Visualization**: Interactive D3-based tree showing all possible outcomes
- 🎮 **Multi-Player Simulation**: Simulate competitive scenarios with multiple players
- 📊 **Strategic Evaluation**: Heuristic scoring based on business metrics
- 🔄 **Time-Based Planning**: Plan across multiple time periods (quarters, months, years)
- 🎨 **Modern Web Interface**: React-based responsive UI

## 🏗️ Architecture

### Backend (FastAPI + Python)

- **MaxN Controller**: Implements MaxN algorithm for multi-player game trees
- **AI Agents**:
  - Strategy Agent: Generates possible moves
  - Opponent Agent: Simulates competitor responses
  - Evaluator Agent: Scores outcomes based on business metrics
- **RESTful API**: FastAPI endpoints for simulation execution

### Frontend (React + Vite)

- **Interactive Forms**: Configure business scenarios
- **Decision Tree Visualization**: D3.js-based interactive trees
- **Results Dashboard**: Display optimal strategies and scores
- **Responsive Design**: Works on desktop and mobile

## 🚀 Quick Start

See [QUICKSTART.md](QUICKSTART.md) for detailed setup instructions.

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd ProjectAI

# Start the application
docker-compose up --build

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

**Backend:**

```bash
cd backend
pip install -r requirements.txt

# Set environment variable
export GOOGLE_API_KEY="your-api-key"

# Run the server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**

```bash
cd frontend
npm install
npm run dev
```

## 📁 Project Structure

```
ProjectAI/
├── backend/               # FastAPI backend
│   ├── api/              # API routes and dependencies
│   ├── core/             # Core engine and agents
│   ├── main.py           # Application entry point
│   ├── schemas.py        # Pydantic models
│   └── requirements.txt
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API services
│   │   ├── constants/   # Application constants
│   │   └── examples/    # Sample data
│   ├── Dockerfile
│   └── package.json
├── compose.yaml          # Docker Compose configuration
├── QUICKSTART.md        # Quick start guide
└── README.md           # This file
```

## 🎮 Usage

1. **Define Business Goal**: Enter your strategic objective
2. **Configure Players**: Add your company and competitors
3. **Set Metrics**: Input current business metrics (revenue, market share, etc.)
4. **Provide Actions**: Enter possible strategic moves or let AI generate them
5. **Run Simulation**: Execute the wargame simulation
6. **Analyze Results**: Review the decision tree and optimal strategy

## 🔧 Configuration

### Environment Variables

**Backend (.env or environment):**

- `GOOGLE_API_KEY`: Google AI API key (required)
- `ENVIRONMENT`: local/staging/production
- `DEFAULT_PLAYERS`: Number of players (default: 3)
- `TIME_PERIODS`: Simulation time periods (default: 4)
- `TIME_PERIOD_UNIT`: quarter/month/year/week
- `FRONTEND_HOST`: Frontend URL for CORS

**Frontend (.env):**

- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## 📚 Documentation

- [Backend README](backend/README.md) - Backend setup and API details
- [Frontend README](frontend/README.md) - Frontend setup and components
- [Quick Start Guide](QUICKSTART.md) - Step-by-step setup
- [Frontend Summary](FRONTEND_SUMMARY.md) - Complete frontend implementation details
- API Documentation: http://localhost:8000/docs (when running)

## 🧪 Testing

### Sample Scenario

**Business Goal:**

```
Increase market share by 15% and become the leading player in the enterprise software segment
```

**Players:**

- TechCorp Solutions (Your Company)
- DataSoft Inc (Competitor 1)
- CloudVision Systems (Competitor 2)

**Metrics:**

- Revenue: 5,000,000
- Market Share: 25%
- Customer Satisfaction: 4.2
- Brand Awareness: 65

See [QUICKSTART.md](QUICKSTART.md) for complete test scenario.

## 🛠️ Technology Stack

### Backend

- Python 3.11+
- FastAPI 0.118+
- Google Gemini AI (google-genai, google-adk)
- Pydantic for data validation
- Uvicorn as ASGI server

### Frontend

- React 19.2
- Vite 7.2
- Axios for API calls
- react-d3-tree for visualization
- CSS3 for styling

### DevOps

- Docker & Docker Compose
- Nginx (production)
- Environment-based configuration

## 🤝 Contributing

This is an academic project for AI course with Aj.Sukree.

## 📄 License

Academic project - Master's Degree in Artificial Intelligence

## 👥 Authors

- Project: AI-Powered Business Wargame
- Course: Artificial Intelligence
- Instructor: Aj.Sukree

## 🙏 Acknowledgments

- Google Gemini AI for powering the strategic agents
- FastAPI for the excellent web framework
- React and D3.js communities for visualization tools

## 📞 Support

For issues or questions:

1. Check the documentation in backend/ and frontend/ directories
2. Review the API docs at http://localhost:8000/docs
3. See example data in frontend/src/examples/
