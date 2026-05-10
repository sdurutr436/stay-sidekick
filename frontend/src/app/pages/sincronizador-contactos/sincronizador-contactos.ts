import { Component, computed, DestroyRef, inject, OnInit, signal } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { NgIconComponent } from '@ng-icons/core';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { FormSelectComponent } from '../../components/atoms/form-select/form-select';
import { FormFieldComponent } from '../../components/molecules/form-field/form-field';
import { FormInputIconComponent } from '../../components/molecules/form-input-icon/form-input-icon';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { TarjetaEstadoComponent } from '../../components/molecules/tarjeta-estado/tarjeta-estado';
import { ModalComponent } from '../../components/organisms/modal/modal';
import { ContactosService, PREFS_CONTACTOS_DEFECTO } from '../../services/contactos.service';

interface Alerta {
  tipo: 'success' | 'error';
  mensaje: string;
}

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
    NgIconComponent,
    PageHeaderComponent,
    ButtonComponent,
    BadgeComponent,
    TarjetaEstadoComponent,
    PanelSeccionComponent,
    FormInputIconComponent,
    FormInputComponent,
    FormSelectComponent,
    FormFieldComponent,
    AlertComponent,
    ModalComponent,
  ],
})
export class SincronizadorContactosPageComponent implements OnInit {

  private readonly http             = inject(HttpClient);
  private readonly route            = inject(ActivatedRoute);
  private readonly destroyRef       = inject(DestroyRef);
  private readonly contactosService = inject(ContactosService);

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
  readonly plantillaAlerta    = signal<Alerta | null>(null);

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

  // ── Modal de instrucciones XLSX ───────────────────────────────────────────
  readonly modalInstruccionesAbierto = signal(false);

  // ── Ciclo de vida ─────────────────────────────────────────────────────────

  ngOnInit(): void {
    this.route.queryParams.pipe(takeUntilDestroyed(this.destroyRef)).subscribe(params => {
      if (params['google_conectado'] === 'true') {
        this.cargarEstadoGoogle();
      }
      if (params['google_error']) {
        console.error('[sincronizador-contactos] Error OAuth Google:', params['google_error']);
      }
    });

    this.cargarEstadoGoogle();
    this.cargarPreferencias();
    this.cargarEstadoPms();
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
      error: err => console.error('[sincronizador-contactos] Error al obtener estado Google:', err),
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
      error: err => console.error('[sincronizador-contactos] Error al obtener preferencias:', err),
    });
  }

  // ── Plantilla / formato ───────────────────────────────────────────────────

  guardarPlantilla(): void {
    this.plantillaAlerta.set(null);
    this.guardandoPlantilla.set(true);
    this.contactosService.savePreferencias({
      plantilla: this.plantillaInput(),
      formato_fecha_salida: this.formatoFechaInput(),
    }).subscribe({
      next: () => {
        this.plantillaAlerta.set({ tipo: 'success', mensaje: 'Formato guardado correctamente.' });
        this.guardandoPlantilla.set(false);
      },
      error: err => {
        this.plantillaAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al guardar el formato.' });
        this.guardandoPlantilla.set(false);
      },
    });
  }

  // ── Fechas ────────────────────────────────────────────────────────────────

  onFechaDesdeChange(valor: string): void {
    this.fechaDesde.set(valor);
  }

  onFechaHastaChange(valor: string): void {
    this.fechaHasta.set(valor);
  }

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
      },
      error: err => {
        this.syncEnCurso.set(false);
        console.error('[sincronizador-contactos] Error en sync:', err);
      },
    });
  }

  exportarCsv(): void {
    this.http.post('/api/contactos/exportacion/csv', this._parseFechasPayload(), { responseType: 'blob' }).subscribe({
      next: blob => this._descargarBlob(blob, 'contactos_google.csv'),
      error: err => console.error('[sincronizador-contactos] Error al exportar CSV:', err),
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
      },
      error: err => {
        this.xlsxEnCurso.set(false);
        console.error('[sincronizador-contactos] Error en XLSX sync:', err);
      },
    });
  }

  exportarXlsxCsv(): void {
    const archivo = this.xlsxArchivo();
    if (!archivo) return;

    const form = new FormData();
    form.append('file', archivo);

    this.http.post('/api/contactos/xlsx/exportacion/csv', form, { responseType: 'blob' }).subscribe({
      next: blob => this._descargarBlob(blob, 'contactos_google.csv'),
      error: err => console.error('[sincronizador-contactos] Error al exportar CSV desde XLSX:', err),
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
