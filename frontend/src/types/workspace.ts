export enum WorkspaceType {
  PERSONAL = 'PERSONAL',
  GROUP = 'GROUP',
}

export interface Workspace {
  id: number;
  uuid: string;
  name: string;
  type: WorkspaceType;
  owner_id: string;
  auto_close_days: number | null;
  database_connection_id?: number | null;
  database_connection_name?: string | null;
  created_at: string;
  query_count: number;
}

export interface WorkspaceCreate {
  name: string;
  type: WorkspaceType;
  auto_close_days?: number | null;
  database_connection_id?: number | null;
}

export interface WorkspaceListResponse {
  items: Workspace[];
  total: number;
}