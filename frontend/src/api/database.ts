import { apiClient } from './client';
import type {
  DatabaseConnection,
  DatabaseConnectionCreate,
  DatabaseConnectionUpdate,
  DatabaseConnectionListResponse,
  DatabaseConnectionTestRequest,
  DatabaseConnectionTestResponse,
} from '../types/database';

export const databaseApi = {
  getConnections: async (): Promise<DatabaseConnectionListResponse> => {
    const response = await apiClient.get<DatabaseConnectionListResponse>(
      '/api/v1/database-connections'
    );
    return response.data;
  },

  getConnection: async (uuid: string): Promise<DatabaseConnection> => {
    const response = await apiClient.get<DatabaseConnection>(
      `/api/v1/database-connections/${uuid}`
    );
    return response.data;
  },

  createConnection: async (data: DatabaseConnectionCreate): Promise<DatabaseConnection> => {
    const response = await apiClient.post<DatabaseConnection>(
      '/api/v1/database-connections',
      data
    );
    return response.data;
  },

  updateConnection: async (
    uuid: string,
    data: DatabaseConnectionUpdate
  ): Promise<DatabaseConnection> => {
    const response = await apiClient.patch<DatabaseConnection>(
      `/api/v1/database-connections/${uuid}`,
      data
    );
    return response.data;
  },

  deleteConnection: async (uuid: string): Promise<void> => {
    await apiClient.delete(`/api/v1/database-connections/${uuid}`);
  },

  testConnection: async (
    data: DatabaseConnectionTestRequest
  ): Promise<DatabaseConnectionTestResponse> => {
    const response = await apiClient.post<DatabaseConnectionTestResponse>(
      '/api/v1/database-connections/test',
      data
    );
    return response.data;
  },
};