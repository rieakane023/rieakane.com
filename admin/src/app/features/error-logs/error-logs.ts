import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ApiService, ListQuery } from '../../core/api.service';
import { ErrorLog } from '../../core/models';

const PAGE_SIZE = 25;

@Component({
  selector: 'adm-error-logs',
  imports: [DatePipe],
  templateUrl: './error-logs.html',
  styleUrl: './error-logs.scss',
})
export class ErrorLogs {
  private readonly api = inject(ApiService);

  protected readonly rows = signal<ErrorLog[]>([]);
  protected readonly count = signal(0);
  protected readonly page = signal(1);
  protected readonly search = signal('');
  protected readonly level = signal('');
  protected readonly resolved = signal('');
  protected readonly loading = signal(true);
  protected readonly error = signal(false);
  protected readonly expandedId = signal<number | null>(null);

  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.count() / PAGE_SIZE)));
  protected readonly rangeStart = computed(() => (this.count() === 0 ? 0 : (this.page() - 1) * PAGE_SIZE + 1));
  protected readonly rangeEnd = computed(() => Math.min(this.page() * PAGE_SIZE, this.count()));

  constructor() {
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(false);
    const query: ListQuery = {
      page: this.page(),
      search: this.search(),
      ordering: '-timestamp',
    };
    if (this.level()) query['level'] = this.level();
    if (this.resolved()) query['resolved'] = this.resolved();

    this.api.listErrors(query).subscribe({
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
    this.reset();
  }
  protected onLevel(event: Event): void {
    this.level.set((event.target as HTMLSelectElement).value);
    this.reset();
  }
  protected onResolved(event: Event): void {
    this.resolved.set((event.target as HTMLSelectElement).value);
    this.reset();
  }
  private reset(): void {
    this.page.set(1);
    this.load();
  }

  protected goTo(page: number): void {
    if (page < 1 || page > this.totalPages()) return;
    this.page.set(page);
    this.load();
  }

  protected toggleExpand(id: number): void {
    this.expandedId.set(this.expandedId() === id ? null : id);
  }

  protected toggleResolved(row: ErrorLog): void {
    this.api.setErrorResolved(row.id, !row.resolved).subscribe({
      next: (updated) => this.rows.update((rows) => rows.map((r) => (r.id === row.id ? updated : r))),
    });
  }

  protected badgeClass(level: string): string {
    return level === 'critical' ? 'badge--error' : level === 'warning' ? 'badge--warning' : 'badge--error';
  }
}
