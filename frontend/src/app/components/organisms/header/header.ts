import { Component, inject } from '@angular/core';
import { Router, NavigationEnd, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map, startWith } from 'rxjs';
import { SidenavService } from '../../../services/sidenav.service';
import { AuthService } from '../../../services/auth.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.html',
  styleUrl: './header.scss',
  standalone: true,
  imports: [RouterLink],
})
export class HeaderComponent {
  private readonly router = inject(Router);
  readonly sidenavService = inject(SidenavService);
  readonly auth = inject(AuthService);

  readonly isMenuPage = toSignal(
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd),
      map(() => this.router.url.startsWith('/menu')),
      startWith(this.router.url.startsWith('/menu')),
    ),
    { initialValue: this.router.url.startsWith('/menu') },
  );
}
