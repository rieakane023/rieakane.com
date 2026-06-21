import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { catchError, throwError } from 'rxjs';
import { AuthService } from './auth.service';

/**
 * Attach the admin token to same-origin API calls only (never leak it
 * cross-origin — security-angular.md §6). On 401, drop the session and bounce
 * to login.
 */
export const authInterceptor: HttpInterceptorFn = (req, next) => {
  const auth = inject(AuthService);
  const router = inject(Router);
  const token = auth.token();

  const isApi = req.url.startsWith('/api/');
  const authed = token && isApi ? req.clone({ setHeaders: { Authorization: `Token ${token}` } }) : req;

  return next(authed).pipe(
    catchError((err: HttpErrorResponse) => {
      if (err.status === 401) {
        auth.clear();
        router.navigate(['/login']);
      }
      return throwError(() => err);
    }),
  );
};
