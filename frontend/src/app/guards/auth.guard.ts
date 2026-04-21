import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  if (auth.isLoggedIn()) return true;

  // /login es una página 11ty fuera del router Angular
  window.location.href = '/login?acceso=requerido';
  return false;
};
