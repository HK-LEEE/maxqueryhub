export enum DatabaseType {
  MYSQL = 'MYSQL',
  POSTGRESQL = 'POSTGRESQL',
  MSSQL = 'MSSQL',
  ORACLE = 'ORACLE',
  SQLITE = 'SQLITE',
}

export interface DatabaseConnection {
  id: number;
  uuid: string;
  name: string;
  database_type: DatabaseType;
  host: string;
  port: number;
  database_name: string;
  username: string;
  additional_params?: Record<string, any>;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DatabaseConnectionCreate {
  name: string;
  database_type: DatabaseType;
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
  additional_params?: Record<string, any>;
  is_active?: boolean;
}

export interface DatabaseConnectionUpdate {
  name?: string;
  database_type?: DatabaseType;
  host?: string;
  port?: number;
  database_name?: string;
  username?: string;
  password?: string;
  additional_params?: Record<string, any>;
  is_active?: boolean;
}

export interface DatabaseConnectionTestRequest {
  database_type: DatabaseType;
  host: string;
  port: number;
  database_name: string;
  username: string;
  password: string;
  additional_params?: Record<string, any>;
}

export interface DatabaseConnectionTestResponse {
  success: boolean;
  message: string;
  version?: string;
}

export interface DatabaseConnectionListResponse {
  items: DatabaseConnection[];
  total: number;
}