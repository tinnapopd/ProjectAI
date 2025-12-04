import { useState } from "react";
import { runWargame, validateRequest } from "./services/api";
import WargameForm from "./components/WargameForm";
import DecisionTree from "./components/DecisionTree";
import Particles from "./components/Particles";
import "./App.css";

function App() {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleRunWargame = async (requestData) => {
    // Validate request data
    const validation = validateRequest(requestData);
    if (!validation.valid) {
      setError(validation.errors.join("; "));
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await runWargame(requestData);
      setResult(response);
    } catch (err) {
      console.error("Error running wargame:", err);
      setError(
        err.response?.data?.detail ||
          err.message ||
          "An error occurred while running the simulation"
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <Particles />
      <header className="app-header">
        <h1>🎯 AI-Powered Business Wargame</h1>
        <p>Strategic Decision-Making with Multi-Agent Simulation</p>
      </header>

      <main className="app-main">
        <div className="split-layout">
          <div className="form-panel">
            <WargameForm onSubmit={handleRunWargame} loading={loading} />
          </div>

          <div className="results-panel">
            {!result && !error && (
              <div className="empty-state">
                <div className="empty-icon">🌳</div>
                <h3>Decision Tree</h3>
                <p>Run a simulation to visualize the strategic decision tree</p>
              </div>
            )}

            {result && (
              <div className="results-container">
                <div className="results-summary">
                  <div className="summary-card">
                    <h3>Best Strategic Move</h3>
                    <p className="best-move">{result.best_move}</p>
                  </div>

                  <div className="summary-card">
                    <h3>Optimal Score</h3>
                    <p className="score">{result.best_score?.toFixed(2)}</p>
                  </div>

                  <div className="summary-card">
                    <h3>Time Horizon</h3>
                    <p className="time-period">
                      {result.time_periods} {result.time_period_unit}
                      {result.time_periods > 1 ? "s" : ""}
                    </p>
                  </div>
                </div>

                <div className="tree-section">
                  <h3>Decision Tree Visualization</h3>
                  <DecisionTree
                    treeData={result.tree_structure}
                    bestMove={result.best_move}
                  />
                </div>
              </div>
            )}

            {error && (
              <div className="error-message">
                <div className="error-icon">⚠️</div>
                <h3>Oops! Something went wrong</h3>
                <p>{error}</p>
                <button onClick={() => setError(null)} className="btn-dismiss">
                  Dismiss
                </button>
              </div>
            )}
          </div>
        </div>

        {loading && (
          <div className="loading-overlay">
            <div className="loading-content">
              <div className="loading-spinner-wrapper">
                <div className="loading-spinner"></div>
                <div className="loading-spinner-inner"></div>
              </div>
              <p>🤖 Running AI simulation...</p>
              <small>
                Analyzing strategic scenarios with multi-agent system
              </small>
            </div>
          </div>
        )}
      </main>

      <footer className="app-footer">
        <p>A Hybrid AI-Powered Strategic Wargame System</p>
      </footer>
    </div>
  );
}

export default App;
