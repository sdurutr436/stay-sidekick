import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AuthService } from './auth.service';

export interface Plantilla {
  id: string;
  nombre: string;
  contenido: string;
  idioma: string;
  categoria: string | null;
  activa: boolean;
}

@Injectable({ providedIn: 'root' })
export class VaultService {
  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);

  private headers(): HttpHeaders {
    return new HttpHeaders({ Authorization: `Bearer ${this.auth.getToken() ?? ''}` });
  }

  getPlantillas(categoria?: string, idioma?: string): Observable<{ ok: boolean; plantillas: Plantilla[] }> {
    let params = new HttpParams();
    if (categoria) params = params.set('categoria', categoria);
    if (idioma)    params = params.set('idioma', idioma);
    return this.http.get<{ ok: boolean; plantillas: Plantilla[] }>('/api/vault/plantillas', { headers: this.headers(), params });
  }

  crearPlantilla(data: { nombre: string; contenido: string; idioma: string; categoria: string | null }): Observable<{ ok: boolean; plantilla: Plantilla }> {
    return this.http.post<{ ok: boolean; plantilla: Plantilla }>('/api/vault/plantillas', data, { headers: this.headers() });
  }

  actualizarPlantilla(id: string, data: { nombre: string; contenido: string; idioma?: string; categoria?: string | null }): Observable<{ ok: boolean; plantilla: Plantilla }> {
    return this.http.put<{ ok: boolean; plantilla: Plantilla }>(`/api/vault/plantillas/${id}`, data, { headers: this.headers() });
  }

  eliminarPlantilla(id: string): Observable<{ ok: boolean }> {
    return this.http.delete<{ ok: boolean }>(`/api/vault/plantillas/${id}`, { headers: this.headers() });
  }

  mejorar(plantillaId: string, contenido: string, idioma: string): Observable<{ ok: boolean; contenido: string }> {
    return this.http.post<{ ok: boolean; contenido: string }>(
      `/api/vault/plantillas/${plantillaId}/mejorar`,
      { contenido, idioma },
      { headers: this.headers() },
    );
  }

  traducir(plantillaId: string, contenido: string, idiomaDestino: string): Observable<{ ok: boolean; contenido: string }> {
    return this.http.post<{ ok: boolean; contenido: string }>(
      `/api/vault/plantillas/${plantillaId}/traducir`,
      { contenido, idioma_destino: idiomaDestino },
      { headers: this.headers() },
    );
  }

  getUso(): Observable<{ ok: boolean; uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number }> {
    return this.http.get<{ ok: boolean; uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number }>(
      '/api/ai/uso',
      { headers: this.headers() },
    );
  }
}
