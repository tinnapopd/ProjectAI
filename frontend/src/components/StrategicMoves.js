import React from "react";

function StrategicMoves({
  moves,
  selectedMove,
  setSelectedMove,
  businessGoal,
}) {
  const getCategoryColor = (category) => {
    const colors = {
      Marketing: "from-pink-500 to-rose-500",
      Product: "from-blue-500 to-cyan-500",
      Acquisition: "from-purple-500 to-indigo-500",
      Partnership: "from-green-500 to-emerald-500",
      Technology: "from-orange-500 to-amber-500",
      Distribution: "from-teal-500 to-cyan-500",
      "Customer Retention": "from-violet-500 to-purple-500",
      "Mergers & Acquisitions": "from-fuchsia-500 to-pink-500",
    };

    for (const [key, value] of Object.entries(colors)) {
      if (category?.includes(key)) return value;
    }
    return "from-gray-500 to-slate-500";
  };

  const getCategoryIcon = (category) => {
    if (category?.includes("Marketing")) return "📢";
    if (category?.includes("Product")) return "🚀";
    if (category?.includes("Acquisition") || category?.includes("M&A"))
      return "🤝";
    if (category?.includes("Partnership")) return "🔗";
    if (category?.includes("Technology")) return "⚡";
    if (category?.includes("Distribution")) return "🌐";
    if (category?.includes("Customer") || category?.includes("Retention"))
      return "💎";
    return "💡";
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 shadow-2xl border border-purple-500/30 h-full">
      <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
        <span className="mr-2">🎯</span>
        Strategic Moves
      </h2>

      {moves.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🤖</div>
          <p className="text-purple-300">
            Generate moves to see AI-powered strategic options
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {moves.map((move, index) => (
            <div
              key={move.move_id}
              onClick={() => setSelectedMove(move)}
              className={`
                cursor-pointer p-4 rounded-lg border-2 transition-all transform hover:scale-105
                ${
                  selectedMove?.move_id === move.move_id
                    ? "border-yellow-400 bg-yellow-500/20 shadow-lg shadow-yellow-500/50"
                    : "border-purple-500/30 bg-white/5 hover:border-purple-400/50"
                }
              `}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">
                    {getCategoryIcon(move.stratgic_category)}
                  </span>
                  <span className="text-white font-bold text-sm">
                    Move {index + 1}
                  </span>
                </div>
                <span
                  className={`
                  text-xs px-2 py-1 rounded-full bg-gradient-to-r ${getCategoryColor(
                    move.stratgic_category
                  )} text-white font-medium
                `}
                >
                  {move.stratgic_category}
                </span>
              </div>

              <h3 className="text-white font-semibold text-sm mb-2">
                {move.move_name.replace(/_/g, " ")}
              </h3>

              <p className="text-purple-200 text-xs leading-relaxed mb-2">
                {move.description}
              </p>

              {move.expected_score !== undefined &&
                move.expected_score !== null && (
                  <div className="flex items-center justify-between mt-2 pt-2 border-t border-purple-500/30">
                    <div className="flex items-center space-x-2">
                      <span className="text-yellow-400 text-lg">⭐</span>
                      <span className="text-yellow-300 text-xs font-medium">
                        Expected Score:
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <div className="bg-yellow-500/20 px-3 py-1 rounded-full">
                        <span className="text-yellow-100 font-bold text-lg">
                          {move.expected_score.toFixed(1)}
                        </span>
                        <span className="text-yellow-300 text-xs ml-1">
                          /100
                        </span>
                      </div>
                    </div>
                  </div>
                )}

              {move.score_explanation && (
                <div className="mt-2 bg-blue-500/10 border border-blue-500/30 rounded p-2">
                  <p className="text-blue-200 text-xs italic">
                    💡 {move.score_explanation}
                  </p>
                </div>
              )}

              {selectedMove?.move_id === move.move_id && (
                <div className="mt-3 pt-3 border-t border-yellow-400/30">
                  <p className="text-yellow-300 text-xs font-medium">
                    ✨ Selected - View decision tree on the right →
                  </p>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default StrategicMoves;
