import { apiClient } from './client';
import type {
  Query,
  QueryCreate,
  QueryListResponse,
  QueryExecuteRequest,
  QueryExecuteResponse,
  QueryStatus,
} from '../types/query';

export const queryApi = {
  getQueries: async (workspaceUuid: string, skip = 0, limit = 100): Promise<QueryListResponse> => {
    const response = await apiClient.get<QueryListResponse>(
      `/api/v1/workspaces/${workspaceUuid}/queries`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  getQuery: async (queryUuid: string): Promise<Query> => {
    const response = await apiClient.get<Query>(`/api/v1/queries/${queryUuid}`);
    return response.data;
  },

  createQuery: async (workspaceUuid: string, data: QueryCreate): Promise<Query> => {
    const response = await apiClient.post<Query>(
      `/api/v1/workspaces/${workspaceUuid}/queries`,
      data
    );
    return response.data;
  },

  updateQueryStatus: async (queryUuid: string, status: QueryStatus): Promise<Query> => {
    const response = await apiClient.patch<Query>(
      `/api/v1/queries/${queryUuid}/status`,
      { status }
    );
    return response.data;
  },

  executeQuery: async (queryUuid: string, params: QueryExecuteRequest): Promise<QueryExecuteResponse> => {
    const response = await apiClient.post<QueryExecuteResponse>(
      `/api/v1/internal/execute/${queryUuid}`,
      params
    );
    return response.data;
  },
};