import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';

interface CheckinHoy {
  nombre: string;
  apartamento: string | null;
  email: string | null;
  telefono: string | null;
  checkin: string | null;
  checkout: string | null;
}

interface ApartamentoRef {
  id: string;
  nombre: string;
  ciudad: string | null;
}

interface StatusResponse {
  ok: boolean;
  gmail_configurado: boolean;
  pms_configurado: boolean;
  pms_error: string | null;
  apartamentos: ApartamentoRef[];
  reservas_pms: CheckinHoy[];
}

type EstadoEnvio = 'idle' | 'ok' | 'error';

@Component({
  selector: 'app-notificaciones-checkin-tardio',
  templateUrl: './notificaciones-checkin-tardio.html',
  styleUrl: './notificaciones-checkin-tardio.scss',
  standalone: true,
  imports: [FormsModule],
})
export class NotificacionesCheckinTardioPageComponent implements OnInit, OnDestroy {

  private readonly http = inject(HttpClient);

  // ── Estado general ────────────────────────────────────────────────────
  readonly cargando = signal(true);
  readonly gmailConfigurado = signal(false);
  readonly pmsConfigurado = signal(false);
  readonly pmsError = signal<string | null>(null);

  // ── Datos del día ─────────────────────────────────────────────────────
  readonly apartamentos = signal<ApartamentoRef[]>([]);
  readonly reservasPms = signal<CheckinHoy[]>([]);

  // ── XLSX ──────────────────────────────────────────────────────────────
  readonly xlsxArchivo = signal<File | null>(null);
  readonly xlsxEnCurso = signal(false);
  readonly xlsxCheckins = signal<CheckinHoy[]>([]);
  readonly xlsxAdvertencias = signal<string[]>([]);

  // ── Todos los check-ins disponibles (PMS + XLSX, deduplicados por nombre) ──
  readonly todosCheckins = computed<CheckinHoy[]>(() => {
    const pms = this.reservasPms();
    const xlsx = this.xlsxCheckins();
    const nombresEnPms = new Set(pms.map(r => r.nombre));
    const soloXlsx = xlsx.filter(r => !nombresEnPms.has(r.nombre));
    return [...pms, ...soloXlsx];
  });

  readonly hayCheckins = computed(() => this.todosCheckins().length > 0);

  // ── Notificación ──────────────────────────────────────────────────────
  destinatario = '';
  asunto = 'Recordatorio de check-in';
  mensaje = '';

  readonly enviando = signal(false);
  readonly estadoEnvio = signal<EstadoEnvio>('idle');
  readonly errorEnvio = signal<string | null>(null);
  readonly copiadoOk = signal(false);
  private _copiadoTimer: ReturnType<typeof setTimeout> | null = null;

  // ── Ciclo de vida ─────────────────────────────────────────────────────

  ngOnInit(): void {
    this.cargarStatus();
  }

  ngOnDestroy(): void {
    if (this._copiadoTimer) clearTimeout(this._copiadoTimer);
  }

  // ── Carga de estado ───────────────────────────────────────────────────

  private cargarStatus(): void {
    this.cargando.set(true);
    this.http.get<StatusResponse>(
      '/api/notificaciones/checkin-tardio/status'
    ).subscribe({
      next: res => {
        this.gmailConfigurado.set(res.gmail_configurado);
        this.pmsConfigurado.set(res.pms_configurado);
        this.pmsError.set(res.pms_error ?? null);
        this.apartamentos.set(res.apartamentos);
        this.reservasPms.set(res.reservas_pms);
        this.cargando.set(false);

        // Pre-generar plantilla si hay datos
        if (res.reservas_pms.length > 0) {
          this.mensaje = this._buildPlantilla(res.reservas_pms);
        }
      },
      error: err => {
        console.error('[notificaciones-checkin-tardio] Error al cargar estado:', err);
        this.cargando.set(false);
      },
    });
  }

  // ── XLSX ──────────────────────────────────────────────────────────────

  onXlsxSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0] ?? null;
    this.xlsxArchivo.set(file);
    this.xlsxCheckins.set([]);
    this.xlsxAdvertencias.set([]);
    input.value = '';
  }

  procesarXlsx(): void {
    const archivo = this.xlsxArchivo();
    if (!archivo || this.xlsxEnCurso()) return;

    this.xlsxEnCurso.set(true);
    const form = new FormData();
    form.append('file', archivo);

    this.http.post<{ ok: boolean; checkins: CheckinHoy[]; warnings?: string[] }>(
      '/api/notificaciones/checkin-tardio/xlsx',
      form,
    ).subscribe({
      next: res => {
        this.xlsxEnCurso.set(false);
        this.xlsxCheckins.set(res.checkins);
        this.xlsxAdvertencias.set(res.warnings ?? []);
        // Regenerar plantilla con todos los datos disponibles
        const todos = this.todosCheckins();
        if (todos.length > 0) {
          this.mensaje = this._buildPlantilla(todos);
        }
      },
      error: err => {
        this.xlsxEnCurso.set(false);
        console.error('[notificaciones-checkin-tardio] Error al procesar XLSX:', err);
      },
    });
  }

  // ── Plantilla de mensaje ──────────────────────────────────────────────

  generarPlantilla(): void {
    const checkins = this.todosCheckins();
    this.mensaje = this._buildPlantilla(checkins);
  }

  private _buildPlantilla(checkins: CheckinHoy[]): string {
    if (checkins.length === 0) return '';

    const hoy = new Date().toLocaleDateString('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    });

    if (checkins.length === 1) {
      const c = checkins[0];
      const apt = c.apartamento ? ` en ${c.apartamento}` : '';
      return (
        `Estimado/a ${c.nombre},\n\n` +
        `Le recordamos que su check-in${apt} está programado para hoy, ${hoy}.\n\n` +
        `Si prevé llegar más tarde de lo habitual, le agradecemos que nos lo comunique lo antes posible para poder gestionar correctamente el acceso.\n\n` +
        `Quedo a su disposición para cualquier consulta.\n\n` +
        `Saludos cordiales.`
      );
    }

    const lista = checkins
      .map(c => {
        const apt = c.apartamento ? ` — ${c.apartamento}` : '';
        const hora = c.checkin ? ` (check-in: ${c.checkin})` : '';
        return `• ${c.nombre}${apt}${hora}`;
      })
      .join('\n');

    return (
      `Recordatorio de check-ins para hoy, ${hoy}:\n\n` +
      `${lista}\n\n` +
      `Si alguno de los huéspedes prevé llegar más tarde de lo habitual, ` +
      `le agradecemos que nos lo comunique lo antes posible.\n\n` +
      `Saludos cordiales.`
    );
  }

  // ── Copiar mensaje ────────────────────────────────────────────────────────

  copiarMensaje(): void {
    if (!this.mensaje) return;
    navigator.clipboard.writeText(this.mensaje).then(() => {
      if (this._copiadoTimer) clearTimeout(this._copiadoTimer);
      this.copiadoOk.set(true);
      this._copiadoTimer = setTimeout(() => this.copiadoOk.set(false), 2000);
    });
  }

  // ── Envío de notificación ─────────────────────────────────────────────

  enviarNotificacion(): void {
    if (this.enviando() || !this.gmailConfigurado()) return;
    if (!this.destinatario.trim() || !this.mensaje.trim()) return;

    this.enviando.set(true);
    this.estadoEnvio.set('idle');
    this.errorEnvio.set(null);

    this.http.post<{ ok: boolean; errors?: string[] }>(
      '/api/notificaciones/checkin-tardio/enviar',
      {
        destinatario: this.destinatario.trim(),
        asunto: this.asunto.trim(),
        mensaje: this.mensaje.trim(),
      },
    ).subscribe({
      next: res => {
        this.enviando.set(false);
        if (res.ok) {
          this.estadoEnvio.set('ok');
        } else {
          this.estadoEnvio.set('error');
          this.errorEnvio.set(res.errors?.[0] ?? 'Error desconocido.');
        }
      },
      error: err => {
        this.enviando.set(false);
        this.estadoEnvio.set('error');
        this.errorEnvio.set(
          err?.error?.errors?.[0] ?? 'No se pudo conectar con el servidor.'
        );
      },
    });
  }
}
