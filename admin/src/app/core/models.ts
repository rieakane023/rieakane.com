export type Role = 'superadmin' | 'admin' | 'editor' | 'support' | 'readonly';

export interface CurrentAdmin {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_superadmin: boolean;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  is_active: boolean;
  is_staff: boolean;
  date_joined: string;
  last_login: string | null;
}

export interface ErrorLog {
  id: number;
  timestamp: string;
  level: 'error' | 'warning' | 'critical';
  exception_type: string;
  message: string;
  traceback: string;
  path: string;
  method: string;
  status_code: number | null;
  user: string | null;
  request_id: string;
  resolved: boolean;
}

export interface FieldChange {
  old: unknown;
  new: unknown;
}

export interface AuditLog {
  id: number;
  timestamp: string;
  action: 'create' | 'update' | 'delete';
  model: string;
  object_id: string;
  object_repr: string;
  changes: Record<string, FieldChange>;
  changed_by: string | null;
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface LoginResponse {
  token: string;
  user: CurrentAdmin;
}
