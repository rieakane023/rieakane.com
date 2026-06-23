import { Injectable, inject } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AdminUser, AuditLog, ErrorLog, Paginated } from './models';
import { environment } from '../../environments/environment';

export interface ListQuery {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  [key: string]: string | number | boolean | undefined;
}

/** Typed access to the admin-only API. Components never call HttpClient directly. */
@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/api/v1/admin`;

  private params(query: ListQuery = {}): HttpParams {
    let p = new HttpParams();
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== '' && value !== null) {
        p = p.set(key, String(value));
      }
    }
    return p;
  }

  // Tab 1 — Users
  listUsers(query?: ListQuery): Observable<Paginated<AdminUser>> {
    return this.http.get<Paginated<AdminUser>>(`${this.base}/users/`, { params: this.params(query) });
  }
  createUser(body: Partial<AdminUser> & { password?: string }): Observable<AdminUser> {
    return this.http.post<AdminUser>(`${this.base}/users/`, body);
  }
  updateUser(id: number, body: Partial<AdminUser>): Observable<AdminUser> {
    return this.http.patch<AdminUser>(`${this.base}/users/${id}/`, body);
  }
  deactivateUser(id: number): Observable<unknown> {
    return this.http.post(`${this.base}/users/${id}/deactivate/`, {});
  }

  // Tab 2 — Error logs
  listErrors(query?: ListQuery): Observable<Paginated<ErrorLog>> {
    return this.http.get<Paginated<ErrorLog>>(`${this.base}/error-logs/`, { params: this.params(query) });
  }
  setErrorResolved(id: number, resolved: boolean): Observable<ErrorLog> {
    return this.http.patch<ErrorLog>(`${this.base}/error-logs/${id}/`, { resolved });
  }

  // Tab 3 — Audit trail
  listAudit(query?: ListQuery): Observable<Paginated<AuditLog>> {
    return this.http.get<Paginated<AuditLog>>(`${this.base}/audit-logs/`, { params: this.params(query) });
  }
  auditModels(): Observable<string[]> {
    return this.http.get<string[]>(`${this.base}/audit-logs/models/`);
  }
}
