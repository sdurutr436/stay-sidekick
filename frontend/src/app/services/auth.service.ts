import { Injectable, inject } from '@angular/core';
import { ToastService } from './toast.service';

interface JwtPayload {
  sub: string;
  exp: number;
  user_id: string;
  empresa_id: string;
  rol: string;
  es_superadmin?: boolean;
  debe_cambiar_password?: boolean;
}

// Antelación con la que avisamos al usuario de que su JWT caducará.
const AVISO_PREVIO_MS = 2 * 60 * 1000;

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY = 'ss_token';
  private readonly toast = inject(ToastService);

  private avisoTimer: ReturnType<typeof setTimeout> | null = null;

  constructor() {
    this.programarAvisoExpiracion();
  }

  getToken(): string | null {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  private decodePayload(token: string): JwtPayload | null {
    try {
      const base64 = token.split('.')[1];
      return JSON.parse(atob(base64)) as JwtPayload;
    } catch {
      return null;
    }
  }

  isLoggedIn(): boolean {
    const token = this.getToken();
    if (!token) return false;
    const payload = this.decodePayload(token);
    if (!payload) return false;
    return payload.exp > Date.now() / 1000;
  }

  getUser(): JwtPayload | null {
    const token = this.getToken();
    if (!token) return null;
    return this.decodePayload(token);
  }

  get isAdmin(): boolean {
    return this.getUser()?.rol === 'admin';
  }

  get esSuperAdmin(): boolean {
    return this.getUser()?.es_superadmin === true;
  }

  get debeChangiarPassword(): boolean {
    return this.getUser()?.debe_cambiar_password === true;
  }

  logout(): void {
    this.cancelarAvisoExpiracion();
    localStorage.removeItem(this.TOKEN_KEY);
    window.location.href = '/login/';
  }

  programarAvisoExpiracion(): void {
    this.cancelarAvisoExpiracion();
    const payload = this.getUser();
    if (!payload?.exp) return;

    const ahoraMs       = Date.now();
    const expMs         = payload.exp * 1000;
    const restanteMs    = expMs - ahoraMs;
    const tiempoAvisoMs = restanteMs - AVISO_PREVIO_MS;

    if (tiempoAvisoMs <= 0) return;

    this.avisoTimer = setTimeout(() => {
      this.toast.showWarning('Tu sesión expirará en 2 minutos. Guarda tu trabajo.', 0);
    }, tiempoAvisoMs);
  }

  private cancelarAvisoExpiracion(): void {
    if (this.avisoTimer) {
      clearTimeout(this.avisoTimer);
      this.avisoTimer = null;
    }
  }
}
