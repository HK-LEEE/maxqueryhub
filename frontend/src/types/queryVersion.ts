export interface QueryVersion {
  id: number;
  uuid: string;
  query_id: number;
  version_number: number;
  name: string;
  description?: string;
  sql_template: string;
  params_info?: Record<string, any>;
  created_by: string;
  created_at: string;
  is_active: boolean;
}

export interface QueryVersionCreate {
  name: string;
  description?: string;
  sql_template: string;
  params_info?: Record<string, any>;
}

export interface QueryVersionResponse extends QueryVersion {}

export interface QueryVersionListResponse {
  items: QueryVersionResponse[];
  total: number;
}