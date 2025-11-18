/**
 * API client for communicating with the analytics backend.
 */
import axios from 'axios';
import { ChatRequest, ChatResponse, HealthResponse, AgentListResponse } from '@/types';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const api = {
  /**
   * Send a chat message and get response.
   */
  async sendMessage(request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>('/chat', request);
    return response.data;
  },

  /**
   * Check backend health status.
   */
  async healthCheck(): Promise<HealthResponse> {
    const response = await apiClient.get<HealthResponse>('/health');
    return response.data;
  },

  /**
   * Delete a session.
   */
  async deleteSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/session/${sessionId}`);
  },

  /**
   * Get list of registered agents.
   */
  async getAgents(): Promise<AgentListResponse> {
    const response = await apiClient.get<AgentListResponse>('/agents');
    return response.data;
  },
};
