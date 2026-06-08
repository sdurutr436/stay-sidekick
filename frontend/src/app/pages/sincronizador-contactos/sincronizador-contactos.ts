import { AfterViewInit, Component, computed, DestroyRef, ElementRef, inject, OnDestroy, OnInit, signal, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute, RouterLink } from '@angular/router';
import flatpickr from 'flatpickr';
import { NgIconComponent } from '@ng-icons/core';
import { ButtonComponent } from '../../components/atoms/button/button';
import { TagComponent } from '../../components/atoms/tag/tag';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { FormSelectComponent } from '../../components/atoms/form-select/form-select';
import { FormFieldComponent } from '../../components/molecules/form-field/form-field';
import { HowItWorksButtonComponent } from '../../components/molecules/how-it-works-button/how-it-works-button';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { ContactosService, PREFS_CONTACTOS_DEFECTO } from '../../services/contactos.service';
import { ToastService } from '../../services/toast.service';

interface SyncResultado {
  total: number;
  nuevos: number;
  actualizados: number;
  advertencias?: string[];
}

const _FECHA_PREVIEW: Record<string, string> = {
  YYMMDD:     '260101',
  YYYYMMDD:   '20260101',
  'DD/MM/YYYY': '01/01/2026',
  'DD/MM/YY':   '01/01/26',
  'MM/DD/YYYY': '01/01/2026',
  'DD-MM-YYYY': '01-01-2026',
};

@Component({
  selector: 'app-sincronizador-contactos',
  templateUrl: './sincronizador-contactos.html',
  styleUrl: './sincronizador-contactos.scss',
  standalone: true,
  imports: [
    RouterLink,
    NgIconComponent,
    PageHeaderComponent,
    ButtonComponent,
    TagComponent,
    PanelSeccionComponent,
    FormInputComponent,
    FormSelectComponent,
    FormFieldComponent,
    HowItWorksButtonComponent,
  ],
})
export class SincronizadorContactosPageComponent implements OnInit, AfterViewInit, OnDestroy {

  private readonly http             = inject(HttpClient);
  private readonly route            = inject(ActivatedRoute);
  private readonly destroyRef       = inject(DestroyRef);
  private readonly contactosService = inject(ContactosService);
  private readonly toast            = inject(ToastService);

  // ── Estado PMS ──────────────────────────────────────────────────────────
  readonly pmsConectado = signal(false);

  // ── Estado Google ─────────────────────────────────────────────────────────
  readonly googleConectado = signal(false);
  readonly ultimoSync = signal<string | null>(null);
  readonly syncEnCurso = signal(false);

  // ── XLSX ──────────────────────────────────────────────────────────────────
  readonly xlsxArchivo = signal<File | null>(null);
  readonly xlsxEnCurso = signal(false);

  // ── Fechas ────────────────────────────────────────────────────────────────
  readonly fechaDesde = signal('');
  readonly fechaHasta = signal('');

  @ViewChild('inputDesde') private readonly inputDesdeRef?: ElementRef<HTMLInputElement>;
  @ViewChild('inputHasta') private readonly inputHastaRef?: ElementRef<HTMLInputElement>;

  private _pickerDesde?: flatpickr.Instance;
  private _pickerHasta?: flatpickr.Instance;

  readonly fechasValidas = computed(() => {
    const desde = this.fechaDesde();
    const hasta = this.fechaHasta();
    if (!desde || !hasta) return false;
    const re = /^\d{2}\/\d{2}\/\d{4}$/;
    return re.test(desde) && re.test(hasta);
  });

  // ── Nuevos contactos (resultado de última operación) ─────────────────────
  readonly nuevosContactos = signal(0);

  // ── Plantilla / formato ───────────────────────────────────────────────────
  readonly plantillaInput    = signal(PREFS_CONTACTOS_DEFECTO.plantilla);
  readonly formatoFechaInput = signal(PREFS_CONTACTOS_DEFECTO.formato_fecha_salida);
  readonly separadorApt      = signal(PREFS_CONTACTOS_DEFECTO.separador_apt);
  readonly guardandoPlantilla = signal(false);

  readonly previewNombre = computed(() => {
    const plantilla = this.plantillaInput();
    const formato   = this.formatoFechaInput();
    const sep       = this.separadorApt();
    const fecha     = _FECHA_PREVIEW[formato] ?? '260101';
    return plantilla
      .replace('{FECHA}', fecha)
      .replace('{APT}', `Cádiz Espiral Marítima`)
      .replace('{NOMBRE}', 'Manolito Fernandez Ruiz');
  });

  readonly formatoFechaOpciones = [
    { value: 'YYMMDD',     label: 'YYMMDD — ej. 260101'    },
    { value: 'YYYYMMDD',   label: 'YYYYMMDD — ej. 20260101' },
    { value: 'DD/MM/YYYY', label: 'DD/MM/YYYY'               },
    { value: 'DD/MM/YY',   label: 'DD/MM/YY'                 },
    { value: 'MM/DD/YYYY', label: 'MM/DD/YYYY'               },
    { value: 'DD-MM-YYYY', label: 'DD-MM-YYYY'               },
  ];

  // ── Ciclo de vida ─────────────────────────────────────────────────────────

  ngOnInit(): void {
    this.route.queryParams.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
      if (params['google_conectado'] === 'true') {
        this.cargarEstadoGoogle();
      }
      if (params['google_error']) {
        const mensajes: Record<string, string> = {
          acceso_denegado: 'Acceso denegado por Google.',
          estado_invalido: 'Error de seguridad en el proceso OAuth. Inténtalo de nuevo.',
          codigo_invalido: 'Código OAuth inválido.',
          token_fallido:   'No se pudieron obtener los tokens de Google.',
        };
        this.toast.showError(mensajes[params['google_error']] ?? 'Error al conectar con Google.');
      }
    });

    this.cargarEstadoGoogle();
    this.cargarPreferencias();
    this.cargarEstadoPms();
  }

  ngAfterViewInit(): void {
    // Mismo selector visual (flatpickr) que el Mapa de calor, manteniendo el
    // formato DD/MM/YYYY que valida y parsea esta página.
    const baseConfig = { dateFormat: 'd/m/Y', locale: { firstDayOfWeek: 1 } };

    if (this.inputDesdeRef) {
      this._pickerDesde = flatpickr(this.inputDesdeRef.nativeElement, {
        ...baseConfig,
        onChange: ([date], dateStr) => {
          this.fechaDesde.set(dateStr);
          if (date) this._pickerHasta?.set('minDate', date);
        },
      }) as flatpickr.Instance;
    }

    if (this.inputHastaRef) {
      this._pickerHasta = flatpickr(this.inputHastaRef.nativeElement, {
        ...baseConfig,
        onChange: (_dates, dateStr) => this.fechaHasta.set(dateStr),
      }) as flatpickr.Instance;
    }
  }

  ngOnDestroy(): void {
    this._pickerDesde?.destroy();
    this._pickerHasta?.destroy();
  }

  // ── Carga inicial ─────────────────────────────────────────────────────────

  private cargarEstadoGoogle(): void {
    this.http.get<{ ok: boolean; google: { conectado: boolean; ultimo_sync?: string } }>(
      '/api/contactos/google/status'
    ).subscribe({
      next: res => {
        this.googleConectado.set(res.google.conectado);
        this.ultimoSync.set(res.google.ultimo_sync ?? null);
      },
      error: () => this.toast.showError('Error al obtener el estado de Google Contacts.'),
    });
  }

  private cargarEstadoPms(): void {
    this.http.get<{ ok: boolean; config: { proveedor: string } | null }>(
      '/api/apartamentos/pms'
    ).subscribe({
      next: res => this.pmsConectado.set(res.config !== null),
      error: () => this.pmsConectado.set(false),
    });
  }

  private cargarPreferencias(): void {
    this.contactosService.getPreferencias().subscribe({
      next: prefs => {
        this.plantillaInput.set(prefs.plantilla);
        this.formatoFechaInput.set(prefs.formato_fecha_salida);
        this.separadorApt.set(prefs.separador_apt);
      },
      error: () => this.toast.showError('Error al cargar las preferencias.'),
    });
  }

  // ── Plantilla / formato ───────────────────────────────────────────────────

  guardarPlantilla(): void {
    this.guardandoPlantilla.set(true);
    this.contactosService.savePreferencias({
      plantilla: this.plantillaInput(),
      formato_fecha_salida: this.formatoFechaInput(),
    }).subscribe({
      next: () => {
        this.guardandoPlantilla.set(false);
        this.toast.showSuccess('Formato guardado correctamente.');
      },
      error: err => {
        this.guardandoPlantilla.set(false);
        this.toast.showError(err?.error?.errors?.[0] ?? 'Error al guardar el formato.');
      },
    });
  }

  // ── Fechas ────────────────────────────────────────────────────────────────

  private _parseFechasPayload(): { desde?: string; hasta?: string } {
    const desde = this.fechaDesde();
    const hasta = this.fechaHasta();
    const payload: { desde?: string; hasta?: string } = {};
    if (desde) {
      const [d, m, y] = desde.split('/');
      payload.desde = `${y}-${m}-${d}`;
    }
    if (hasta) {
      const [d, m, y] = hasta.split('/');
      payload.hasta = `${y}-${m}-${d}`;
    }
    return payload;
  }

  // ── Sincronización (fuente: PMS API) ──────────────────────────────────────

  lanzarSync(): void {
    if (this.syncEnCurso()) return;
    this.syncEnCurso.set(true);

    this.http.post<{ ok: boolean; resultado: SyncResultado }>(
      '/api/contactos/sincronizacion',
      this._parseFechasPayload(),
    ).subscribe({
      next: res => {
        this.syncEnCurso.set(false);
        this.ultimoSync.set(new Date().toISOString());
        this.nuevosContactos.set(res.resultado.nuevos);
        this.toast.showSuccess(
          `Sincronización con Google completada: ${res.resultado.nuevos} nuevos, ${res.resultado.actualizados} actualizados.`,
        );
      },
      error: err => {
        this.syncEnCurso.set(false);
        this.toast.showError(err?.error?.errors?.[0] ?? 'Error durante la sincronización.');
      },
    });
  }

  exportarCsv(): void {
    this.http.post('/api/contactos/exportacion/csv', this._parseFechasPayload(), { responseType: 'blob' }).subscribe({
      next: blob => {
        this._descargarBlob(blob, 'contactos_google.csv');
        this.toast.showSuccess('CSV generado correctamente.');
      },
      error: err => this.toast.showError(err?.error?.errors?.[0] ?? 'Error al exportar el CSV.'),
    });
  }

  // ── XLSX ──────────────────────────────────────────────────────────────────

  onXlsxSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.xlsxArchivo.set(file);
    input.value = '';
  }

  lanzarXlsxSync(): void {
    const archivo = this.xlsxArchivo();
    if (!archivo || this.xlsxEnCurso()) return;

    this.xlsxEnCurso.set(true);
    const form = new FormData();
    form.append('file', archivo);

    this.http.post<{ ok: boolean; resultado: SyncResultado }>(
      '/api/contactos/xlsx/sincronizacion',
      form,
    ).subscribe({
      next: res => {
        this.xlsxEnCurso.set(false);
        this.ultimoSync.set(new Date().toISOString());
        this.nuevosContactos.set(res.resultado.nuevos);
        this.toast.showSuccess(
          `Sincronización con Google completada: ${res.resultado.nuevos} nuevos, ${res.resultado.actualizados} actualizados.`,
        );
      },
      error: err => {
        this.xlsxEnCurso.set(false);
        this.toast.showError(err?.error?.errors?.[0] ?? 'Error durante la sincronización del XLSX.');
      },
    });
  }

  exportarXlsxCsv(): void {
    const archivo = this.xlsxArchivo();
    if (!archivo) return;

    const form = new FormData();
    form.append('file', archivo);

    this.http.post('/api/contactos/xlsx/exportacion/csv', form, { responseType: 'blob' }).subscribe({
      next: blob => {
        this._descargarBlob(blob, 'contactos_google.csv');
        this.toast.showSuccess('CSV generado correctamente.');
      },
      error: err => this.toast.showError(err?.error?.errors?.[0] ?? 'Error al exportar el CSV desde XLSX.'),
    });
  }

  // ── Utilidades ────────────────────────────────────────────────────────────

  private _descargarBlob(blob: Blob, nombreFichero: string): void {
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nombreFichero;
    a.click();
    URL.revokeObjectURL(url);
  }
}
