import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { HttpErrorResponse } from '@angular/common/http';
import { ApiService } from '../../core/api.service';
import { AuthService } from '../../core/auth.service';
import { AdminUser, Role } from '../../core/models';

const PAGE_SIZE = 25;
const ROLES: Role[] = ['superadmin', 'admin', 'editor', 'support', 'readonly'];

@Component({
  selector: 'adm-users',
  imports: [ReactiveFormsModule, DatePipe],
  templateUrl: './users.html',
  styleUrl: './users.scss',
})
export class Users {
  private readonly api = inject(ApiService);
  private readonly fb = inject(FormBuilder);
  protected readonly auth = inject(AuthService);

  protected readonly roles = ROLES;
  protected readonly rows = signal<AdminUser[]>([]);
  protected readonly count = signal(0);
  protected readonly page = signal(1);
  protected readonly search = signal('');
  protected readonly loading = signal(true);
  protected readonly error = signal(false);

  protected readonly showCreate = signal(false);
  protected readonly createError = signal<string | null>(null);
  protected readonly canManage = computed(() => this.auth.user()?.is_superadmin ?? false);

  protected readonly pageSize = PAGE_SIZE;
  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.count() / PAGE_SIZE)));
  protected readonly rangeStart = computed(() => (this.count() === 0 ? 0 : (this.page() - 1) * PAGE_SIZE + 1));
  protected readonly rangeEnd = computed(() => Math.min(this.page() * PAGE_SIZE, this.count()));

  protected readonly form = this.fb.nonNullable.group({
    username: ['', Validators.required],
    email: [''],
    role: ['readonly' as Role, Validators.required],
    password: ['', [Validators.required, Validators.minLength(8)]],
    is_staff: [true],
  });

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(false);
    this.api.listUsers({ page: this.page(), search: this.search(), ordering: 'username' }).subscribe({
      next: (res) => {
        this.rows.set(res.results);
        this.count.set(res.count);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set(true);
      },
    });
  }

  protected onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
    this.page.set(1);
    this.load();
  }

  protected goTo(page: number): void {
    if (page < 1 || page > this.totalPages()) return;
    this.page.set(page);
    this.load();
  }

  protected create(): void {
    if (this.form.invalid) {
      this.form.markAllAsTouched();
      return;
    }
    this.createError.set(null);
    this.api.createUser(this.form.getRawValue()).subscribe({
      next: () => {
        this.showCreate.set(false);
        this.form.reset({ role: 'readonly', is_staff: true });
        this.page.set(1);
        this.load();
      },
      error: (err: HttpErrorResponse) => this.createError.set(this.firstError(err)),
    });
  }

  protected deactivate(user: AdminUser): void {
    if (!confirm(`Deactivate ${user.username}? They will lose admin access (reversible).`)) return;
    this.api.deactivateUser(user.id).subscribe({ next: () => this.load() });
  }

  private firstError(err: HttpErrorResponse): string {
    const data = err.error;
    if (data && typeof data === 'object') {
      const [field, value] = Object.entries(data)[0] ?? [];
      if (field) return `${field}: ${[value].flat()[0]}`;
    }
    return 'Could not save the user.';
  }
}
