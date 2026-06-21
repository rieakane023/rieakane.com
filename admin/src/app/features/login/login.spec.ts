import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { provideRouter } from '@angular/router';
import { Login } from './login';

describe('Login', () => {
  let httpMock: HttpTestingController;

  beforeEach(async () => {
    localStorage.clear();
    await TestBed.configureTestingModule({
      imports: [Login],
      providers: [provideHttpClient(), provideHttpClientTesting(), provideRouter([])],
    }).compileComponents();
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpMock.verify());

  it('does not submit when fields are empty', () => {
    const fixture = TestBed.createComponent(Login);
    fixture.detectChanges();
    fixture.nativeElement.querySelector('form').dispatchEvent(new Event('submit'));
    httpMock.expectNone('/api/v1/admin/auth/login/');
  });

  it('reveals the MFA field when the server requires it', async () => {
    const fixture = TestBed.createComponent(Login);
    const cmp = fixture.componentInstance as unknown as {
      form: { setValue: (v: unknown) => void };
      submit: () => void;
    };
    fixture.detectChanges();
    cmp.form.setValue({ username: 'rie', password: 'pass-w0rd-123', otpToken: '' });
    cmp.submit();

    const req = httpMock.expectOne('/api/v1/admin/auth/login/');
    req.flush({ otp_token: ['An MFA code is required.'] }, { status: 400, statusText: 'Bad Request' });

    await fixture.whenStable();
    fixture.detectChanges();
    expect(fixture.nativeElement.querySelector('#otp')).toBeTruthy();
  });
});
