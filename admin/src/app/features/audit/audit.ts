import { Component, computed, inject, signal } from '@angular/core';
import { DatePipe } from '@angular/common';
import { ApiService, ListQuery } from '../../core/api.service';
import { AuditLog, FieldChange } from '../../core/models';

const PAGE_SIZE = 25;

@Component({
  selector: 'adm-audit',
  imports: [DatePipe],
  templateUrl: './audit.html',
  styleUrl: './audit.scss',
})
export class Audit {
  private readonly api = inject(ApiService);

  protected readonly models = signal<string[]>([]);
  protected readonly selectedModel = signal('');
  protected readonly action = signal('');
  protected readonly search = signal('');
  protected readonly rows = signal<AuditLog[]>([]);
  protected readonly count = signal(0);
  protected readonly page = signal(1);
  protected readonly loading = signal(true);
  protected readonly error = signal(false);
  protected readonly expandedId = signal<number | null>(null);

  protected readonly totalPages = computed(() => Math.max(1, Math.ceil(this.count() / PAGE_SIZE)));
  protected readonly rangeStart = computed(() => (this.count() === 0 ? 0 : (this.page() - 1) * PAGE_SIZE + 1));
  protected readonly rangeEnd = computed(() => Math.min(this.page() * PAGE_SIZE, this.count()));

  constructor() {
    this.api.auditModels().subscribe({ next: (m) => this.models.set(m) });
    this.load();
  }

  protected load(): void {
    this.loading.set(true);
    this.error.set(false);
    const query: ListQuery = { page: this.page(), search: this.search(), ordering: '-timestamp' };
    if (this.selectedModel()) query['model'] = this.selectedModel();
    if (this.action()) query['action'] = this.action();

    this.api.listAudit(query).subscribe({
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

  protected onModel(event: Event): void {
    this.selectedModel.set((event.target as HTMLSelectElement).value);
    this.reset();
  }
  protected onAction(event: Event): void {
    this.action.set((event.target as HTMLSelectElement).value);
    this.reset();
  }
  protected onSearch(event: Event): void {
    this.search.set((event.target as HTMLInputElement).value);
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

  protected fields(row: AuditLog): { name: string; old: unknown; new: unknown }[] {
    return Object.entries(row.changes ?? {}).map(([name, c]: [string, FieldChange]) => ({
      name,
      old: c.old,
      new: c.new,
    }));
  }

  protected actionBadge(action: string): string {
    return action === 'create' ? 'badge--success' : action === 'delete' ? 'badge--error' : 'badge--info';
  }

  protected display(value: unknown): string {
    if (value === null || value === undefined || value === '') return '—';
    return String(value);
  }
}
