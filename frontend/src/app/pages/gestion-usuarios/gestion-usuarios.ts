import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { NgIconComponent } from '@ng-icons/core';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ConfirmInlineComponent } from '../../components/molecules/confirm-inline/confirm-inline';
import { FormCheckboxComponent } from '../../components/atoms/form-checkbox/form-checkbox';
import { FormFieldComponent } from '../../components/molecules/form-field/form-field';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { FormSelectComponent } from '../../components/atoms/form-select/form-select';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { TablaCrudComponent } from '../../components/organisms/tabla-crud/tabla-crud';
import { ModalComponent } from '../../components/organisms/modal/modal';
import { GestionUsuariosService, EmpresaItem, Usuario, EmpresaCreatePayload } from '../../services/gestion-usuarios.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-gestion-usuarios',
  templateUrl: './gestion-usuarios.html',
  styleUrl: './gestion-usuarios.scss',
  standalone: true,
  imports: [
    RouterLink,
    NgIconComponent,
    PageHeaderComponent,
    TablaCrudComponent,
    ModalComponent,
    AlertComponent,
    ConfirmInlineComponent,
    FormCheckboxComponent,
    FormFieldComponent,
    BadgeComponent,
    ButtonComponent,
    FormInputComponent,
    FormSelectComponent,
  ],
})
export class GestionUsuariosPageComponent implements OnInit {
  private readonly service = inject(GestionUsuariosService);
  private readonly auth = inject(AuthService);

  readonly esSuperAdmin = this.auth.esSuperAdmin;

  readonly empresas = signal<EmpresaItem[]>([]);
  readonly empresaSeleccionadaId = signal<string>('');

  readonly usuarios = signal<Usuario[]>([]);
  readonly maxUsuarios = signal(4);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);

  // Modal de creación
  readonly modalAbierto = signal(false);
  readonly nuevoEmail = signal('');
  readonly nuevoRol = signal('operativo');
  readonly creando = signal(false);
  readonly errorCreacion = signal<string | null>(null);
  readonly passwordTemporal = signal<string | null>(null);

  // Modal de edición de usuario
  readonly usuarioEditando = signal<Usuario | null>(null);
  readonly modalEdicionAbierto = signal(false);
  readonly editRol = signal<string>('operativo');
  readonly guardando = signal(false);
  readonly errorEdicion = signal<string | null>(null);
  readonly resetInfoEdicion = signal<string | null>(null);
  readonly resetandoEnEdicion = signal(false);
  readonly confirmandoEliminarEdicion = signal(false);
  readonly eliminandoEdicion = signal(false);

  // Modal de nueva empresa (solo superadmin)
  readonly modalEmpresaAbierto = signal(false);
  readonly nuevaEmpresaNombre = signal('');
  readonly nuevaEmpresaEmail = signal('');
  readonly creandoEmpresa = signal(false);
  readonly errorCreacionEmpresa = signal<string | null>(null);

  readonly totalUsuarios = computed(() => this.usuarios().length);
  readonly limiteAlcanzado = computed(() => this.totalUsuarios() >= this.maxUsuarios());

  readonly rolesOpciones = [
    { value: 'operativo', label: 'Empleado' },
    { value: 'admin', label: 'Administrador' },
  ];

  readonly empresasOpciones = computed(() =>
    this.empresas().map(e => ({ value: e.id, label: `${e.nombre} (${e.email})` }))
  );

  ngOnInit(): void {
    if (this.esSuperAdmin) {
      this.service.getEmpresas().pipe(catchError(() => of([] as EmpresaItem[]))).subscribe(empresas => {
        this.empresas.set(empresas);
        if (empresas.length > 0) {
          this.empresaSeleccionadaId.set(empresas[0].id);
          this._cargar(empresas[0].id);
        } else {
          this.cargando.set(false);
        }
      });
    } else {
      this._cargar();
    }
  }

  onEmpresaChange(id: string): void {
    this.empresaSeleccionadaId.set(id);
    this._cargar(id);
  }

  private _cargar(empresaId?: string): void {
    this.cargando.set(true);
    this.error.set(null);
    this.service.getUsuarios(empresaId).subscribe({
      next: ({ usuarios, max_usuarios }) => {
        this.usuarios.set(usuarios);
        this.maxUsuarios.set(max_usuarios);
        this.cargando.set(false);
      },
      error: () => {
        this.error.set('No se pudieron cargar los usuarios. Inténtalo de nuevo.');
        this.cargando.set(false);
      },
    });
  }

  private _empresaIdActual(): string | undefined {
    return this.esSuperAdmin ? this.empresaSeleccionadaId() || undefined : undefined;
  }

  abrirModal(): void {
    this.nuevoEmail.set('');
    this.nuevoRol.set('operativo');
    this.errorCreacion.set(null);
    this.passwordTemporal.set(null);
    this.modalAbierto.set(true);
  }

  cerrarModal(): void {
    this.modalAbierto.set(false);
    this.passwordTemporal.set(null);
  }

  crear(): void {
    const email = this.nuevoEmail().trim();
    if (!email) {
      this.errorCreacion.set('El correo electrónico es obligatorio.');
      return;
    }
    this.creando.set(true);
    this.errorCreacion.set(null);
    this.service.crearUsuario({ email, rol: this.nuevoRol() }, this._empresaIdActual()).subscribe({
      next: ({ password_temporal }) => {
        this.creando.set(false);
        this.passwordTemporal.set(password_temporal);
        this._cargar(this._empresaIdActual());
      },
      error: err => {
        this.creando.set(false);
        this.errorCreacion.set(err?.error?.errors?.[0] ?? 'Error al crear el usuario.');
      },
    });
  }

  abrirEdicion(u: Usuario): void {
    this.usuarioEditando.set(u);
    this.editRol.set(u.rol);
    this.errorEdicion.set(null);
    this.resetInfoEdicion.set(null);
    this.confirmandoEliminarEdicion.set(false);
    this.modalEdicionAbierto.set(true);
  }

  cerrarEdicion(): void {
    this.modalEdicionAbierto.set(false);
    this.usuarioEditando.set(null);
    this.resetInfoEdicion.set(null);
    this.confirmandoEliminarEdicion.set(false);
  }

  guardarEdicion(): void {
    const u = this.usuarioEditando();
    if (!u) return;
    this.guardando.set(true);
    this.errorEdicion.set(null);
    this.service.editarRol(u.id, this.editRol(), this._empresaIdActual()).subscribe({
      next: (updated) => {
        this.guardando.set(false);
        this.usuarios.update(lista => lista.map(x => x.id === updated.id ? updated : x));
        this.cerrarEdicion();
      },
      error: err => {
        this.guardando.set(false);
        this.errorEdicion.set(err?.error?.errors?.[0] ?? 'Error al guardar.');
      },
    });
  }

  resetearPasswordEdicion(): void {
    const u = this.usuarioEditando();
    if (!u) return;
    this.resetandoEnEdicion.set(true);
    this.resetInfoEdicion.set(null);
    this.service.resetearPassword(u.id, this._empresaIdActual()).subscribe({
      next: ({ password_temporal }) => {
        this.resetandoEnEdicion.set(false);
        this.resetInfoEdicion.set(password_temporal);
      },
      error: () => { this.resetandoEnEdicion.set(false); },
    });
  }

  confirmarEliminarEdicion(): void {
    const u = this.usuarioEditando();
    if (!u) return;
    this.eliminandoEdicion.set(true);
    this.service.eliminarUsuario(u.id, this._empresaIdActual()).subscribe({
      next: () => {
        this.eliminandoEdicion.set(false);
        this._cargar(this._empresaIdActual());
        this.cerrarEdicion();
      },
      error: () => { this.eliminandoEdicion.set(false); },
    });
  }

  copiar(text: string): void {
    navigator.clipboard.writeText(text);
  }

  rolLabel(rol: string): string {
    return rol === 'admin' ? 'Admin' : 'Empleado';
  }

  abrirModalEmpresa(): void {
    this.nuevaEmpresaNombre.set('');
    this.nuevaEmpresaEmail.set('');
    this.errorCreacionEmpresa.set(null);
    this.modalEmpresaAbierto.set(true);
  }

  cerrarModalEmpresa(): void {
    this.modalEmpresaAbierto.set(false);
  }

  crearEmpresa(): void {
    const nombre = this.nuevaEmpresaNombre().trim();
    const email = this.nuevaEmpresaEmail().trim();
    if (!nombre) { this.errorCreacionEmpresa.set('El nombre es obligatorio.'); return; }
    if (!email) { this.errorCreacionEmpresa.set('El email es obligatorio.'); return; }
    this.creandoEmpresa.set(true);
    this.errorCreacionEmpresa.set(null);
    this.service.crearEmpresa({ nombre, email }).subscribe({
      next: (empresa) => {
        this.creandoEmpresa.set(false);
        this.modalEmpresaAbierto.set(false);
        this.empresas.update(lista => [...lista, empresa]);
        this.empresaSeleccionadaId.set(empresa.id);
        this._cargar(empresa.id);
      },
      error: err => {
        this.creandoEmpresa.set(false);
        this.errorCreacionEmpresa.set(err?.error?.errors?.[0] ?? 'Error al crear la empresa.');
      },
    });
  }
}
