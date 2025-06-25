import { apiClient } from './client';
import type { Workspace, WorkspaceCreate, WorkspaceListResponse } from '../types/workspace';

export const workspaceApi = {
  getWorkspaces: async (skip = 0, limit = 100): Promise<WorkspaceListResponse> => {
    const response = await apiClient.get<WorkspaceListResponse>('/api/v1/workspaces', {
      params: { skip, limit },
    });
    return response.data;
  },

  getWorkspace: async (uuid: string): Promise<Workspace> => {
    const response = await apiClient.get<Workspace>(`/api/v1/workspaces/${uuid}`);
    return response.data;
  },

  createWorkspace: async (data: WorkspaceCreate): Promise<Workspace> => {
    const response = await apiClient.post<Workspace>('/api/v1/workspaces', data);
    return response.data;
  },
};