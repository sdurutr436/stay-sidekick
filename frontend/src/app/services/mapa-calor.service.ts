import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface DiaCalor {
  fecha: string;
  checkins: number;
  checkouts: number;
  mesAdyacente: boolean;
}

export interface MapaCalorResponse {
  dias: DiaCalor[];
  warnings?: string[];
}

export interface UmbralesCalor {
  nivel1: number;
  nivel2: number;
  nivel3: number;
}

export interface ConfigXlsx {
  col_fecha_checkin: string | null;
  col_fecha_checkout: string | null;
}

@Injectable({ providedIn: 'root' })
export class MapaCalorService {
  private readonly http = inject(HttpClient);

  generarDesdePms(desde: string, hasta: string): Observable<MapaCalorResponse> {
    return this.http.get<{ ok: boolean; dias: DiaCalor[] }>(
      `/api/heatmap?desde=${desde}&hasta=${hasta}`
    ).pipe(map(res => ({ dias: res.dias })));
  }

  generarDesdeXlsx(checkins: File, checkouts: File | undefined, desde: string, hasta: string): Observable<MapaCalorResponse> {
    const fd = new FormData();
    fd.append('checkins', checkins);
    if (checkouts) fd.append('checkouts', checkouts);
    fd.append('desde', desde);
    fd.append('hasta', hasta);
    return this.http.post<{ ok: boolean; dias: DiaCalor[]; warnings?: string[] }>(
      '/api/heatmap/xlsx', fd
    ).pipe(map(res => ({ dias: res.dias, warnings: res.warnings })));
  }

  getUmbrales(): Observable<UmbralesCalor> {
    return this.http
      .get<{ ok: boolean; umbrales: UmbralesCalor }>('/api/heatmap/umbrales')
      .pipe(map(res => res.umbrales));
  }

  saveUmbrales(umbrales: UmbralesCalor): Observable<UmbralesCalor> {
    return this.http
      .put<{ ok: boolean; umbrales: UmbralesCalor }>('/api/heatmap/umbrales', umbrales)
      .pipe(map(res => res.umbrales));
  }

  getConfigXlsx(): Observable<ConfigXlsx> {
    return this.http
      .get<{ ok: boolean; config: ConfigXlsx }>('/api/heatmap/config-xlsx')
      .pipe(map(res => res.config));
  }

  saveConfigXlsx(config: ConfigXlsx): Observable<ConfigXlsx> {
    return this.http
      .put<{ ok: boolean; config: ConfigXlsx }>('/api/heatmap/config-xlsx', config)
      .pipe(map(res => res.config));
  }
}
