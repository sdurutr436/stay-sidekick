import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from '../../services/auth.service';
import { PerfilService, IntegracionesData } from '../../services/perfil.service';
import { ApartamentosService } from '../../services/apartamentos.service';
import { ContactosService } from '../../services/contactos.service';
import { MapaCalorService, UmbralesCalor } from '../../services/mapa-calor.service';
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
  private  readonly aptService        = inject(ApartamentosService);
  private  readonly contactosService  = inject(ContactosService);
  private  readonly mapaCalorService  = inject(MapaCalorService);
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

  // XLSX — Configuración de columnas (maestro de apartamentos)
  readonly xlsxColIdExterno = signal(0);
  readonly xlsxColNombre    = signal(0);
  readonly xlsxColDireccion = signal(0);
  readonly xlsxColCiudad    = signal(0);
  readonly xlsxGuardando    = signal(false);
  readonly xlsxAlerta       = signal<Alerta | null>(null);

  // XLSX — Configuración de columnas (reservas de contactos)
  readonly xlsxRColCheckin   = signal(0);
  readonly xlsxRColNombre    = signal(0);
  readonly xlsxRColTipologia = signal(0);
  readonly xlsxRColTelefono  = signal(0);
  readonly xlsxReservasGuardando = signal(false);
  readonly xlsxReservasAlerta    = signal<Alerta | null>(null);

  // Mapa de calor — Columnas XLSX
  readonly heatmapColCheckin  = signal('');
  readonly heatmapColCheckout = signal('');
  readonly heatmapXlsxGuardando = signal(false);
  readonly heatmapXlsxAlerta    = signal<Alerta | null>(null);

  // Mapa de calor — Umbrales de color
  readonly heatmapUmbrales          = signal<UmbralesCalor>({ nivel1: 10, nivel2: 20, nivel3: 30 });
  readonly heatmapUmbralesGuardando = signal(false);
  readonly heatmapUmbralesAlerta    = signal<Alerta | null>(null);

  readonly heatmapUmbralesError = computed(() => {
    const u = this.heatmapUmbrales();
    if (u.nivel1 <= 0 || u.nivel2 <= 0 || u.nivel3 <= 0) return 'Los tres niveles deben ser enteros positivos.';
    if (!(u.nivel1 < u.nivel2 && u.nivel2 < u.nivel3)) return 'Debe cumplirse: Nivel 1 < Nivel 2 < Nivel 3.';
    return null;
  });

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
    this.isAdmin.set(this.auth.isAdmin);

    this.service.getPerfil().subscribe({
      next: res => {
        this.email.set(res.data.email);
        this.passwordChangedAt.set(res.data.password_changed_at);
      },
    });

    this.cargarIntegraciones();
    this.cargarXlsxColumnas();
    this.cargarXlsxReservasColumnas();
    this.cargarHeatmapXlsxColumnas();
    this.cargarHeatmapUmbrales();

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

  guardarXlsxColumnas(): void {
    this.xlsxAlerta.set(null);
    this.xlsxGuardando.set(true);
    this.aptService.saveXlsxColumnas({
      col_id_externo: this.xlsxColIdExterno(),
      col_nombre:     this.xlsxColNombre(),
      col_direccion:  this.xlsxColDireccion(),
      col_ciudad:     this.xlsxColCiudad(),
    }).subscribe({
      next: () => {
        this.xlsxAlerta.set({ tipo: 'success', mensaje: 'Configuración de columnas guardada.' });
        this.xlsxGuardando.set(false);
      },
      error: err => {
        this.xlsxAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar la configuración.' });
        this.xlsxGuardando.set(false);
      },
    });
  }

  guardarXlsxReservasColumnas(): void {
    this.xlsxReservasAlerta.set(null);
    this.xlsxReservasGuardando.set(true);
    this.contactosService.savePreferencias({
      xlsx_reservas: {
        col_checkin:   this.xlsxRColCheckin(),
        col_nombre:    this.xlsxRColNombre(),
        col_tipologia: this.xlsxRColTipologia(),
        col_telefono:  this.xlsxRColTelefono(),
      },
    }).subscribe({
      next: () => {
        this.xlsxReservasAlerta.set({ tipo: 'success', mensaje: 'Configuración de columnas guardada.' });
        this.xlsxReservasGuardando.set(false);
      },
      error: err => {
        this.xlsxReservasAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar la configuración.' });
        this.xlsxReservasGuardando.set(false);
      },
    });
  }

  guardarHeatmapXlsxColumnas(): void {
    this.heatmapXlsxAlerta.set(null);
    this.heatmapXlsxGuardando.set(true);
    this.mapaCalorService.saveConfigXlsx({
      col_fecha_checkin:  this.heatmapColCheckin() || null,
      col_fecha_checkout: this.heatmapColCheckout() || null,
    }).subscribe({
      next: () => {
        this.heatmapXlsxAlerta.set({ tipo: 'success', mensaje: 'Configuración de columnas guardada.' });
        this.heatmapXlsxGuardando.set(false);
      },
      error: err => {
        this.heatmapXlsxAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar la configuración.' });
        this.heatmapXlsxGuardando.set(false);
      },
    });
  }

  guardarHeatmapUmbrales(): void {
    this.heatmapUmbralesAlerta.set(null);
    this.heatmapUmbralesGuardando.set(true);
    this.mapaCalorService.saveUmbrales(this.heatmapUmbrales()).subscribe({
      next: () => {
        this.heatmapUmbralesAlerta.set({ tipo: 'success', mensaje: 'Umbrales de color guardados.' });
        this.heatmapUmbralesGuardando.set(false);
      },
      error: err => {
        this.heatmapUmbralesAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar los umbrales.' });
        this.heatmapUmbralesGuardando.set(false);
      },
    });
  }

  cerrarSesion(): void {
    this.auth.logout();
  }

  private cargarXlsxColumnas(): void {
    this.aptService.getXlsxColumnas().subscribe({
      next: config => {
        if (config) {
          this.xlsxColIdExterno.set(config.col_id_externo ?? 0);
          this.xlsxColNombre.set(config.col_nombre ?? 0);
          this.xlsxColDireccion.set(config.col_direccion ?? 0);
          this.xlsxColCiudad.set(config.col_ciudad ?? 0);
        }
      },
    });
  }

  private cargarXlsxReservasColumnas(): void {
    this.contactosService.getPreferencias().subscribe({
      next: prefs => {
        this.xlsxRColCheckin.set(prefs.xlsx_reservas?.col_checkin ?? 0);
        this.xlsxRColNombre.set(prefs.xlsx_reservas?.col_nombre ?? 0);
        this.xlsxRColTipologia.set(prefs.xlsx_reservas?.col_tipologia ?? 0);
        this.xlsxRColTelefono.set(prefs.xlsx_reservas?.col_telefono ?? 0);
      },
    });
  }

  private cargarHeatmapXlsxColumnas(): void {
    this.mapaCalorService.getConfigXlsx().subscribe({
      next: config => {
        if (config) {
          this.heatmapColCheckin.set(config.col_fecha_checkin ?? '');
          this.heatmapColCheckout.set(config.col_fecha_checkout ?? '');
        }
      },
    });
  }

  private cargarHeatmapUmbrales(): void {
    this.mapaCalorService.getUmbrales().subscribe({
      next: u => this.heatmapUmbrales.set(u),
    });
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
