import { Component, inject, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ReactiveFormsModule, FormBuilder, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AuthService } from '../../core/auth.service';

@Component({
  selector: 'adm-login',
  imports: [ReactiveFormsModule],
  templateUrl: './login.html',
  styleUrl: './login.scss',
})
export class Login {
  private readonly fb = inject(FormBuilder);
  private readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  protected readonly submitting = signal(false);
  protected readonly error = signal<string | null>(null);
  protected readonly mfaNeeded = signal(false);

  protected readonly form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    password: ['', Validators.required],
    otpToken: [''],
  });

  protected submit(): void {
    if (this.form.invalid || this.submitting()) {
      this.form.markAllAsTouched();
      return;
    }
    this.submitting.set(true);
    this.error.set(null);
    const { username, password, otpToken } = this.form.getRawValue();

    this.auth.login(username, password, otpToken).subscribe({
      next: () => this.router.navigate(['/dashboard']),
      error: (err: HttpErrorResponse) => {
        this.submitting.set(false);
        const detail = this.firstError(err);
        // The server signals MFA via these codes / messages.
        if (/mfa/i.test(detail)) this.mfaNeeded.set(true);
        this.error.set(detail);
      },
    });
  }

  private firstError(err: HttpErrorResponse): string {
    const data = err.error;
    if (data && typeof data === 'object') {
      const values = Object.values(data).flat();
      if (values.length) return String(values[0]);
    }
    return 'Sign-in failed. Check your credentials and try again.';
  }
}
