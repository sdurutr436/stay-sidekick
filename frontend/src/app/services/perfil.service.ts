import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface PerfilData {
  email: string;
  rol: string;
  empresa_id: string;
  password_changed_at: string | null;
}

export interface IntegracionesData {
  pms:    { configurado: boolean; proveedor: string | null };
  google: { configurado: boolean };
  ia:     { configurado: boolean; proveedor: string | null; modelo: string | null };
}

@Injectable({ providedIn: 'root' })
export class PerfilService {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);

  private headers(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.auth.getToken() ?? ''}` });
  }

  getPerfil(): Observable<{ ok: boolean; data: PerfilData }> {
    return this.http.get<{ ok: boolean; data: PerfilData }>('/api/perfil', { headers: this.headers() });
  }

  cambiarPassword(passwordActual: string, passwordNueva: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/password',
      { password_actual: passwordActual, password_nueva: passwordNueva },
      { headers: this.headers() },
    );
  }

  getIntegraciones(): Observable<{ ok: boolean; data: IntegracionesData }> {
    return this.http.get<{ ok: boolean; data: IntegracionesData }>('/api/perfil/integraciones', { headers: this.headers() });
  }

  actualizarPMS(proveedor: string, apiKey: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/integraciones/pms',
      { proveedor, api_key: apiKey },
      { headers: this.headers() },
    );
  }

  actualizarIA(proveedor: string, modelo: string, apiKey?: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/integraciones/ia',
      { proveedor, modelo: modelo || null, api_key: apiKey || null },
      { headers: this.headers() },
    );
  }
}
