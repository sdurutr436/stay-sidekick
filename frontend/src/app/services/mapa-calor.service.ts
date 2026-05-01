import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

export interface DiaCalor {
  fecha: string;          // ISO YYYY-MM-DD
  checkins: number;
  checkouts: number;
  mesAdyacente: boolean;  // true si el día está fuera del rango seleccionado
                          // pero pertenece a la semana visible del calendario
}

export interface MapaCalorResponse {
  dias: DiaCalor[];
}

export interface UmbralesCalor {
  nivel1: number;  // ≤ este valor → intensidad 1 (más claro)
  nivel2: number;
  nivel3: number;
  // nivel4 = cualquier valor superior a nivel3 → intensidad máxima
}

export interface HeatmapXlsxColumnas {
  col_fecha_checkin:  number;  // columna de fecha en el XLSX de check-ins  (1 = col. A)
  col_fecha_checkout: number;  // columna de fecha en el XLSX de check-outs (1 = col. A)
}

@Injectable({ providedIn: 'root' })
export class MapaCalorService {
  private readonly http = inject(HttpClient);

  generarDesdePms(desde: string, hasta: string): Observable<MapaCalorResponse> {
    return this.http.get<MapaCalorResponse>(`/api/heatmap?desde=${desde}&hasta=${hasta}`);
  }

  generarDesdeXlsx(checkins: File, checkouts?: File): Observable<MapaCalorResponse> {
    const fd = new FormData();
    fd.append('checkins', checkins);
    if (checkouts) fd.append('checkouts', checkouts);
    return this.http.post<MapaCalorResponse>('/api/heatmap/xlsx', fd);
  }

  getUmbrales(): Observable<UmbralesCalor> {
    return this.http.get<UmbralesCalor>('/api/heatmap/umbrales');
  }

  saveUmbrales(umbrales: UmbralesCalor): Observable<void> {
    return this.http.put<void>('/api/heatmap/umbrales', umbrales);
  }

  getXlsxColumnas(): Observable<HeatmapXlsxColumnas | null> {
    return this.http
      .get<{ ok: boolean; config: HeatmapXlsxColumnas | null }>('/api/heatmap/xlsx-columnas')
      .pipe(map(res => res.config));
  }

  saveXlsxColumnas(config: HeatmapXlsxColumnas): Observable<void> {
    return this.http.put<void>('/api/heatmap/xlsx-columnas', config);
  }
}
