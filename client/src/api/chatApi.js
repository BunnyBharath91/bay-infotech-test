/**
 * Chat API Client
 * Handles all communication with the backend AI Help Desk API
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Send a chat message to the backend
 * @param {string} sessionId - Unique session identifier
 * @param {string} message - User's message
 * @param {string} userRole - User's role (trainee, operator, instructor, support_engineer, admin)
 * @param {object} context - Additional context (module, channel, etc.)
 * @returns {Promise<object>} Chat response with answer, KB references, tier, severity, etc.
 */
export const sendChatMessage = async (sessionId, message, userRole, context = {}) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        sessionId,
        message,
        userRole,
        context,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
};

/**
 * Get all tickets
 * @param {number} limit - Maximum number of tickets to retrieve
 * @param {number} offset - Number of tickets to skip
 * @returns {Promise<object>} List of tickets with pagination info
 */
export const getTickets = async (limit = 50, offset = 0) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/tickets?limit=${limit}&offset=${offset}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching tickets:', error);
    throw error;
  }
};

/**
 * Get a specific ticket by ID
 * @param {string} ticketId - Ticket ID (e.g., INC-0001)
 * @returns {Promise<object>} Ticket details
 */
export const getTicketById = async (ticketId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching ticket:', error);
    throw error;
  }
};

/**
 * Get tickets for a specific session
 * @param {string} sessionId - Session ID
 * @returns {Promise<Array>} List of tickets for the session
 */
export const getTicketsBySession = async (sessionId) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/tickets/session/${sessionId}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching session tickets:', error);
    throw error;
  }
};

/**
 * Get metrics summary
 * @param {number} hours - Number of hours to look back (default: 24)
 * @returns {Promise<object>} Metrics summary including deflection rate, tickets by tier/severity, etc.
 */
export const getMetricsSummary = async (hours = 24) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/metrics/summary?hours=${hours}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics summary:', error);
    throw error;
  }
};

/**
 * Get metrics trends over time
 * @param {number} hours - Number of hours to look back (default: 24)
 * @returns {Promise<object>} Time-series metrics data
 */
export const getMetricsTrends = async (hours = 24) => {
  try {
    const response = await fetch(
      `${API_BASE_URL}/api/metrics/trends?hours=${hours}`,
      {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error fetching metrics trends:', error);
    throw error;
  }
};

/**
 * Health check endpoint
 * @returns {Promise<object>} Health status
 */
export const healthCheck = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error checking health:', error);
    throw error;
  }
};

export default {
  sendChatMessage,
  getTickets,
  getTicketById,
  getTicketsBySession,
  getMetricsSummary,
  getMetricsTrends,
  healthCheck,
};
