import { Component, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { RouterOutlet } from '@angular/router';
import { CvdMode, ThemeService } from './core/theme.service';

interface Health {
  status: string;
  service: string;
}

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App {
  private readonly http = inject(HttpClient);
  protected readonly themeSvc = inject(ThemeService);

  protected readonly title = signal('Rie Akane');
  protected readonly apiStatus = signal<string>('checking…');

  protected readonly cvdModes: { value: CvdMode; label: string }[] = [
    { value: 'none', label: 'Default' },
    { value: 'deuteranopia', label: 'Deuteranopia' },
    { value: 'protanopia', label: 'Protanopia' },
    { value: 'tritanopia', label: 'Tritanopia' },
    { value: 'grayscale', label: 'Grayscale' },
  ];

  protected readonly themeLabel = computed(() => {
    const t = this.themeSvc.theme();
    return t === 'system' ? 'System' : t === 'dark' ? 'Dark' : 'Light';
  });

  constructor() {
    this.http.get<Health>('/api/health/').subscribe({
      next: (res) => this.apiStatus.set(res.status),
      error: () => this.apiStatus.set('unreachable'),
    });
  }

  protected onCvdChange(event: Event): void {
    this.themeSvc.setCvd((event.target as HTMLSelectElement).value as CvdMode);
  }
}
