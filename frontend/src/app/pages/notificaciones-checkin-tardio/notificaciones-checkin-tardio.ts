import { Component, ElementRef, OnDestroy, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { NgIconComponent } from '@ng-icons/core';
import { ButtonComponent } from '../../components/atoms/button/button';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { DropdownBuscadorComponent, DropdownOption } from '../../components/molecules/dropdown-buscador/dropdown-buscador';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { AuthService } from '../../services/auth.service';

const TOKENS: DropdownOption[] = [
  { value: '{NOMBRE}',       label: '{NOMBRE} — Nombre del huésped'         },
  { value: '{APARTAMENTO}',  label: '{APARTAMENTO} — Nombre del apartamento'},
  { value: '{TELEFONO}',     label: '{TELEFONO} — Teléfono del huésped'     },
  { value: '{HORA_LLEGADA}', label: '{HORA_LLEGADA} — Hora prevista'        },
  { value: '{DIRECCION}',    label: '{DIRECCION} — Dirección'               },
];

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

interface PlantillaNotif {
  id: string;
  nombre: string;
  contenido: string;
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
  imports: [
    NgIconComponent,
    FormsModule,
    PageHeaderComponent, PanelSeccionComponent,
    ButtonComponent, AlertComponent,
    DropdownBuscadorComponent,
  ],
})
export class NotificacionesCheckinTardioPageComponent implements OnInit, OnDestroy {

  @ViewChild('editTextarea')   private editTaRef!: ElementRef<HTMLTextAreaElement>;
  @ViewChild('mensajeTextarea') private msgTaRef!: ElementRef<HTMLTextAreaElement>;

  private readonly http = inject(HttpClient);
  private readonly auth = inject(AuthService);
  readonly isAdmin = this.auth.isAdmin;

  // ── Tokens disponibles ────────────────────────────────────────────────
  readonly tokensOpciones = signal<DropdownOption[]>(TOKENS);
  readonly tokenEditorSel  = signal<DropdownOption | null>(null);
  readonly tokenMensajeSel = signal<DropdownOption | null>(null);
  private editCursorPos   = 0;
  private msgCursorPos    = 0;

  // ── Estado general ────────────────────────────────────────────────────
  readonly cargando        = signal(true);
  readonly pmsConfigurado  = signal(false);
  readonly pmsError        = signal<string | null>(null);
  readonly horaCortePerfil = signal<string>('20:00');

  // ── Datos del día ─────────────────────────────────────────────────────
  readonly apartamentos = signal<ApartamentoRef[]>([]);
  readonly reservasPms  = signal<CheckinHoy[]>([]);

  // ── XLSX ──────────────────────────────────────────────────────────────
  readonly xlsxArchivo      = signal<File | null>(null);
  readonly xlsxEnCurso      = signal(false);
  readonly xlsxCheckins     = signal<CheckinHoy[]>([]);
  readonly xlsxAdvertencias = signal<string[]>([]);

  readonly todosCheckins = computed<CheckinHoy[]>(() => {
    const pms  = this.reservasPms();
    const xlsx = this.xlsxCheckins();
    const enPms = new Set(pms.map(r => r.nombre));
    return [...pms, ...xlsx.filter(r => !enPms.has(r.nombre))];
  });
  readonly hayCheckins = computed(() => this.todosCheckins().length > 0);

  // ── Plantillas ────────────────────────────────────────────────────────
  readonly plantillas            = signal<PlantillaNotif[]>([]);
  readonly searchPlantillas      = signal('');
  readonly plantillaSeleccionada = signal<PlantillaNotif | null>(null);
  readonly plantillasFiltradas   = computed(() => {
    const q = this.searchPlantillas().toLowerCase().trim();
    if (!q) return this.plantillas();
    return this.plantillas().filter(p => p.nombre.toLowerCase().includes(q));
  });

  readonly modoEditor      = signal<'ninguno' | 'nueva' | 'editar'>('ninguno');
  readonly editNombre      = signal('');
  readonly editContenido   = signal('');
  readonly guardandoEdit   = signal(false);
  readonly plantillaAlerta = signal<{ tipo: 'success' | 'error'; mensaje: string } | null>(null);

  // ── Mensaje ───────────────────────────────────────────────────────────
  mensaje = '';
  readonly copiadoOk = signal(false);
  private _copiadoTimer: ReturnType<typeof setTimeout> | null = null;

  // ── Ciclo de vida ─────────────────────────────────────────────────────

  ngOnInit(): void {
    this.cargarStatus();
    this.cargarPlantillas();
  }

  ngOnDestroy(): void {
    if (this._copiadoTimer) clearTimeout(this._copiadoTimer);
  }

  // ── Carga de estado ───────────────────────────────────────────────────

  private cargarStatus(): void {
    this.cargando.set(true);
    const d = new Date();
    const fechaLocal = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`;
    this.http.get<StatusResponse>(`/api/notificaciones/checkin-tardio/status?fecha=${fechaLocal}`).subscribe({
      next: res => {
        this.pmsConfigurado.set(res.pms_configurado);
        this.horaCortePerfil.set(res.hora_corte ?? '20:00');
        this.pmsError.set(res.pms_error ?? null);
        this.apartamentos.set(res.apartamentos);
        this.reservasPms.set(res.reservas_pms);
        this.cargando.set(false);
        if (res.reservas_pms.length > 0) {
          this.mensaje = this._buildPlantilla(res.reservas_pms);
        }
      },
      error: () => this.cargando.set(false),
    });
  }

  // ── XLSX (auto-proceso al seleccionar) ────────────────────────────────

  onXlsxSeleccionado(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file  = input.files?.[0] ?? null;
    input.value = '';
    this.xlsxArchivo.set(file);
    this.xlsxCheckins.set([]);
    this.xlsxAdvertencias.set([]);
    if (file) this._subirXlsx(file);
  }

  limpiarXlsx(): void {
    this.xlsxArchivo.set(null);
    this.xlsxCheckins.set([]);
    this.xlsxAdvertencias.set([]);
  }

  private _subirXlsx(archivo: File): void {
    if (this.xlsxEnCurso()) return;
    this.xlsxEnCurso.set(true);
    const form = new FormData();
    form.append('file', archivo);
    this.http.post<{ ok: boolean; checkins: CheckinHoy[]; warnings?: string[] }>(
      '/api/notificaciones/checkin-tardio/checkins', form,
    ).subscribe({
      next: res => {
        this.xlsxEnCurso.set(false);
        this.xlsxCheckins.set(res.checkins);
        this.xlsxAdvertencias.set(res.warnings ?? []);
        const todos = this.todosCheckins();
        if (todos.length > 0) this.mensaje = this._buildPlantilla(todos);
      },
      error: () => this.xlsxEnCurso.set(false),
    });
  }

  // ── Plantillas: CRUD ──────────────────────────────────────────────────

  private cargarPlantillas(): void {
    this.http.get<{ ok: boolean; plantillas: PlantillaNotif[] }>(
      '/api/notificaciones/checkin-tardio/plantillas'
    ).subscribe({ next: res => this.plantillas.set(res.plantillas ?? []) });
  }

  onSearchPlantillas(event: Event): void {
    this.searchPlantillas.set((event.target as HTMLInputElement).value);
  }

  seleccionarPlantilla(p: PlantillaNotif): void {
    this.plantillaSeleccionada.set(p);
    if (this.modoEditor() !== 'ninguno') this.modoEditor.set('ninguno');
  }

  nuevaPlantilla(): void {
    this.plantillaSeleccionada.set(null);
    this.editNombre.set('');
    this.editContenido.set('');
    this.editCursorPos = 0;
    this.plantillaAlerta.set(null);
    this.modoEditor.set('nueva');
  }

  iniciarEdicion(p: PlantillaNotif): void {
    this.plantillaSeleccionada.set(p);
    this.editNombre.set(p.nombre);
    this.editContenido.set(p.contenido);
    this.editCursorPos = p.contenido.length;
    this.plantillaAlerta.set(null);
    this.modoEditor.set('editar');
  }

  cancelarEdicion(): void {
    this.modoEditor.set('ninguno');
    this.plantillaAlerta.set(null);
  }

  guardarEdicion(): void {
    const nombre   = this.editNombre().trim();
    const contenido = this.editContenido().trim();
    if (!nombre || !contenido) return;

    this.plantillaAlerta.set(null);
    this.guardandoEdit.set(true);

    if (this.modoEditor() === 'nueva') {
      this.http.post<{ ok: boolean; plantilla: PlantillaNotif; errors?: string[] }>(
        '/api/notificaciones/checkin-tardio/plantillas', { nombre, contenido }
      ).subscribe({
        next: res => {
          if (res.ok) {
            this.plantillas.update(l => [...l, res.plantilla]);
            this.plantillaSeleccionada.set(res.plantilla);
            this.modoEditor.set('ninguno');
            this.plantillaAlerta.set({ tipo: 'success', mensaje: 'Plantilla creada.' });
          } else {
            this.plantillaAlerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al crear.' });
          }
          this.guardandoEdit.set(false);
        },
        error: err => {
          this.plantillaAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al crear.' });
          this.guardandoEdit.set(false);
        },
      });
    } else {
      const id = this.plantillaSeleccionada()!.id;
      this.http.put<{ ok: boolean; plantilla: PlantillaNotif; errors?: string[] }>(
        `/api/notificaciones/checkin-tardio/plantillas/${id}`, { nombre, contenido }
      ).subscribe({
        next: res => {
          if (res.ok) {
            this.plantillas.update(l => l.map(p => p.id === id ? res.plantilla : p));
            this.plantillaSeleccionada.set(res.plantilla);
            this.modoEditor.set('ninguno');
            this.plantillaAlerta.set({ tipo: 'success', mensaje: 'Plantilla actualizada.' });
          } else {
            this.plantillaAlerta.set({ tipo: 'error', mensaje: res.errors?.[0] ?? 'Error al actualizar.' });
          }
          this.guardandoEdit.set(false);
        },
        error: err => {
          this.plantillaAlerta.set({ tipo: 'error', mensaje: err?.error?.errors?.[0] ?? 'Error al actualizar.' });
          this.guardandoEdit.set(false);
        },
      });
    }
  }

  eliminarPlantilla(p: PlantillaNotif): void {
    this.http.delete<{ ok: boolean }>(
      `/api/notificaciones/checkin-tardio/plantillas/${p.id}`
    ).subscribe({
      next: () => {
        this.plantillas.update(l => l.filter(t => t.id !== p.id));
        if (this.plantillaSeleccionada()?.id === p.id) {
          this.plantillaSeleccionada.set(null);
          this.modoEditor.set('ninguno');
        }
      },
    });
  }

  // ── Generación de mensaje ─────────────────────────────────────────────

  generarMensaje(): void {
    const checkins  = this.todosCheckins();
    if (checkins.length === 0) return;
    const plantilla = this.plantillaSeleccionada();
    this.mensaje = plantilla
      ? this._buildConPlantilla(checkins, plantilla.contenido)
      : this._buildPlantilla(checkins);
  }

  private _buildConPlantilla(checkins: CheckinHoy[], tpl: string): string {
    return checkins.map(c =>
      tpl
        .replace(/{NOMBRE}/g,       c.nombre)
        .replace(/{APARTAMENTO}/g,  c.apartamento ?? '—')
        .replace(/{TELEFONO}/g,     c.telefono ?? '—')
        .replace(/{HORA_LLEGADA}/g, c.hora_llegada ?? '—')
        .replace(/{DIRECCION}/g,    c.direccion ?? '—')
    ).join('\n\n---\n\n');
  }

  private _buildPlantilla(checkins: CheckinHoy[]): string {
    if (checkins.length === 0) return '';
    const hoy = new Date().toLocaleDateString('es-ES', {
      weekday: 'long', year: 'numeric', month: 'long', day: 'numeric',
    });
    if (checkins.length === 1) {
      const c = checkins[0];
      const apt    = c.apartamento ? ` en ${c.apartamento}` : '';
      const extras = [
        c.hora_llegada ? `Hora prevista: ${c.hora_llegada}` : null,
        c.direccion    ? `Dirección: ${c.direccion}`         : null,
      ].filter(Boolean).join('\n');
      return (
        `Estimado/a ${c.nombre},\n\n` +
        `Le recordamos que su check-in${apt} está programado para hoy, ${hoy}.` +
        (extras ? `\n${extras}` : '') +
        `\n\nSi prevé llegar más tarde de lo habitual, le agradecemos que nos lo comunique.\n\n` +
        `Quedo a su disposición para cualquier consulta.\n\nSaludos cordiales.`
      );
    }
    const lista = checkins.map(c => {
      const apt    = c.apartamento ? ` — ${c.apartamento}` : '';
      const extras = [
        c.hora_llegada ? `  Hora prevista: ${c.hora_llegada}` : null,
        c.direccion    ? `  Dirección: ${c.direccion}`         : null,
      ].filter(Boolean).join('\n');
      return `• ${c.nombre}${apt}` + (extras ? `\n${extras}` : '');
    }).join('\n');
    return (
      `Recordatorio de check-ins para hoy, ${hoy}:\n\n${lista}\n\n` +
      `Si alguno prevé llegar tarde, le agradecemos que nos lo comunique.\n\nSaludos cordiales.`
    );
  }

  // ── Tokens: inserción en editor de plantilla ──────────────────────────

  onTokenEditorSel(opt: DropdownOption): void { this.tokenEditorSel.set(opt); }

  insertarTokenEnPlantilla(): void {
    const token = this.tokenEditorSel();
    if (!token) return;
    const base = this.editContenido();
    const pos  = this.editCursorPos;
    const nuevo = base.slice(0, pos) + token.value + base.slice(pos);
    const nuevoCursor = pos + token.value.length;
    this.editContenido.set(nuevo);
    this.editCursorPos = nuevoCursor;
    const el = this.editTaRef?.nativeElement;
    if (el) {
      el.value = nuevo;
      setTimeout(() => { el.focus(); el.setSelectionRange(nuevoCursor, nuevoCursor); });
    }
  }

  onEditInput(event: Event): void {
    const ta = event.target as HTMLTextAreaElement;
    this.editContenido.set(ta.value);
    this.editCursorPos = ta.selectionStart ?? this.editContenido().length;
  }

  onEditCursor(event: Event): void {
    this.editCursorPos = (event.target as HTMLTextAreaElement).selectionStart ?? 0;
  }

  // ── Tokens: inserción en mensaje ──────────────────────────────────────

  onTokenMensajeSel(opt: DropdownOption): void { this.tokenMensajeSel.set(opt); }

  insertarTokenEnMensaje(): void {
    const token = this.tokenMensajeSel();
    if (!token) return;
    const pos  = this.msgCursorPos;
    const nuevo = this.mensaje.slice(0, pos) + token.value + this.mensaje.slice(pos);
    const nuevoCursor = pos + token.value.length;
    this.mensaje = nuevo;
    this.msgCursorPos = nuevoCursor;
    const el = this.msgTaRef?.nativeElement;
    if (el) {
      el.value = nuevo;
      setTimeout(() => { el.focus(); el.setSelectionRange(nuevoCursor, nuevoCursor); });
    }
  }

  onMsgCursor(event: Event): void {
    this.msgCursorPos = (event.target as HTMLTextAreaElement).selectionStart ?? 0;
  }

  // ── Copiar mensaje ────────────────────────────────────────────────────

  copiarMensaje(): void {
    if (!this.mensaje) return;
    navigator.clipboard.writeText(this.mensaje).then(() => {
      if (this._copiadoTimer) clearTimeout(this._copiadoTimer);
      this.copiadoOk.set(true);
      this._copiadoTimer = setTimeout(() => this.copiadoOk.set(false), 2000);
    });
  }
}
