import { apiClient } from './client';
import type { 
  QueryVersionCreate, 
  QueryVersionResponse, 
  QueryVersionListResponse 
} from '../types/queryVersion';

export const queryVersionApi = {
  getVersions: async (queryId: string): Promise<QueryVersionListResponse> => {
    const response = await apiClient.get<QueryVersionListResponse>(
      `/api/v1/queries/${queryId}/versions`
    );
    return response.data;
  },

  createVersion: async (
    queryId: string,
    data: QueryVersionCreate
  ): Promise<QueryVersionResponse> => {
    const response = await apiClient.post<QueryVersionResponse>(
      `/api/v1/queries/${queryId}/versions`,
      data
    );
    return response.data;
  },

  getVersion: async (
    queryId: string,
    versionId: string
  ): Promise<QueryVersionResponse> => {
    const response = await apiClient.get<QueryVersionResponse>(
      `/api/v1/queries/${queryId}/versions/${versionId}`
    );
    return response.data;
  },

  activateVersion: async (
    queryId: string,
    versionId: string
  ): Promise<QueryVersionResponse> => {
    const response = await apiClient.put<QueryVersionResponse>(
      `/api/v1/queries/${queryId}/versions/${versionId}/activate`
    );
    return response.data;
  },
};