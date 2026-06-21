import { inject } from '@angular/core';
import { CanMatchFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

/**
 * UX-only gate (security-angular.md §7): keeps unauthenticated users off admin
 * routes. Real enforcement is server-side on every admin endpoint.
 */
export const authGuard: CanMatchFn = () => {
  const auth = inject(AuthService);
  const router = inject(Router);
  return auth.isAuthenticated() ? true : router.createUrlTree(['/login']);
};
