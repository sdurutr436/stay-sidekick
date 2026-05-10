import { inject, Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

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

  getPlantillas(categoria?: string, idioma?: string): Observable<{ ok: boolean; plantillas: Plantilla[] }> {
    let params = new HttpParams();
    if (categoria) params = params.set('categoria', categoria);
    if (idioma)    params = params.set('idioma', idioma);
    return this.http.get<{ ok: boolean; plantillas: Plantilla[] }>('/api/vault/plantillas', { params });
  }

  crearPlantilla(data: { nombre: string; contenido: string; idioma: string; categoria: string | null }): Observable<{ ok: boolean; plantilla: Plantilla }> {
    return this.http.post<{ ok: boolean; plantilla: Plantilla }>('/api/vault/plantillas', data);
  }

  actualizarPlantilla(id: string, data: { nombre: string; contenido: string; idioma?: string; categoria?: string | null }): Observable<{ ok: boolean; plantilla: Plantilla }> {
    return this.http.put<{ ok: boolean; plantilla: Plantilla }>(`/api/vault/plantillas/${id}`, data);
  }

  eliminarPlantilla(id: string): Observable<{ ok: boolean }> {
    return this.http.delete<{ ok: boolean }>(`/api/vault/plantillas/${id}`);
  }

  mejorar(plantillaId: string, contenido: string, idioma: string): Observable<{ ok: boolean; contenido: string }> {
    return this.http.post<{ ok: boolean; contenido: string }>(
      `/api/vault/plantillas/${plantillaId}/mejoras`,
      { contenido, idioma },
    );
  }

  traducir(plantillaId: string, contenido: string, idiomaDestino: string): Observable<{ ok: boolean; contenido: string }> {
    return this.http.post<{ ok: boolean; contenido: string }>(
      `/api/vault/plantillas/${plantillaId}/traducciones`,
      { contenido, idioma_destino: idiomaDestino },
    );
  }

  getUso(): Observable<{ ok: boolean; uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number }> {
    return this.http.get<{ ok: boolean; uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number }>(
      '/api/ai/uso',
    );
  }
}
