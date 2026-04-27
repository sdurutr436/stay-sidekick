import { Component, inject } from '@angular/core';
import { Router } from '@angular/router';
import { AuthService } from '../../services/auth.service';

/**
 * Componente 404 para rutas desconocidas dentro de la SPA.
 * Header y footer los provee app.html (envuelven todos los router-outlet).
 * No se importan HeaderComponent/FooterComponent para evitar duplicarlos.
 *
 * TODO (ITCSS): añadir estilos para .not-found, __code, __title,
 * __description y __cta en styles/components/_not-found.scss.
 */
@Component({
  selector: 'app-not-found',
  standalone: true,
  imports: [],
  template: `
    <section class="l-container u-text-center">
      <div class="not-found">

        <p class="not-found__code" aria-hidden="true">404</p>
        <h1 class="not-found__title">Página no encontrada</h1>
        <p class="not-found__description u-text-secondary">
          La página que buscas no existe dentro del panel.
        </p>

        <button
          class="not-found__cta btn btn--primary btn--md"
          (click)="goBack()"
        >
          Volver
        </button>

      </div>
    </section>
  `,
})
export class NotFoundComponent {
  private readonly router = inject(Router);
  private readonly auth = inject(AuthService);

  goBack(): void {
    if (this.auth.isLoggedIn()) {
      this.router.navigate(['/menu']);
    } else {
      window.location.href = '/';
    }
  }
}
