import React, { useState } from "react";
import axios from "axios";

const API_BASE_URL = "http://localhost:8000/api/v1";

function GameSetup({
  sessionId,
  setSessionId,
  businessGoal,
  setBusinessGoal,
  setMoves,
  setGameState,
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Our Company Data
  const [companyName, setCompanyName] = useState("TechNova Solutions");
  const [companyType, setCompanyType] = useState("Cloud Software & SaaS");
  const [companySize, setCompanySize] = useState(250);
  const [companyProducts, setCompanyProducts] = useState(
    "Enterprise Cloud Platform, AI Analytics Suite, Mobile App"
  );
  const [companyCustomers, setCompanyCustomers] = useState(
    "Mid-size Enterprises, Tech Startups, Fortune 500"
  );
  const [companyMarketShare, setCompanyMarketShare] = useState(15);
  const [companyRevenue, setCompanyRevenue] = useState(7500000);
  const [companyResources, setCompanyResources] = useState(3000000);

  // Competitor Data
  const [competitorName, setCompetitorName] = useState("UltraEgo");
  const [competitorType, setCompetitorType] = useState("Cloud Software & SaaS");
  const [competitorSize, setCompetitorSize] = useState(500);
  const [competitorProducts, setCompetitorProducts] = useState(
    "Cloud Infrastructure, BI Platform, Collaboration Tools"
  );
  const [competitorCustomers, setCompetitorCustomers] = useState(
    "Large Enterprises, Government, Financial Institutions"
  );
  const [competitorMarketShare, setCompetitorMarketShare] = useState(25);
  const [competitorRevenue, setCompetitorRevenue] = useState(12500000);
  const [competitorResources, setCompetitorResources] = useState(8000000);

  // Market Data
  const [marketSize, setMarketSize] = useState(50000000);
  const [marketGrowth, setMarketGrowth] = useState(8);
  const [competitiveIntensity, setCompetitiveIntensity] = useState("very high");

  const handleStartGame = async () => {
    if (!businessGoal.trim()) {
      setError("Please enter a business goal");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(`${API_BASE_URL}/agent/start_game`, {
        business_goal: businessGoal,
        our_company: {
          name: companyName,
          business_type: companyType,
          company_size: parseInt(companySize),
          products: companyProducts.split(",").map((p) => p.trim()),
          target_customers: companyCustomers.split(",").map((c) => c.trim()),
        },
        competitors: [
          {
            name: competitorName,
            business_type: competitorType,
            company_size: parseInt(competitorSize),
            products: competitorProducts.split(",").map((p) => p.trim()),
            target_customers: competitorCustomers
              .split(",")
              .map((c) => c.trim()),
          },
        ],
        initial_game_state: {
          period: 1,
          market_size: parseFloat(marketSize),
          players: [
            {
              player_id: "OurCompany",
              market_share: parseFloat(companyMarketShare) / 100,
              revenue: parseFloat(companyRevenue),
              brand_sentiment: 0.7,
              resources: parseFloat(companyResources),
              additional_metrics: {
                customer_satisfaction: 0.75,
                product_quality: 0.8,
              },
            },
            {
              player_id: competitorName,
              market_share: parseFloat(competitorMarketShare) / 100,
              revenue: parseFloat(competitorRevenue),
              brand_sentiment: 0.85,
              resources: parseFloat(competitorResources),
              additional_metrics: {
                customer_satisfaction: 0.82,
                product_quality: 0.88,
              },
            },
          ],
          market_conditions: {
            growth_rate: parseFloat(marketGrowth) / 100,
            competitive_intensity: competitiveIntensity,
          },
        },
      });

      setSessionId(response.data.session_id);
      setGameState(response.data.initial_state);
    } catch (err) {
      console.error("Game start error:", err);
      const errorMsg =
        err.response?.data?.detail || err.message || "Failed to start game";
      setError(
        typeof errorMsg === "string" ? errorMsg : JSON.stringify(errorMsg)
      );
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateMoves = async () => {
    if (!sessionId) {
      setError("Please start a game first");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const response = await axios.post(
        `${API_BASE_URL}/agent/get_strategic_moves`,
        {
          period: 1,
          market_size: 50000000,
          players: [
            {
              player_id: "OurCompany",
              market_share: 0.15,
              revenue: 7500000,
              brand_sentiment: 0.7,
              resources: 3000000,
            },
            {
              player_id: competitorName,
              market_share: 0.25,
              revenue: 12500000,
              brand_sentiment: 0.85,
              resources: 8000000,
            },
          ],
          market_conditions: {
            growth_rate: 0.08,
            competitive_intensity: "very high",
          },
        },
        {
          params: { session_id: sessionId },
        }
      );

      setMoves(response.data.moves);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate moves");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white/10 backdrop-blur-lg rounded-xl p-6 shadow-2xl border border-purple-500/30">
      <h2 className="text-2xl font-bold text-white mb-4 flex items-center">
        <span className="mr-2">⚙️</span>
        Game Setup
      </h2>

      {!sessionId ? (
        <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
          {/* Business Goal */}
          <div className="bg-purple-500/20 border border-purple-500/50 rounded-lg p-4">
            <h3 className="text-white font-bold mb-3 flex items-center">
              🎯 Business Goal
            </h3>
            <textarea
              value={businessGoal}
              onChange={(e) => setBusinessGoal(e.target.value)}
              className="w-full px-4 py-2 bg-white/5 border border-purple-500/30 rounded-lg text-white placeholder-purple-300/50 focus:outline-none focus:border-purple-400 h-20 resize-none"
              placeholder="e.g., Achieve 10% revenue growth, Increase market share by 15%, Launch new product line"
            />
          </div>

          {/* Our Company */}
          <div className="bg-blue-500/20 border border-blue-500/50 rounded-lg p-4">
            <h3 className="text-white font-bold mb-3 flex items-center">
              👤 Your Company Profile
            </h3>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={companyName}
                    onChange={(e) => setCompanyName(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Business Type
                  </label>
                  <input
                    type="text"
                    value={companyType}
                    onChange={(e) => setCompanyType(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-blue-200 mb-1 text-xs font-medium">
                  Products/Services (comma-separated)
                </label>
                <input
                  type="text"
                  value={companyProducts}
                  onChange={(e) => setCompanyProducts(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  placeholder="Product 1, Product 2, Product 3"
                />
              </div>

              <div>
                <label className="block text-blue-200 mb-1 text-xs font-medium">
                  Target Customers (comma-separated)
                </label>
                <input
                  type="text"
                  value={companyCustomers}
                  onChange={(e) => setCompanyCustomers(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  placeholder="Customer Segment 1, Segment 2"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Company Size (employees)
                  </label>
                  <input
                    type="number"
                    value={companySize}
                    onChange={(e) => setCompanySize(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Market Share (%)
                  </label>
                  <input
                    type="number"
                    value={companyMarketShare}
                    onChange={(e) => setCompanyMarketShare(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Annual Revenue ($)
                  </label>
                  <input
                    type="number"
                    value={companyRevenue}
                    onChange={(e) => setCompanyRevenue(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
                <div>
                  <label className="block text-blue-200 mb-1 text-xs font-medium">
                    Resources/Budget ($)
                  </label>
                  <input
                    type="number"
                    value={companyResources}
                    onChange={(e) => setCompanyResources(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-blue-500/30 rounded text-white text-sm focus:outline-none focus:border-blue-400"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Competitor */}
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-4">
            <h3 className="text-white font-bold mb-3 flex items-center">
              🏢 Competitor Profile
            </h3>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Competitor Name
                  </label>
                  <input
                    type="text"
                    value={competitorName}
                    onChange={(e) => setCompetitorName(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Business Type
                  </label>
                  <input
                    type="text"
                    value={competitorType}
                    onChange={(e) => setCompetitorType(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-red-200 mb-1 text-xs font-medium">
                  Products/Services (comma-separated)
                </label>
                <input
                  type="text"
                  value={competitorProducts}
                  onChange={(e) => setCompetitorProducts(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                />
              </div>

              <div>
                <label className="block text-red-200 mb-1 text-xs font-medium">
                  Target Customers (comma-separated)
                </label>
                <input
                  type="text"
                  value={competitorCustomers}
                  onChange={(e) => setCompetitorCustomers(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Company Size (employees)
                  </label>
                  <input
                    type="number"
                    value={competitorSize}
                    onChange={(e) => setCompetitorSize(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Market Share (%)
                  </label>
                  <input
                    type="number"
                    value={competitorMarketShare}
                    onChange={(e) => setCompetitorMarketShare(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Annual Revenue ($)
                  </label>
                  <input
                    type="number"
                    value={competitorRevenue}
                    onChange={(e) => setCompetitorRevenue(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
                <div>
                  <label className="block text-red-200 mb-1 text-xs font-medium">
                    Resources/Budget ($)
                  </label>
                  <input
                    type="number"
                    value={competitorResources}
                    onChange={(e) => setCompetitorResources(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-red-500/30 rounded text-white text-sm focus:outline-none focus:border-red-400"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Market Conditions */}
          <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
            <h3 className="text-white font-bold mb-3 flex items-center">
              📊 Market Conditions
            </h3>
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-green-200 mb-1 text-xs font-medium">
                    Market Size ($)
                  </label>
                  <input
                    type="number"
                    value={marketSize}
                    onChange={(e) => setMarketSize(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-green-500/30 rounded text-white text-sm focus:outline-none focus:border-green-400"
                  />
                </div>
                <div>
                  <label className="block text-green-200 mb-1 text-xs font-medium">
                    Market Growth Rate (%)
                  </label>
                  <input
                    type="number"
                    value={marketGrowth}
                    onChange={(e) => setMarketGrowth(e.target.value)}
                    className="w-full px-3 py-2 bg-white/5 border border-green-500/30 rounded text-white text-sm focus:outline-none focus:border-green-400"
                  />
                </div>
              </div>

              <div>
                <label className="block text-green-200 mb-1 text-xs font-medium">
                  Competitive Intensity
                </label>
                <select
                  value={competitiveIntensity}
                  onChange={(e) => setCompetitiveIntensity(e.target.value)}
                  className="w-full px-3 py-2 bg-white/5 border border-green-500/30 rounded text-white text-sm focus:outline-none focus:border-green-400"
                >
                  <option value="low">Low</option>
                  <option value="moderate">Moderate</option>
                  <option value="high">High</option>
                  <option value="very high">Very High</option>
                </select>
              </div>
            </div>
          </div>

          <button
            onClick={handleStartGame}
            disabled={loading}
            className="w-full bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg"
          >
            {loading ? "🔄 Starting Game..." : "🚀 Start Strategic Analysis"}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-green-500/20 border border-green-500/50 rounded-lg p-4">
            <p className="text-green-300 text-sm font-medium">
              ✅ Game Started
            </p>
            <p className="text-white text-xs mt-1">Session: {sessionId}</p>
            <p className="text-purple-200 text-sm mt-2">{businessGoal}</p>
          </div>

          <button
            onClick={handleGenerateMoves}
            disabled={loading}
            className="w-full bg-gradient-to-r from-green-600 to-teal-600 hover:from-green-700 hover:to-teal-700 text-white font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "🤖 AI Thinking..." : "🎯 Generate Strategic Moves"}
          </button>

          <button
            onClick={() => {
              setSessionId(null);
              setMoves([]);
              setBusinessGoal("");
            }}
            className="w-full bg-red-600/80 hover:bg-red-700 text-white font-bold py-2 px-6 rounded-lg transition-all"
          >
            🔄 Reset Game
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 bg-red-500/20 border border-red-500/50 rounded-lg p-3">
          <p className="text-red-300 text-sm">❌ {error}</p>
        </div>
      )}
    </div>
  );
}

export default GameSetup;
