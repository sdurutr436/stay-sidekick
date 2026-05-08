import { inject } from '@angular/core';
import { CanActivateFn } from '@angular/router';
import { AuthService } from '../services/auth.service';

export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  if (!auth.isLoggedIn()) {
    window.location.href = '/login?acceso=requerido';
    return false;
  }

  if (auth.debeChangiarPassword) {
    window.location.href = '/cambio-password';
    return false;
  }

  return true;
};
