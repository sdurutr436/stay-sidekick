import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { of } from 'rxjs';
import { catchError } from 'rxjs/operators';

import { NgIconComponent } from '@ng-icons/core';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ConfirmInlineComponent } from '../../components/molecules/confirm-inline/confirm-inline';
import { FormFieldComponent } from '../../components/molecules/form-field/form-field';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { FormSelectComponent } from '../../components/atoms/form-select/form-select';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { TablaCrudComponent } from '../../components/organisms/tabla-crud/tabla-crud';
import { ModalComponent } from '../../components/organisms/modal/modal';
import { GestionUsuariosService, EmpresaItem, Usuario } from '../../services/gestion-usuarios.service';
import { AuthService } from '../../services/auth.service';

@Component({
  selector: 'app-gestion-usuarios',
  templateUrl: './gestion-usuarios.html',
  styleUrl: './gestion-usuarios.scss',
  standalone: true,
  imports: [
    NgIconComponent,
    PageHeaderComponent,
    TablaCrudComponent,
    ModalComponent,
    AlertComponent,
    ConfirmInlineComponent,
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

  // Confirmación de borrado
  readonly confirmandoId = signal<string | null>(null);
  readonly eliminando = signal(false);

  // Reset de contraseña
  readonly resetandoId = signal<string | null>(null);
  readonly resetInfo = signal<{ id: string; password: string } | null>(null);

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

  pedirEliminar(id: string): void {
    this.confirmandoId.set(id);
    this.resetInfo.set(null);
  }

  cancelarEliminar(): void {
    this.confirmandoId.set(null);
  }

  confirmarEliminar(): void {
    const id = this.confirmandoId();
    if (!id) return;
    this.eliminando.set(true);
    this.service.eliminarUsuario(id, this._empresaIdActual()).subscribe({
      next: () => {
        this.eliminando.set(false);
        this.confirmandoId.set(null);
        this._cargar(this._empresaIdActual());
      },
      error: () => {
        this.eliminando.set(false);
        this.confirmandoId.set(null);
      },
    });
  }

  resetearPassword(id: string): void {
    this.resetandoId.set(id);
    this.resetInfo.set(null);
    this.service.resetearPassword(id, this._empresaIdActual()).subscribe({
      next: ({ password_temporal }) => {
        this.resetandoId.set(null);
        this.resetInfo.set({ id, password: password_temporal });
      },
      error: () => {
        this.resetandoId.set(null);
      },
    });
  }

  copiar(text: string): void {
    navigator.clipboard.writeText(text);
  }

  cerrarResetInfo(): void {
    this.resetInfo.set(null);
  }

  rolLabel(rol: string): string {
    return rol === 'admin' ? 'Admin' : 'Empleado';
  }
}
