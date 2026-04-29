import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface Apartamento {
  id: string;
  id_externo: string | null;
  nombre: string;
  direccion: string | null;
  ciudad: string | null;
  pms_origen: 'smoobu' | 'manual' | 'xlsx' | null;
  activo: boolean;
}

export interface ApartamentoCreatePayload {
  nombre: string;
  ciudad?: string;
  direccion?: string;
  id_externo?: string;
}

export interface ImportacionResultado {
  total: number;
  nuevos: number;
  actualizados: number;
  warnings?: string[];
}

export interface ApartamentoConflicto {
  id_externo: string;
  nombre: string;
  nombre_actual?: string;
  ciudad?: string | null;
  direccion?: string | null;
}

export interface ImportacionPreview {
  nuevos: ApartamentoConflicto[];
  actualizados: ApartamentoConflicto[];
  sin_cambios: ApartamentoConflicto[];
  errores: string[];
}

export interface PmsConfig {
  proveedor: string;
  endpoint: string | null;
  activo: boolean;
  ultimo_sync: string | null;
}

export interface XlsxColumnas {
  col_id_externo: number;
  col_nombre: number;
  col_direccion: number;
  col_ciudad: number;
}

@Injectable({ providedIn: 'root' })
export class ApartamentosService {
  private readonly http = inject(HttpClient);

  listar(): Observable<Apartamento[]> {
    return this.http
      .get<{ ok: boolean; apartamentos: Apartamento[] }>('/api/apartamentos')
      .pipe(map(res => res.apartamentos));
  }

  crear(payload: ApartamentoCreatePayload): Observable<Apartamento> {
    return this.http
      .post<{ ok: boolean; apartamento: Apartamento }>('/api/apartamentos', payload)
      .pipe(map(res => res.apartamento));
  }

  actualizar(id: string, payload: Partial<ApartamentoCreatePayload>): Observable<Apartamento> {
    return this.http
      .put<{ ok: boolean; apartamento: Apartamento }>(`/api/apartamentos/${id}`, payload)
      .pipe(map(res => res.apartamento));
  }

  eliminar(id: string): Observable<void> {
    return this.http
      .delete<{ ok: boolean }>(`/api/apartamentos/${id}`)
      .pipe(map(() => undefined));
  }

  sincronizarSmoobu(): Observable<{ total: number; nuevos: number; actualizados: number }> {
    return this.http
      .post<{ ok: boolean; resultado: { total: number; nuevos: number; actualizados: number } }>(
        '/api/apartamentos/sincronizacion/smoobu',
        {}
      )
      .pipe(map(res => res.resultado));
  }

  importarXlsx(file: File): Observable<ImportacionResultado> {
    const form = new FormData();
    form.append('file', file);
    return this.http
      .post<{ ok: boolean; resultado: ImportacionResultado; warnings?: string[] }>(
        '/api/apartamentos/importacion',
        form
      )
      .pipe(map(res => ({ ...res.resultado, warnings: res.warnings })));
  }

  previewXlsx(file: File): Observable<ImportacionPreview> {
    const form = new FormData();
    form.append('file', file);
    return this.http
      .post<{ ok: boolean; preview: ImportacionPreview }>(
        '/api/apartamentos/importacion/preview',
        form
      )
      .pipe(map(res => res.preview));
  }

  getPmsStatus(): Observable<PmsConfig | null> {
    return this.http
      .get<{ ok: boolean; config: PmsConfig | null }>('/api/apartamentos/pms')
      .pipe(map(res => res.config));
  }

  getXlsxColumnas(): Observable<XlsxColumnas | null> {
    return this.http
      .get<{ ok: boolean; config: XlsxColumnas | null }>('/api/perfil/xlsx-apartamentos')
      .pipe(map(res => res.config));
  }

  saveXlsxColumnas(config: XlsxColumnas): Observable<void> {
    return this.http
      .put<{ ok: boolean }>('/api/perfil/xlsx-apartamentos', config)
      .pipe(map(() => undefined));
  }
}
