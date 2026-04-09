import { Component, computed, inject, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';

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
  imports: [FormsModule],
})
export class SincronizadorContactosPageComponent implements OnInit {

  private readonly http = inject(HttpClient);
  private readonly route = inject(ActivatedRoute);

  // ── Estado Google ─────────────────────────────────────────────────────────
  readonly googleConectado = signal(false);
  readonly ultimoSync = signal<string | null>(null);
  readonly syncEnCurso = signal(false);

  // ── Preferencias ──────────────────────────────────────────────────────────
  readonly preferencias = signal<PreferenciasContactos>({ ..._PREFS_DEFECTO });

  readonly mostrarFormatoApartamento = computed(
    () => this.preferencias().incluir_apartamento_contacto,
  );

  // ── XLSX ──────────────────────────────────────────────────────────────────
  readonly xlsxArchivo = signal<File | null>(null);
  readonly xlsxEnCurso = signal(false);

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
    // Leer parámetros de query del callback OAuth de Google
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

  private cargarPreferencias(): void {
    this.http.get<{ ok: boolean; preferencias: PreferenciasContactos }>(
      '/api/contactos/preferencias'
    ).subscribe({
      next: res => this.preferencias.set(res.preferencias),
      error: err => console.error('[sincronizador-contactos] Error al obtener preferencias:', err),
    });
  }

  // ── Conexión Google ───────────────────────────────────────────────────────

  connectarGoogle(): void {
    this.http.get<{ ok: boolean; url: string }>('/api/contactos/google/auth').subscribe({
      next: res => {
        if (res.url) {
          window.location.href = res.url;
        }
      },
      error: err => console.error('[sincronizador-contactos] Error al obtener URL OAuth:', err),
    });
  }

  desconectarGoogle(): void {
    this.http.delete<{ ok: boolean }>('/api/contactos/google/disconnect').subscribe({
      next: () => {
        this.googleConectado.set(false);
        this.ultimoSync.set(null);
      },
      error: err => console.error('[sincronizador-contactos] Error al desconectar Google:', err),
    });
  }

  // ── Preferencias ──────────────────────────────────────────────────────────

  onFormatoNombreChange(valor: string): void {
    this.preferencias.update(p => ({
      ...p,
      formato_nombre_contacto: valor as FormatoNombre,
    }));
  }

  onIncluirApartamentoChange(checked: boolean): void {
    this.preferencias.update(p => ({ ...p, incluir_apartamento_contacto: checked }));
  }

  onFormatoApartamentoChange(valor: string): void {
    this.preferencias.update(p => ({
      ...p,
      formato_apartamento_contacto: valor as FormatoApartamento,
    }));
  }

  onIncluirCheckinChange(checked: boolean): void {
    this.preferencias.update(p => ({ ...p, incluir_checkin_contacto: checked }));
  }

  guardarPreferencias(): void {
    this.http.put<{ ok: boolean; preferencias: PreferenciasContactos }>(
      '/api/contactos/preferencias',
      this.preferencias(),
    ).subscribe({
      next: res => this.preferencias.set(res.preferencias),
      error: err => console.error('[sincronizador-contactos] Error al guardar preferencias:', err),
    });
  }

  // ── Sincronización (fuente: PMS API) ──────────────────────────────────────

  lanzarSync(): void {
    if (this.syncEnCurso()) return;
    this.syncEnCurso.set(true);

    this.http.post<{ ok: boolean; resultado: SyncResultado }>(
      '/api/contactos/sync',
      {},
    ).subscribe({
      next: res => {
        this.syncEnCurso.set(false);
        this.ultimoSync.set(new Date().toISOString());
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
    this.http.post('/api/contactos/export/csv', {}, { responseType: 'blob' }).subscribe({
      next: blob => this._descargarBlob(blob, 'contactos_google.csv'),
      error: err => console.error('[sincronizador-contactos] Error al exportar CSV:', err),
    });
  }

  // ── XLSX ──────────────────────────────────────────────────────────────────

  onXlsxSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.xlsxArchivo.set(file);
    input.value = ''; // permite volver a seleccionar el mismo archivo
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
