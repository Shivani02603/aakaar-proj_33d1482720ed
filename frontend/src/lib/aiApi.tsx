import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || '';

export interface Session {
  id: string;
  name: string;
  created_at: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface AIQueryResponse {
  answer: string;
  sources: string[];
}

const getAuthHeaders = () => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Authorization token not found');
  }
  return { Authorization: `Bearer ${token}` };
};

export const ingestFile = async (file: File, sessionId: string): Promise<{ chunks_indexed: number }> => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('session_id', sessionId);

  try {
    const response = await axios.post(`${API_BASE_URL}/api/ai/ingest`, formData, {
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to ingest file');
  }
};

export const queryAI = async (query: string, sessionId: string): Promise<AIQueryResponse> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/ai/query`,
      { query, session_id: sessionId },
      {
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to query AI');
  }
};

export const streamAnswer = (query: string, sessionId: string): EventSource => {
  const token = localStorage.getItem('token');
  if (!token) {
    throw new Error('Authorization token not found');
  }

  const url = `${API_BASE_URL}/api/ai/stream?query=${encodeURIComponent(query)}&session_id=${encodeURIComponent(sessionId)}`;
  const eventSource = new EventSource(url, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  return eventSource;
};

export const getSessions = async (): Promise<Session[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sessions`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to fetch sessions');
  }
};

export const createSession = async (name?: string): Promise<Session> => {
  try {
    const response = await axios.post(
      `${API_BASE_URL}/api/sessions`,
      { name },
      {
        headers: {
          ...getAuthHeaders(),
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to create session');
  }
};

export const getMessages = async (sessionId: string): Promise<Message[]> => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/sessions/${sessionId}/messages`, {
      headers: getAuthHeaders(),
    });
    return response.data;
  } catch (error: any) {
    throw new Error(error.response?.data?.message || 'Failed to fetch messages');
  }
};