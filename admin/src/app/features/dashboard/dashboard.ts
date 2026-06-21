import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin } from 'rxjs';
import { ApiService } from '../../core/api.service';

interface Metric {
  label: string;
  value: number;
  link: string;
  tone: 'primary' | 'error' | 'neutral';
}

@Component({
  selector: 'adm-dashboard',
  imports: [RouterLink],
  templateUrl: './dashboard.html',
  styleUrl: './dashboard.scss',
})
export class Dashboard {
  private readonly api = inject(ApiService);

  protected readonly loading = signal(true);
  protected readonly error = signal(false);
  protected readonly metrics = signal<Metric[]>([]);

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(false);
    forkJoin({
      users: this.api.listUsers({ page_size: 1 }),
      unresolved: this.api.listErrors({ page_size: 1, resolved: false }),
      audit: this.api.listAudit({ page_size: 1 }),
    }).subscribe({
      next: ({ users, unresolved, audit }) => {
        this.metrics.set([
          { label: 'Admin users', value: users.count, link: '/users', tone: 'primary' },
          { label: 'Unresolved errors', value: unresolved.count, link: '/error-logs', tone: 'error' },
          { label: 'Audit entries', value: audit.count, link: '/audit', tone: 'neutral' },
        ]);
        this.loading.set(false);
      },
      error: () => {
        this.loading.set(false);
        this.error.set(true);
      },
    });
  }
}
