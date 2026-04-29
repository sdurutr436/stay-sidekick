import { Component, inject, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { PerfilService, IntegracionesData } from '../../services/perfil.service';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormFieldComponent } from '../../components/molecules/form-field/form-field';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { FormSelectComponent } from '../../components/atoms/form-select/form-select';

interface Alerta {
  tipo: 'success' | 'error';
  mensaje: string;
}

@Component({
  selector: 'app-perfil-page',
  templateUrl: './perfil.html',
  standalone: true,
  imports: [
    PageHeaderComponent,
    PanelSeccionComponent,
    AlertComponent,
    ButtonComponent,
    FormFieldComponent,
    FormInputComponent,
    FormSelectComponent,
  ],
})
export class PerfilPageComponent implements OnInit {
  readonly auth    = inject(AuthService);
  readonly service = inject(PerfilService);
  private  readonly http  = inject(HttpClient);
  private  readonly route = inject(ActivatedRoute);

  readonly email             = signal('');
  readonly passwordChangedAt = signal<string | null>(null);
  readonly isAdmin           = signal(false);
  readonly integraciones     = signal<IntegracionesData | null>(null);

  // Cambiar contraseña
  readonly passwordActual    = signal('');
  readonly passwordNueva     = signal('');
  readonly passwordConfirm   = signal('');
  readonly passwordGuardando = signal(false);
  readonly passwordAlerta    = signal<Alerta | null>(null);

  // PMS
  readonly pmsProveedor  = signal('');
  readonly pmsApiKey     = signal('');
  readonly pmsGuardando  = signal(false);
  readonly pmsAlerta     = signal<Alerta | null>(null);

  // IA
  readonly iaProveedor  = signal('');
  readonly iaModelo     = signal('');
  readonly iaApiKey     = signal('');
  readonly iaGuardando  = signal(false);
  readonly iaAlerta     = signal<Alerta | null>(null);

  // Google
  readonly googleGuardando = signal(false);
  readonly googleAlerta    = signal<Alerta | null>(null);

  readonly pmsOpciones = [
    { value: 'smoobu',    label: 'Smoobu'    },
    { value: 'beds24',    label: 'Beds24'    },
    { value: 'hostaway',  label: 'Hostaway'  },
    { value: 'cloudbeds', label: 'Cloudbeds' },
  ];

  readonly iaOpciones = [
    { value: 'default', label: 'Sistema (Gemini compartido)'  },
    { value: 'gemini',  label: 'Gemini (API propia)'          },
    { value: 'openai',  label: 'OpenAI'                       },
    { value: 'claude',  label: 'Claude (Anthropic)'           },
  ];

  ngOnInit(): void {
    this.isAdmin.set(this.auth.isAdmin());

    this.service.getPerfil().subscribe({
      next: res => {
        this.email.set(res.data.email);
        this.passwordChangedAt.set(res.data.password_changed_at);
      },
    });

    this.cargarIntegraciones();

    this.route.queryParamMap.subscribe(params => {
      if (params.get('google_conectado') === 'true') {
        this.googleAlerta.set({ tipo: 'success', mensaje: 'Google Contacts conectado correctamente.' });
        this.cargarIntegraciones();
      }
      const err = params.get('google_error');
      if (err) {
        const mensajes: Record<string, string> = {
          acceso_denegado: 'Acceso denegado por Google.',
          estado_invalido: 'Error de seguridad en el proceso OAuth. Inténtalo de nuevo.',
          codigo_invalido: 'Código OAuth inválido.',
          token_fallido:   'No se pudieron obtener los tokens de Google.',
        };
        this.googleAlerta.set({ tipo: 'error', mensaje: mensajes[err] ?? 'Error al conectar con Google.' });
      }
    });
  }

  diasDesdeUltimoCambio(): number | null {
    const at = this.passwordChangedAt();
    if (!at) return null;
    return Math.floor((Date.now() - new Date(at).getTime()) / 86_400_000);
  }

  guardarPassword(): void {
    this.passwordAlerta.set(null);

    if (this.passwordNueva() !== this.passwordConfirm()) {
      this.passwordAlerta.set({ tipo: 'error', mensaje: 'Las contraseñas nuevas no coinciden.' });
      return;
    }

    this.passwordGuardando.set(true);
    this.service.cambiarPassword(this.passwordActual(), this.passwordNueva()).subscribe({
      next: res => {
        if (res.ok) {
          this.passwordAlerta.set({ tipo: 'success', mensaje: 'Contraseña actualizada correctamente.' });
          this.passwordActual.set('');
          this.passwordNueva.set('');
          this.passwordConfirm.set('');
          this.passwordChangedAt.set(new Date().toISOString());
        } else {
          this.passwordAlerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al cambiar la contraseña.' });
        }
        this.passwordGuardando.set(false);
      },
      error: err => {
        const msg = err?.error?.errors?.[0] ?? 'Error al cambiar la contraseña.';
        this.passwordAlerta.set({ tipo: 'error', mensaje: msg });
        this.passwordGuardando.set(false);
      },
    });
  }

  guardarPMS(): void {
    this.pmsAlerta.set(null);
    this.pmsGuardando.set(true);
    this.service.actualizarPMS(this.pmsProveedor(), this.pmsApiKey()).subscribe({
      next: res => {
        if (res.ok) {
          this.pmsAlerta.set({ tipo: 'success', mensaje: 'Integración PMS guardada.' });
          this.pmsApiKey.set('');
          this.cargarIntegraciones();
        } else {
          this.pmsAlerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al guardar el PMS.' });
        }
        this.pmsGuardando.set(false);
      },
      error: err => {
        this.pmsAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar el PMS.' });
        this.pmsGuardando.set(false);
      },
    });
  }

  guardarIA(): void {
    this.iaAlerta.set(null);
    this.iaGuardando.set(true);
    this.service.actualizarIA(this.iaProveedor(), this.iaModelo(), this.iaApiKey() || undefined).subscribe({
      next: res => {
        if (res.ok) {
          this.iaAlerta.set({ tipo: 'success', mensaje: 'Configuración de IA guardada.' });
          this.iaApiKey.set('');
          this.cargarIntegraciones();
        } else {
          this.iaAlerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al guardar la IA.' });
        }
        this.iaGuardando.set(false);
      },
      error: err => {
        this.iaAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar la IA.' });
        this.iaGuardando.set(false);
      },
    });
  }

  conectarGoogle(): void {
    this.googleAlerta.set(null);
    this.googleGuardando.set(true);
    const headers = { Authorization: `Bearer ${this.auth.getToken() ?? ''}` };
    this.http.get<{ ok: boolean; url: string }>('/api/contactos/google/auth', { headers }).subscribe({
      next: res => {
        if (res.url) window.location.href = res.url;
        else this.googleGuardando.set(false);
      },
      error: err => {
        this.googleAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al iniciar la conexión con Google.' });
        this.googleGuardando.set(false);
      },
    });
  }

  desconectarGoogle(): void {
    this.googleAlerta.set(null);
    this.googleGuardando.set(true);
    const headers = { Authorization: `Bearer ${this.auth.getToken() ?? ''}` };
    this.http.delete<{ ok: boolean }>('/api/contactos/google/conexion', { headers }).subscribe({
      next: () => {
        this.googleAlerta.set({ tipo: 'success', mensaje: 'Google Contacts desconectado.' });
        this.cargarIntegraciones();
        this.googleGuardando.set(false);
      },
      error: err => {
        this.googleAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al desconectar Google.' });
        this.googleGuardando.set(false);
      },
    });
  }

  cerrarSesion(): void {
    this.auth.logout();
  }

  private cargarIntegraciones(): void {
    this.service.getIntegraciones().subscribe({
      next: res => {
        this.integraciones.set(res.data);
        this.pmsProveedor.set(res.data.pms.proveedor ?? '');
        this.iaProveedor.set(res.data.ia.proveedor ?? 'default');
        this.iaModelo.set(res.data.ia.modelo ?? '');
      },
    });
  }
}
