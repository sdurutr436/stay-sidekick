import { Component, computed, inject, OnDestroy, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { RouterLink } from '@angular/router';
import { ButtonComponent } from '../../components/atoms/button/button';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { TarjetaEstadoComponent } from '../../components/molecules/tarjeta-estado/tarjeta-estado';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { BadgeComponent } from '../../components/atoms/badge/badge';

interface CheckinHoy {
  nombre: string;
  apartamento: string | null;
  email: string | null;
  telefono: string | null;
  checkin: string | null;
  checkout: string | null;
  hora_llegada: string | null;
  direccion: string | null;
}

interface ApartamentoRef {
  id: string;
  nombre: string;
  ciudad: string | null;
}

interface StatusResponse {
  ok: boolean;
  pms_configurado: boolean;
  hora_corte: string;
  pms_error: string | null;
  apartamentos: ApartamentoRef[];
  reservas_pms: CheckinHoy[];
}

@Component({
  selector: 'app-notificaciones-checkin-tardio',
  templateUrl: './notificaciones-checkin-tardio.html',
  styleUrl: './notificaciones-checkin-tardio.scss',
  standalone: true,
  imports: [FormsModule, RouterLink, PageHeaderComponent, PanelSeccionComponent, ButtonComponent, TarjetaEstadoComponent, AlertComponent, BadgeComponent],
})
export class NotificacionesCheckinTardioPageComponent implements OnInit, OnDestroy {

  private readonly http = inject(HttpClient);

  // ── Estado general ────────────────────────────────────────────────────
  readonly cargando = signal(true);
  readonly pmsConfigurado = signal(false);
  readonly pmsError = signal<string | null>(null);
  readonly horaCortePerfil = signal<string>('20:00');

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
  mensaje = '';

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
        this.pmsConfigurado.set(res.pms_configurado);
        this.horaCortePerfil.set(res.hora_corte ?? '20:00');
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
      '/api/notificaciones/checkin-tardio/checkins',
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
      const extras = [
        c.hora_llegada ? `Hora prevista: ${c.hora_llegada}` : null,
        c.direccion    ? `Dirección: ${c.direccion}`         : null,
      ].filter(Boolean).join('\n');
      return (
        `Estimado/a ${c.nombre},\n\n` +
        `Le recordamos que su check-in${apt} está programado para hoy, ${hoy}.` +
        (extras ? `\n${extras}` : '') +
        `\n\nSi prevé llegar más tarde de lo habitual, le agradecemos que nos lo comunique lo antes posible para poder gestionar correctamente el acceso.\n\n` +
        `Quedo a su disposición para cualquier consulta.\n\n` +
        `Saludos cordiales.`
      );
    }

    const lista = checkins
      .map(c => {
        const apt = c.apartamento ? ` — ${c.apartamento}` : '';
        const hora = c.checkin ? ` (check-in: ${c.checkin})` : '';
        const extras = [
          c.hora_llegada ? `  Hora prevista: ${c.hora_llegada}` : null,
          c.direccion    ? `  Dirección: ${c.direccion}`         : null,
        ].filter(Boolean).join('\n');
        return `• ${c.nombre}${apt}${hora}` + (extras ? `\n${extras}` : '');
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

}

