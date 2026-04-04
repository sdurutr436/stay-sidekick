import { Component, inject } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { filter, map, startWith } from 'rxjs';
import { SidenavService } from '../../services/sidenav.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.html',
  styleUrl: './header.scss',
  standalone: true,
})
export class HeaderComponent {
  private readonly router = inject(Router);
  readonly sidenavService = inject(SidenavService);

  // Señal reactiva que indica si estamos en la página de menú
  readonly isMenuPage = toSignal(
    this.router.events.pipe(
      filter(e => e instanceof NavigationEnd),
      map(() => this.router.url.startsWith('/menu')),
      startWith(this.router.url.startsWith('/menu')),
    ),
    { initialValue: this.router.url.startsWith('/menu') },
  );
}
