import { useState } from "react";
import "./WargameForm.css";

const WargameForm = ({ onSubmit, loading }) => {
  const [businessGoal, setBusinessGoal] = useState("");
  const [timePeriods, setTimePeriods] = useState(4);
  const [timePeriodUnit, setTimePeriodUnit] = useState("quarter");
  const [companyName, setCompanyName] = useState("Your Company");
  const [aboutUs, setAboutUs] = useState("");
  const [customers, setCustomers] = useState("");
  const [metrics, setMetrics] = useState("");
  const [actionSet, setActionSet] = useState("");

  const parseMetrics = (metricsStr) => {
    if (!metricsStr.trim()) return {};
    try {
      // Try parsing as JSON first
      return JSON.parse(metricsStr);
    } catch {
      // Parse as key:value pairs (one per line or comma-separated)
      const result = {};
      const pairs = metricsStr.split(/[,\n]/).filter((p) => p.trim());
      pairs.forEach((pair) => {
        const [key, value] = pair.split(":").map((s) => s.trim());
        if (key && value) {
          // Try to convert to number if possible
          const numValue = parseFloat(value);
          result[key] = isNaN(numValue) ? value : numValue;
        }
      });
      return result;
    }
  };

  const parseActionSet = (actionStr) => {
    if (!actionStr.trim()) return [];
    // Split by newlines or semicolons
    return actionStr
      .split(/[;\n]/)
      .map((a) => a.trim())
      .filter((a) => a);
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    // Prepare user company profile
    const userCompany = {
      id: "1",
      name: companyName,
      business_goal: businessGoal,
      about_us: aboutUs,
      customers: customers
        ? customers
            .split(",")
            .map((c) => c.trim())
            .filter((c) => c)
        : [],
      isUserCompany: true,
    };

    const requestData = {
      business_goal: businessGoal,
      player_profiles: [userCompany],
      game_state: {
        metrics: parseMetrics(metrics),
        history: [],
        time_periods: timePeriods,
        time_period_unit: timePeriodUnit,
      },
      action_set: parseActionSet(actionSet),
    };

    onSubmit(requestData);
  };

  return (
    <form className="wargame-form" onSubmit={handleSubmit}>
      <div className="form-section">
        <h3>⚙️ General Settings</h3>
        <div className="form-group">
          <label>Business Goal *</label>
          <textarea
            value={businessGoal}
            onChange={(e) => setBusinessGoal(e.target.value)}
            placeholder="Describe your strategic business objective..."
            required
            rows={3}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>Time Periods *</label>
            <input
              type="number"
              value={timePeriods}
              onChange={(e) => setTimePeriods(parseInt(e.target.value))}
              min="1"
              max="12"
              required
            />
          </div>
          <div className="form-group">
            <label>Time Unit *</label>
            <select
              value={timePeriodUnit}
              onChange={(e) => setTimePeriodUnit(e.target.value)}
              required
            >
              <option value="quarter">Quarter</option>
              <option value="month">Month</option>
              <option value="year">Year</option>
              <option value="week">Week</option>
            </select>
          </div>
        </div>
      </div>

      <div className="form-section">
        <h3>🏢 Your Company Profile</h3>

        <div className="form-group">
          <label>Company Name *</label>
          <input
            type="text"
            value={companyName}
            onChange={(e) => setCompanyName(e.target.value)}
            placeholder="Enter your company name"
            required
          />
        </div>

        <div className="form-group">
          <label>About Your Company</label>
          <textarea
            value={aboutUs}
            onChange={(e) => setAboutUs(e.target.value)}
            placeholder="Brief description of your company..."
            rows={2}
          />
        </div>

        <div className="form-group">
          <label>Target Customers (comma-separated)</label>
          <input
            type="text"
            value={customers}
            onChange={(e) => setCustomers(e.target.value)}
            placeholder="e.g., Enterprise, SMB, Consumer"
          />
        </div>
      </div>

      <div className="form-section">
        <h3>📊 Initial Metrics</h3>
        <div className="form-group">
          <label>Current Business Metrics</label>
          <textarea
            value={metrics}
            onChange={(e) => setMetrics(e.target.value)}
            placeholder={`Enter metrics as key:value pairs (one per line) or JSON:
market_share: 40
monthly_active_users: 1000000
revenue: 5000000
engagement_rate: 0.35`}
            rows={5}
          />
          <small className="form-hint">
            Format: key: value (one per line) or valid JSON object
          </small>
        </div>
      </div>

      <div className="form-section">
        <h3>🎯 Strategic Actions</h3>
        <div className="form-group">
          <label>Action Set (optional - AI will generate if empty)</label>
          <textarea
            value={actionSet}
            onChange={(e) => setActionSet(e.target.value)}
            placeholder={`Enter strategic actions (one per line):
Launch marketing campaign
Expand product line
Optimize pricing strategy
Form strategic partnerships`}
            rows={5}
          />
          <small className="form-hint">
            Leave empty to let AI generate strategic moves automatically
          </small>
        </div>
      </div>

      <button type="submit" className="btn-submit" disabled={loading}>
        {loading ? "⏳ Running Simulation..." : "🚀 Run Wargame Simulation"}
      </button>
    </form>
  );
};

export default WargameForm;
