export type PrincipalType = 'USER' | 'GROUP';

export interface Permission {
  id: number;
  uuid: string;
  workspace_id: number;
  principal_type: PrincipalType;
  principal_id: string;
}

export interface PermissionCreate {
  principal_type: PrincipalType;
  principal_id: string;
}