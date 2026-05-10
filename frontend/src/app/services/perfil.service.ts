import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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

  getPerfil(): Observable<{ ok: boolean; data: PerfilData }> {
    return this.http.get<{ ok: boolean; data: PerfilData }>('/api/perfil');
  }

  cambiarPassword(passwordActual: string, passwordNueva: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/password',
      { password_actual: passwordActual, password_nueva: passwordNueva },
    );
  }

  getIntegraciones(): Observable<{ ok: boolean; data: IntegracionesData }> {
    return this.http.get<{ ok: boolean; data: IntegracionesData }>('/api/perfil/integraciones');
  }

  actualizarPMS(proveedor: string, apiKey: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/integraciones/pms',
      { proveedor, api_key: apiKey },
    );
  }

  actualizarIA(proveedor: string, modelo: string, apiKey?: string): Observable<{ ok: boolean; errors?: string[] }> {
    return this.http.put<{ ok: boolean; errors?: string[] }>(
      '/api/perfil/integraciones/ia',
      { proveedor, modelo: modelo || null, api_key: apiKey || null },
    );
  }

  eliminarPMS(): Observable<{ ok: boolean }> {
    return this.http.delete<{ ok: boolean }>('/api/perfil/integraciones/pms');
  }

  eliminarIA(): Observable<{ ok: boolean }> {
    return this.http.delete<{ ok: boolean }>('/api/perfil/integraciones/ia');
  }
}
