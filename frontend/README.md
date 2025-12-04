# Business Wargame Frontend

A React-based frontend application for running AI-powered business wargame simulations with decision tree visualization.

## Features

- 🎯 **Interactive Form Interface**: Configure business goals, player profiles, and game metrics
- 🌳 **Decision Tree Visualization**: Interactive tree diagram showing all possible strategic paths
- 🤖 **AI-Powered Simulation**: Integration with backend MaxN algorithm and AI agents
- 📊 **Results Dashboard**: Clear visualization of optimal strategies and scores
- 🎨 **Modern UI**: Responsive design with gradient backgrounds and smooth animations

## Technology Stack

- **React 19.2** - Modern React with hooks
- **Vite 7.2** - Fast build tool and dev server
- **Axios** - HTTP client for API communication
- **react-d3-tree** - Interactive decision tree visualization
- **CSS3** - Modern styling with gradients and animations

## Getting Started

### Prerequisites

- Node.js 20+
- npm or yarn
- Backend API running (see backend README)

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env and set VITE_API_URL to your backend URL
```

### Development

```bash
# Start development server
npm run dev

# Access the application at http://localhost:5173
```

### Building for Production

```bash
# Build the application
npm run build

# Preview the build
npm run preview
```

### Docker Deployment

```bash
# Build and run with Docker Compose (from project root)
docker-compose up

# Or build frontend only
docker build -t wargame-frontend .
docker run -p 5173:5173 wargame-frontend
```

## Usage Guide

### 1. Configure General Settings

- **Business Goal**: Enter your strategic objective
- **Time Periods**: Set the simulation horizon (1-12)
- **Time Unit**: Choose quarter, month, year, or week

### 2. Set Current Metrics

Enter your current business metrics:

- Revenue
- Market Share (%)
- Customer Satisfaction
- Brand Awareness

### 3. Define Players

- **Your Company**: Configure your company profile
- **Competitors**: Add one or more competitor profiles
- For each player, provide:
  - Company name
  - Business goal
  - About/description
  - Customer segments

### 4. Action Set (Optional)

- Enter strategic actions (one per line)
- Leave empty to auto-generate using AI

### 5. Run Simulation

Click "Run Wargame Simulation" to execute the MaxN algorithm and display results.

### 6. View Results

The results page shows:

- **Best Strategic Move**: Recommended action
- **Optimal Score**: Expected outcome value
- **Decision Tree**: Visual representation of all paths

## Environment Variables

- `VITE_API_URL`: Backend API URL (default: `http://localhost:8000`)

## License

Part of "A Hybrid AI-Powered Strategic Wargame" project.
