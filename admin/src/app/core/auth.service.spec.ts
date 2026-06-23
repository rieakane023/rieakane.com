import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

const LOGIN_URL = `${environment.apiBaseUrl}/api/v1/admin/auth/login/`;

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({
      providers: [AuthService, provideHttpClient(), provideHttpClientTesting()],
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('starts unauthenticated', () => {
    expect(service.isAuthenticated()).toBe(false);
  });

  it('stores token + user on successful login', () => {
    service.login('rie', 'pass-w0rd-123').subscribe();

    const req = httpMock.expectOne(LOGIN_URL);
    expect(req.request.method).toBe('POST');
    expect(req.request.body.otp_token).toBe('');
    req.flush({
      token: 'abc123',
      user: { id: 1, username: 'rie', email: '', first_name: '', last_name: '', role: 'admin', is_superadmin: false },
    });

    expect(service.token()).toBe('abc123');
    expect(service.user()?.username).toBe('rie');
    expect(service.isAuthenticated()).toBe(true);
    expect(localStorage.getItem('rieakane-admin:token')).toBe('abc123');
  });

  it('clears state on logout', () => {
    service.token.set('abc');
    service.clear();
    expect(service.token()).toBeNull();
    expect(service.isAuthenticated()).toBe(false);
  });
});
