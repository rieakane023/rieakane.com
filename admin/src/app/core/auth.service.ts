import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { CurrentAdmin, LoginResponse } from './models';
import { environment } from '../../environments/environment';

const TOKEN_KEY = 'rieakane-admin:token';

/**
 * Admin auth. The token is the ONLY credential the SPA holds; all real authz is
 * enforced server-side (security-angular.md §7 — guards are UX only). Token lives
 * in localStorage for this internal tool; the network is restricted per
 * security.md §3.1 and MFA is enforced at login.
 */
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly base = `${environment.apiBaseUrl}/api/v1/admin`;

  readonly token = signal<string | null>(this.read());
  readonly user = signal<CurrentAdmin | null>(null);
  readonly isAuthenticated = computed(() => this.token() !== null);

  login(username: string, password: string, otpToken?: string): Observable<LoginResponse> {
    return this.http
      .post<LoginResponse>(`${this.base}/auth/login/`, {
        username,
        password,
        otp_token: otpToken ?? '',
      })
      .pipe(
        tap((res) => {
          this.token.set(res.token);
          this.user.set(res.user);
          this.write(res.token);
        }),
      );
  }

  /** Load the current admin profile (e.g. after a refresh while holding a token). */
  loadMe(): Observable<CurrentAdmin> {
    return this.http
      .get<CurrentAdmin>(`${this.base}/auth/me/`)
      .pipe(tap((u) => this.user.set(u)));
  }

  logout(): void {
    // Best-effort server-side invalidation; clear locally regardless.
    this.http.post(`${this.base}/auth/logout/`, {}).subscribe({
      next: () => this.clear(),
      error: () => this.clear(),
    });
  }

  clear(): void {
    this.token.set(null);
    this.user.set(null);
    try {
      localStorage.removeItem(TOKEN_KEY);
    } catch {
      /* ignore */
    }
  }

  private read(): string | null {
    try {
      return localStorage.getItem(TOKEN_KEY);
    } catch {
      return null;
    }
  }

  private write(token: string): void {
    try {
      localStorage.setItem(TOKEN_KEY, token);
    } catch {
      /* ignore */
    }
  }
}
