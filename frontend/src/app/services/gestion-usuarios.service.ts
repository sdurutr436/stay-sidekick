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

export interface EmpresaCreatePayload {
  nombre: string;
  email: string;
}

@Injectable({ providedIn: 'root' })
export class GestionUsuariosService {
  private readonly http = inject(HttpClient);

  private _params(empresaId?: string): Record<string, string> {
    return empresaId ? { empresa_id: empresaId } : {};
  }

  getEmpresas(): Observable<EmpresaItem[]> {
    return this.http
      .get<{ ok: boolean; empresas: EmpresaItem[] }>('/api/empresas')
      .pipe(map(res => res.empresas));
  }

  getUsuarios(empresaId?: string): Observable<{ usuarios: Usuario[]; max_usuarios: number }> {
    return this.http
      .get<{ ok: boolean; usuarios: Usuario[]; max_usuarios: number }>('/api/usuarios', { params: this._params(empresaId) })
      .pipe(map(res => ({ usuarios: res.usuarios, max_usuarios: res.max_usuarios })));
  }

  crearUsuario(payload: UsuarioCreatePayload, empresaId?: string): Observable<{ usuario: Usuario; password_temporal: string }> {
    return this.http
      .post<{ ok: boolean; usuario: Usuario; password_temporal: string }>('/api/usuarios', payload, { params: this._params(empresaId) })
      .pipe(map(res => ({ usuario: res.usuario, password_temporal: res.password_temporal })));
  }

  eliminarUsuario(id: string, empresaId?: string): Observable<void> {
    return this.http
      .delete<{ ok: boolean }>(`/api/usuarios/${id}`, { params: this._params(empresaId) })
      .pipe(map(() => undefined));
  }

  editarRol(id: string, rol: string, empresaId?: string): Observable<Usuario> {
    return this.http
      .patch<{ ok: boolean; usuario: Usuario }>(`/api/usuarios/${id}`, { rol }, { params: this._params(empresaId) })
      .pipe(map(res => res.usuario));
  }

  resetearPassword(id: string, empresaId?: string): Observable<{ password_temporal: string }> {
    return this.http
      .patch<{ ok: boolean; password_temporal: string }>(`/api/usuarios/${id}/contrasena`, {}, { params: this._params(empresaId) })
      .pipe(map(res => ({ password_temporal: res.password_temporal })));
  }

  crearEmpresa(payload: EmpresaCreatePayload): Observable<EmpresaItem> {
    return this.http
      .post<{ ok: boolean; empresa: EmpresaItem }>('/api/empresas', payload)
      .pipe(map(res => res.empresa));
  }
}
