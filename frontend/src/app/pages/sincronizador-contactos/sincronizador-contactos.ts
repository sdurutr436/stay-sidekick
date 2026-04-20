import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormInputIconComponent } from '../../components/molecules/form-input-icon/form-input-icon';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { TarjetaEstadoComponent } from '../../components/molecules/tarjeta-estado/tarjeta-estado';

type FormatoNombre = 'nombre_apellidos' | 'apellidos_nombre' | 'nombre_solo';
type FormatoApartamento = 'nota' | 'etiqueta' | 'ninguno';

interface PreferenciasContactos {
  formato_nombre_contacto: FormatoNombre;
  incluir_apartamento_contacto: boolean;
  formato_apartamento_contacto: FormatoApartamento;
  incluir_checkin_contacto: boolean;
}

interface SyncResultado {
  total: number;
  nuevos: number;
  actualizados: number;
  advertencias?: string[];
}

const _PREFS_DEFECTO: PreferenciasContactos = {
  formato_nombre_contacto: 'nombre_apellidos',
  incluir_apartamento_contacto: true,
  formato_apartamento_contacto: 'nota',
  incluir_checkin_contacto: true,
};

@Component({
  selector: 'app-sincronizador-contactos',
  templateUrl: './sincronizador-contactos.html',
  styleUrl: './sincronizador-contactos.scss',
  standalone: true,
  imports: [FormsModule, PageHeaderComponent, ButtonComponent, BadgeComponent, TarjetaEstadoComponent, PanelSeccionComponent, FormInputIconComponent],
})
export class SincronizadorContactosPageComponent implements OnInit {

  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);

  // ── Estado PMS ──────────────────────────────────────────────────────────
  readonly pmsConectado = signal(false);

  // ── Estado Google ─────────────────────────────────────────────────────────
  readonly googleConectado = signal(false);
  readonly ultimoSync = signal<string | null>(null);
  readonly syncEnCurso = signal(false);

  // ── Preferencias ──────────────────────────────────────────────────────────
  readonly preferencias = signal<PreferenciasContactos>({ ..._PREFS_DEFECTO });

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

  // ── Opciones de formulario ────────────────────────────────────────────────
  readonly formatoNombreOpciones: { valor: FormatoNombre; label: string }[] = [
    { valor: 'nombre_apellidos', label: 'Nombre Apellidos (ej. Juan García)' },
    { valor: 'apellidos_nombre', label: 'Apellidos, Nombre (ej. García, Juan)' },
    { valor: 'nombre_solo', label: 'Solo nombre (ej. Juan)' },
  ];

  readonly formatoApartamentoOpciones: { valor: FormatoApartamento; label: string }[] = [
    { valor: 'nota', label: 'En notas del contacto' },
    { valor: 'etiqueta', label: 'Como etiqueta de grupo en Google Contacts' },
    { valor: 'ninguno', label: 'No incluir' },
  ];

  // ── Ciclo de vida ─────────────────────────────────────────────────────────

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
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
      '/api/pms/config'
    ).subscribe({
      next: res => this.pmsConectado.set(res.config !== null),
      error: () => this.pmsConectado.set(false),
    });
  }

  private cargarPreferencias(): void {
    this.http.get<{ ok: boolean; preferencias: PreferenciasContactos }>(
      '/api/contactos/preferencias'
    ).subscribe({
      next: res => this.preferencias.set(res.preferencias),
      error: err => console.error('[sincronizador-contactos] Error al obtener preferencias:', err),
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
      '/api/contactos/sync',
      this._parseFechasPayload(),
    ).subscribe({
      next: res => {
        this.syncEnCurso.set(false);
        this.ultimoSync.set(new Date().toISOString());
        this.nuevosContactos.set(res.resultado.nuevos);
        if (res.resultado.advertencias?.length) {
          console.warn('[sincronizador-contactos] Sync con advertencias:', res.resultado.advertencias);
        }
      },
      error: err => {
        this.syncEnCurso.set(false);
        console.error('[sincronizador-contactos] Error en sync:', err);
      },
    });
  }

  exportarCsv(): void {
    this.http.post('/api/contactos/export/csv', this._parseFechasPayload(), { responseType: 'blob' }).subscribe({
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
      '/api/contactos/xlsx/sync',
      form,
    ).subscribe({
      next: res => {
        this.xlsxEnCurso.set(false);
        this.ultimoSync.set(new Date().toISOString());
        this.nuevosContactos.set(res.resultado.nuevos);
        if (res.resultado.advertencias?.length) {
          console.warn('[sincronizador-contactos] XLSX sync con advertencias:', res.resultado.advertencias);
        }
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

    this.http.post('/api/contactos/xlsx/export/csv', form, { responseType: 'blob' }).subscribe({
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
