import { Component, inject } from '@angular/core';
import { Router, NavigationEnd, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map, startWith } from 'rxjs';
import { SidenavService } from '../../../services/sidenav.service';
import { AuthService } from '../../../services/auth.service';
import { ThemeToggleComponent } from '../../molecules/theme-toggle/theme-toggle';

@Component({
  selector: 'app-header',
  templateUrl: './header.html',
  styleUrl: './header.scss',
  standalone: true,
  imports: [RouterLink, ThemeToggleComponent],
})
export class HeaderComponent {
  private readonly router = inject(Router);
  readonly sidenavService = inject(SidenavService);
  readonly auth = inject(AuthService);

  // Toda la SPA vive bajo /menu/ — el hamburger es siempre visible.
  readonly isMenuPage = toSignal(
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd),
      map(() => true),
      startWith(true),
    ),
    { initialValue: true },
  );
}
