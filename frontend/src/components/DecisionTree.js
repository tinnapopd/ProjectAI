import React, { useState, useEffect } from "react";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

function DecisionTree({ selectedMove, gameState, businessGoal, sessionId }) {
  const [expandedPath, setExpandedPath] = useState(0);
  const [treeData, setTreeData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch decision tree when a move is selected
  useEffect(() => {
    if (selectedMove && gameState && sessionId) {
      fetchDecisionTree();
    }
  }, [selectedMove?.move_id]); // Re-fetch when move changes

  const fetchDecisionTree = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/agent/get_decision_tree`,
        {
          game_state: gameState,
          selected_move: selectedMove,
        },
        {
          params: { session_id: sessionId, depth: 2 },
        }
      );

      setTreeData(response.data.tree.root);
    } catch (err) {
      console.error("Error fetching decision tree:", err);
      setError(
        err.response?.data?.detail || "Failed to generate decision tree"
      );
    } finally {
      setLoading(false);
    }
  };

  const renderNode = (node, isExpanded = false) => (
    <div
      className={`
        px-4 py-3 rounded-lg border-2 transition-all cursor-pointer
        ${
          node.player === "Us"
            ? "bg-blue-600 border-blue-400 hover:bg-blue-500"
            : "bg-red-600 border-red-400 hover:bg-red-500"
        }
        ${
          node.isOptimal
            ? "ring-4 ring-yellow-400 shadow-xl shadow-yellow-400/50"
            : ""
        }
      `}
      onClick={() =>
        node.level === 1 && setExpandedPath(parseInt(node.id.split("-")[1]) - 1)
      }
    >
      <div className="text-white text-xs font-bold mb-1">
        {node.player === "Us" ? "👤 Our Company" : "🏢 Competitor"}
      </div>
      <div className="text-white font-medium text-sm mb-2">
        {node.move.replace(/_/g, " ")}
      </div>
      {node.score && (
        <div className="flex items-center justify-between">
          <span className="text-yellow-300 text-xs">Expected Score:</span>
          <span className="text-yellow-100 font-bold text-lg">
            {node.score}
          </span>
        </div>
      )}
      {node.isOptimal && (
        <div className="mt-2 bg-yellow-400/20 border border-yellow-400 rounded px-2 py-1">
          <span className="text-yellow-200 text-xs font-bold">
            ⭐ OPTIMAL PATH
          </span>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 shadow-2xl border border-purple-500/30 h-full overflow-auto">
      <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
        <span className="mr-2">🌳</span>
        MaxN Decision Tree
      </h2>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4 animate-pulse">🤖</div>
          <p className="text-purple-300 animate-pulse">
            AI is analyzing possible outcomes...
          </p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">❌</div>
          <p className="text-red-300">{error}</p>
          <button
            onClick={fetchDecisionTree}
            className="mt-4 bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg"
          >
            Retry
          </button>
        </div>
      ) : !treeData ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🎲</div>
          <p className="text-purple-300">
            Select a strategic move to visualize the decision tree
          </p>
        </div>
      ) : (
        <div>
          {/* Info Panel */}
          <div className="bg-purple-500/20 border border-purple-500/50 rounded-lg p-4 mb-6">
            <p className="text-purple-200 text-xs font-medium mb-2">
              🎯 <strong>Business Goal:</strong> {businessGoal}
            </p>
            <p className="text-white text-sm font-semibold mb-2">
              📊 <strong>Selected Strategy:</strong>{" "}
              {treeData.move.replace(/_/g, " ")}
            </p>
            <p className="text-purple-300 text-xs">
              💡 <strong>How it works:</strong> The AI evaluates all possible
              competitor responses and our counter-moves to find the best path.
            </p>
          </div>

          {/* Level 0: Our Initial Move */}
          <div className="mb-8">
            <div className="text-center mb-3">
              <span className="bg-blue-500/30 text-blue-200 px-3 py-1 rounded-full text-xs font-bold">
                LEVEL 0 - Our Initial Move
              </span>
            </div>
            <div className="flex justify-center">
              <div className="w-80">{renderNode(treeData)}</div>
            </div>
            <div className="text-center mt-2">
              <div className="text-purple-300 text-2xl">↓</div>
              <p className="text-purple-400 text-xs">
                Competitor's possible responses
              </p>
            </div>
          </div>

          {/* Level 1: Competitor Responses */}
          <div className="mb-8">
            <div className="text-center mb-3">
              <span className="bg-red-500/30 text-red-200 px-3 py-1 rounded-full text-xs font-bold">
                LEVEL 1 - Competitor's Responses
              </span>
            </div>
            <div className="grid grid-cols-3 gap-4">
              {treeData.children.map((child, idx) => (
                <div
                  key={child.id}
                  className={expandedPath === idx ? "scale-105" : "opacity-70"}
                >
                  {renderNode(child)}
                  {expandedPath === idx && (
                    <div className="text-center mt-2">
                      <div className="text-green-300 text-xl">↓</div>
                      <p className="text-green-400 text-xs">
                        Click to expand our counter-moves
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Level 2: Our Counter-Moves */}
          {treeData.children[expandedPath] && (
            <div className="mb-8">
              <div className="text-center mb-3">
                <span className="bg-blue-500/30 text-blue-200 px-3 py-1 rounded-full text-xs font-bold">
                  LEVEL 2 - Our Counter-Moves to "
                  {treeData.children[expandedPath].move}"
                </span>
              </div>
              <div className="grid grid-cols-3 gap-4">
                {treeData.children[expandedPath].children.map((counterMove) => (
                  <div key={counterMove.id}>{renderNode(counterMove)}</div>
                ))}
              </div>
            </div>
          )}

          {/* Stats and Legend */}
          <div className="grid grid-cols-3 gap-3 mt-6">
            <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-3">
              <p className="text-blue-300 text-xs font-medium">Search Depth</p>
              <p className="text-white text-2xl font-bold">2 Levels</p>
            </div>
            <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-3">
              <p className="text-green-300 text-xs font-medium">
                Nodes Evaluated
              </p>
              <p className="text-white text-2xl font-bold">
                {1 +
                  (treeData.children?.length || 0) +
                  (treeData.children?.reduce(
                    (sum, c) => sum + (c.children?.length || 0),
                    0
                  ) || 0)}{" "}
                Nodes
              </p>
            </div>
            <div className="bg-yellow-500/20 border border-yellow-500/50 rounded-lg p-3">
              <p className="text-yellow-300 text-xs font-medium">Best Score</p>
              <p className="text-white text-2xl font-bold">
                {Math.max(
                  ...(treeData.children?.flatMap(
                    (c) => c.children?.map((cc) => cc.score) || []
                  ) || [0])
                ).toFixed(1)}
              </p>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-6 bg-black/30 rounded-lg p-4">
            <p className="text-white font-bold text-sm mb-3">
              📖 How to Read This Tree:
            </p>
            <div className="space-y-2 text-xs text-purple-200">
              <p>
                • <strong className="text-blue-300">Blue boxes</strong> = Our
                company's moves
              </p>
              <p>
                • <strong className="text-red-300">Red boxes</strong> =
                Competitor's moves
              </p>
              <p>
                • <strong className="text-yellow-300">Yellow ring</strong> =
                Optimal path with highest score
              </p>
              <p>
                • <strong>Scores</strong> = AI-evaluated outcome (0-100, higher
                is better)
              </p>
              <p>
                • <strong>Click</strong> on competitor moves to see our
                counter-strategies
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default DecisionTree;
