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

export interface UsuarioCreatePayload {
  email: string;
  rol: string;
}

@Injectable({ providedIn: 'root' })
export class GestionUsuariosService {
  private readonly http = inject(HttpClient);

  getUsuarios(): Observable<{ usuarios: Usuario[]; max_usuarios: number }> {
    return this.http
      .get<{ ok: boolean; usuarios: Usuario[]; max_usuarios: number }>('/api/usuarios')
      .pipe(map(res => ({ usuarios: res.usuarios, max_usuarios: res.max_usuarios })));
  }

  crearUsuario(payload: UsuarioCreatePayload): Observable<{ usuario: Usuario; password_temporal: string }> {
    return this.http
      .post<{ ok: boolean; usuario: Usuario; password_temporal: string }>('/api/usuarios', payload)
      .pipe(map(res => ({ usuario: res.usuario, password_temporal: res.password_temporal })));
  }

  eliminarUsuario(id: string): Observable<void> {
    return this.http
      .delete<{ ok: boolean }>(`/api/usuarios/${id}`)
      .pipe(map(() => undefined));
  }

  editarRol(id: string, rol: string): Observable<Usuario> {
    return this.http
      .patch<{ ok: boolean; usuario: Usuario }>(`/api/usuarios/${id}`, { rol })
      .pipe(map(res => res.usuario));
  }

  resetearPassword(id: string): Observable<{ password_temporal: string }> {
    return this.http
      .patch<{ ok: boolean; password_temporal: string }>(`/api/usuarios/${id}/resetear-password`, {})
      .pipe(map(res => ({ password_temporal: res.password_temporal })));
  }
}
