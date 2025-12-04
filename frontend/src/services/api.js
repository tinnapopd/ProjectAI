// API service for wargame operations

import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_BASE = `${API_URL}/api/v1`;

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 120000, // 2 minutes timeout for AI operations
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log("API Request:", config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error("Request Error:", error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log("API Response:", response.status, response.config.url);
    return response;
  },
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error(
        "Response Error:",
        error.response.status,
        error.response.data
      );
    } else if (error.request) {
      // Request made but no response
      console.error("Network Error: No response received");
    } else {
      // Error in request setup
      console.error("Request Setup Error:", error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Run a wargame simulation
 * @param {Object} requestData - Wargame configuration
 * @returns {Promise<Object>} Simulation results
 */
export const runWargame = async (requestData) => {
  try {
    const response = await api.post("/wargame/run", requestData);
    return response.data;
  } catch (error) {
    throw error;
  }
};

/**
 * Validate request data before sending
 * @param {Object} data - Request data to validate
 * @returns {Object} Validation result
 */
export const validateRequest = (data) => {
  const errors = [];

  if (!data.business_goal || data.business_goal.trim().length === 0) {
    errors.push("Business goal is required");
  }

  if (!data.player_profiles || data.player_profiles.length === 0) {
    errors.push("At least one player profile is required");
  } else {
    data.player_profiles.forEach((player, index) => {
      if (!player.name || player.name.trim().length === 0) {
        errors.push(`Player ${index + 1}: Name is required`);
      }
      if (!player.business_goal || player.business_goal.trim().length === 0) {
        errors.push(`Player ${index + 1}: Business goal is required`);
      }
    });
  }

  if (!data.game_state || !data.game_state.metrics) {
    errors.push("Game state with metrics is required");
  }

  if (!data.game_state?.time_periods || data.game_state.time_periods < 1) {
    errors.push("Time periods must be at least 1");
  }

  return {
    valid: errors.length === 0,
    errors,
  };
};

export default api;
