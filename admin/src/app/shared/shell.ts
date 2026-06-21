import { Component, OnInit, computed, inject } from '@angular/core';
import { Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { AuthService } from '../core/auth.service';
import { CvdMode, ThemeService } from '../core/theme.service';

interface NavItem {
  path: string;
  label: string;
  icon: string;
}

@Component({
  selector: 'adm-shell',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './shell.html',
  styleUrl: './shell.scss',
})
export class Shell implements OnInit {
  protected readonly auth = inject(AuthService);
  protected readonly themeSvc = inject(ThemeService);
  private readonly router = inject(Router);

  protected readonly nav: NavItem[] = [
    { path: '/dashboard', label: 'Dashboard', icon: '▦' },
    { path: '/users', label: 'Users', icon: '👤' },
    { path: '/error-logs', label: 'Error logs', icon: '⚠' },
    { path: '/audit', label: 'Audit trail', icon: '🕓' },
  ];

  protected readonly cvdModes: { value: CvdMode; label: string }[] = [
    { value: 'none', label: 'Default' },
    { value: 'deuteranopia', label: 'Deuteranopia' },
    { value: 'protanopia', label: 'Protanopia' },
    { value: 'tritanopia', label: 'Tritanopia' },
    { value: 'grayscale', label: 'Grayscale' },
  ];

  protected readonly userLabel = computed(() => {
    const u = this.auth.user();
    return u ? `${u.username} · ${u.role}` : '';
  });

  protected readonly themeLabel = computed(() => {
    const t = this.themeSvc.theme();
    return t === 'system' ? 'System' : t === 'dark' ? 'Dark' : 'Light';
  });

  ngOnInit(): void {
    // Refresh the profile if we hold a token but lost the in-memory user (reload).
    if (this.auth.isAuthenticated() && !this.auth.user()) {
      this.auth.loadMe().subscribe({ error: () => this.auth.clear() });
    }
  }

  protected onCvdChange(event: Event): void {
    this.themeSvc.setCvd((event.target as HTMLSelectElement).value as CvdMode);
  }

  protected logout(): void {
    this.auth.logout();
    this.router.navigate(['/login']);
  }
}
