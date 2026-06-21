import { Injectable, signal } from '@angular/core';

export type ThemeMode = 'light' | 'dark' | 'system';
export type CvdMode = 'none' | 'deuteranopia' | 'protanopia' | 'tritanopia' | 'grayscale';

const THEME_KEY = 'rieakane:theme';
const CVD_KEY = 'rieakane:cvd';

/**
 * Owns the visual theme. Writes `data-theme` / `data-cvd` onto <html> so the
 * token themes in shared/styles/_tokens.scss take effect. Persists the user's
 * choice and falls back to the OS `prefers-color-scheme` in 'system' mode.
 *
 * Token values live in ONE file; this service only flips attributes.
 */
@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly root = document.documentElement;

  readonly theme = signal<ThemeMode>(this.readStored(THEME_KEY, 'system') as ThemeMode);
  readonly cvd = signal<CvdMode>(this.readStored(CVD_KEY, 'none') as CvdMode);

  constructor() {
    this.apply();
    // React to OS changes while in 'system' mode (matchMedia may be absent in
    // non-browser/test environments).
    if (typeof window !== 'undefined' && typeof window.matchMedia === 'function') {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        if (this.theme() === 'system') this.apply();
      });
    }
  }

  setTheme(mode: ThemeMode): void {
    this.theme.set(mode);
    this.persist(THEME_KEY, mode);
    this.apply();
  }

  /** Cycle light → dark → system for a single toggle control. */
  toggleTheme(): void {
    const next: ThemeMode =
      this.theme() === 'light' ? 'dark' : this.theme() === 'dark' ? 'system' : 'light';
    this.setTheme(next);
  }

  setCvd(mode: CvdMode): void {
    this.cvd.set(mode);
    this.persist(CVD_KEY, mode);
    this.apply();
  }

  private apply(): void {
    if (this.theme() === 'system') this.root.removeAttribute('data-theme');
    else this.root.setAttribute('data-theme', this.theme());

    if (this.cvd() === 'none') this.root.removeAttribute('data-cvd');
    else this.root.setAttribute('data-cvd', this.cvd());
  }

  private readStored(key: string, fallback: string): string {
    try {
      return localStorage.getItem(key) ?? fallback;
    } catch {
      return fallback;
    }
  }

  private persist(key: string, value: string): void {
    try {
      localStorage.setItem(key, value);
    } catch {
      /* storage may be unavailable (private mode); ignore */
    }
  }
}
