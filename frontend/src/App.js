import React, { useState } from "react";
import GameSetup from "./components/GameSetup";
import DecisionTree from "./components/DecisionTree";
import StrategicMoves from "./components/StrategicMoves";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [businessGoal, setBusinessGoal] = useState("");
  const [moves, setMoves] = useState([]);
  const [selectedMove, setSelectedMove] = useState(null);
  const [gameState, setGameState] = useState(null);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-5xl font-bold text-white mb-2">
            🎯 Strategic Wargame AI
          </h1>
          <p className="text-purple-300 text-lg">
            AI-Powered Strategic Decision Tree Visualization
          </p>
        </header>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Panel - Game Setup */}
          <div className="lg:col-span-1">
            <GameSetup
              sessionId={sessionId}
              setSessionId={setSessionId}
              businessGoal={businessGoal}
              setBusinessGoal={setBusinessGoal}
              setMoves={setMoves}
              setGameState={setGameState}
            />
          </div>

          {/* Middle Panel - Strategic Moves */}
          <div className="lg:col-span-1">
            <StrategicMoves
              moves={moves}
              selectedMove={selectedMove}
              setSelectedMove={setSelectedMove}
              businessGoal={businessGoal}
            />
          </div>

          {/* Right Panel - Decision Tree Visualization */}
          <div className="lg:col-span-1">
            <DecisionTree
              selectedMove={selectedMove}
              gameState={gameState}
              businessGoal={businessGoal}
              sessionId={sessionId}
            />
          </div>
        </div>

        {/* Footer */}
        <footer className="text-center mt-12 text-purple-300">
          <p className="text-sm">
            Powered by Google Gemini AI | MaxN Search Algorithm
          </p>
        </footer>
      </div>
    </div>
  );
}

export default App;
