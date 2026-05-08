import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, map } from 'rxjs';

export interface Usuario {
  id: string;
  email: string;
  rol: 'admin' | 'operativo';
  activo: boolean;
  created_at: string;
}

export interface EmpresaItem {
  id: string;
  nombre: string;
  email: string;
}

export interface UsuarioCreatePayload {
  email: string;
  rol: string;
}

@Injectable({ providedIn: 'root' })
export class GestionUsuariosService {
  private readonly http = inject(HttpClient);

  getEmpresas(): Observable<EmpresaItem[]> {
    return this.http
      .get<{ ok: boolean; empresas: EmpresaItem[] }>('/api/empresas')
      .pipe(map(res => res.empresas));
  }

  getUsuarios(empresaId?: string): Observable<{ usuarios: Usuario[]; max_usuarios: number }> {
    const params = empresaId ? { empresa_id: empresaId } : {};
    return this.http
      .get<{ ok: boolean; usuarios: Usuario[]; max_usuarios: number }>('/api/usuarios', { params })
      .pipe(map(res => ({ usuarios: res.usuarios, max_usuarios: res.max_usuarios })));
  }

  crearUsuario(payload: UsuarioCreatePayload, empresaId?: string): Observable<{ usuario: Usuario; password_temporal: string }> {
    const params = empresaId ? { empresa_id: empresaId } : {};
    return this.http
      .post<{ ok: boolean; usuario: Usuario; password_temporal: string }>('/api/usuarios', payload, { params })
      .pipe(map(res => ({ usuario: res.usuario, password_temporal: res.password_temporal })));
  }

  eliminarUsuario(id: string, empresaId?: string): Observable<void> {
    const params = empresaId ? { empresa_id: empresaId } : {};
    return this.http
      .delete<{ ok: boolean }>(`/api/usuarios/${id}`, { params })
      .pipe(map(() => undefined));
  }

  editarRol(id: string, rol: string, empresaId?: string): Observable<Usuario> {
    const params = empresaId ? { empresa_id: empresaId } : {};
    return this.http
      .patch<{ ok: boolean; usuario: Usuario }>(`/api/usuarios/${id}`, { rol }, { params })
      .pipe(map(res => res.usuario));
  }

  resetearPassword(id: string, empresaId?: string): Observable<{ password_temporal: string }> {
    const params = empresaId ? { empresa_id: empresaId } : {};
    return this.http
      .patch<{ ok: boolean; password_temporal: string }>(`/api/usuarios/${id}/resetear-password`, {}, { params })
      .pipe(map(res => ({ password_temporal: res.password_temporal })));
  }
}
