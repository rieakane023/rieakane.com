import { Component, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterOutlet } from '@angular/router';

interface Health {
  status: string;
  service: string;
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  private readonly http = inject(HttpClient);

  protected readonly title = signal('Rie Akane');
  protected readonly apiStatus = signal<string>('checking…');

  constructor() {
    this.http.get<Health>('/api/health/').subscribe({
      next: (res) => this.apiStatus.set(res.status),
      error: () => this.apiStatus.set('unreachable')
    });
  }
}
