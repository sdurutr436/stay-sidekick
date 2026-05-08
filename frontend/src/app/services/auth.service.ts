import { Injectable } from '@angular/core';

interface JwtPayload {
  sub: string;
  exp: number;
  user_id: string;
  empresa_id: string;
  rol: string;
  es_superadmin?: boolean;
  debe_cambiar_password?: boolean;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly TOKEN_KEY = 'ss_token';

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
    localStorage.removeItem(this.TOKEN_KEY);
    window.location.href = '/login';
  }
}
