import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { ThemeService } from './core/theme.service';

@Component({
  selector: 'adm-root',
  imports: [RouterOutlet],
  template: '<router-outlet />',
})
export class App {
  // Eager-init so the persisted theme is applied on first paint.
  private readonly theme = inject(ThemeService);
}
