import { Component, OnInit, computed, inject, signal } from '@angular/core';

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
import { GestionUsuariosService, Usuario } from '../../services/gestion-usuarios.service';

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

  ngOnInit(): void {
    this._cargar();
  }

  private _cargar(): void {
    this.cargando.set(true);
    this.error.set(null);
    this.service.getUsuarios().subscribe({
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
    this.service.crearUsuario({ email, rol: this.nuevoRol() }).subscribe({
      next: ({ password_temporal }) => {
        this.creando.set(false);
        this.passwordTemporal.set(password_temporal);
        this._cargar();
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
    this.service.eliminarUsuario(id).subscribe({
      next: () => {
        this.eliminando.set(false);
        this.confirmandoId.set(null);
        this._cargar();
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
    this.service.resetearPassword(id).subscribe({
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
