import { TestBed } from '@angular/core/testing';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  beforeEach(() => {
    localStorage.clear();
    document.documentElement.removeAttribute('data-theme');
    document.documentElement.removeAttribute('data-cvd');
    TestBed.configureTestingModule({});
  });

  it('defaults to system theme (no data-theme attribute)', () => {
    const svc = TestBed.inject(ThemeService);
    expect(svc.theme()).toBe('system');
    expect(document.documentElement.hasAttribute('data-theme')).toBe(false);
  });

  it('applies an explicit theme to <html> and persists it', () => {
    const svc = TestBed.inject(ThemeService);
    svc.setTheme('dark');
    expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    expect(localStorage.getItem('rieakane:theme')).toBe('dark');
  });

  it('cycles light → dark → system', () => {
    const svc = TestBed.inject(ThemeService);
    svc.setTheme('light');
    svc.toggleTheme();
    expect(svc.theme()).toBe('dark');
    svc.toggleTheme();
    expect(svc.theme()).toBe('system');
    svc.toggleTheme();
    expect(svc.theme()).toBe('light');
  });

  it('sets and clears CVD modes', () => {
    const svc = TestBed.inject(ThemeService);
    svc.setCvd('deuteranopia');
    expect(document.documentElement.getAttribute('data-cvd')).toBe('deuteranopia');
    svc.setCvd('none');
    expect(document.documentElement.hasAttribute('data-cvd')).toBe(false);
  });
});
