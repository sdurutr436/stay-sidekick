import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface XlsxReservasCols {
  col_checkin: number;
  col_nombre: number;
  col_tipologia: number;
  col_telefono: number;
}

export interface PreferenciasContactos {
  plantilla: string;
  separador_apt: string;
  formato_fecha_salida: string;
  xlsx_reservas: XlsxReservasCols;
}

export const PREFS_CONTACTOS_DEFECTO: PreferenciasContactos = {
  plantilla: '{FECHA} - {APT} - {NOMBRE}',
  separador_apt: ', ',
  formato_fecha_salida: 'YYMMDD',
  xlsx_reservas: { col_checkin: 0, col_nombre: 0, col_tipologia: 0, col_telefono: 0 },
};

@Injectable({ providedIn: 'root' })
export class ContactosService {
  private readonly http = inject(HttpClient);

  getPreferencias(): Observable<PreferenciasContactos> {
    return this.http
      .get<{ ok: boolean; preferencias: PreferenciasContactos }>('/api/contactos/preferencias')
      .pipe(map(res => res.preferencias));
  }

  savePreferencias(prefs: Partial<PreferenciasContactos>): Observable<PreferenciasContactos> {
    return this.http
      .put<{ ok: boolean; preferencias: PreferenciasContactos }>('/api/contactos/preferencias', prefs)
      .pipe(map(res => res.preferencias));
  }
}
