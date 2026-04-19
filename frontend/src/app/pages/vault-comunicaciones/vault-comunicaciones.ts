import { Component, ElementRef, OnDestroy, ViewChild, computed, signal } from '@angular/core';
// import { HttpClient } from '@angular/common/http'; // Descomentar al integrar el backend
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ButtonComponent } from '../../components/atoms/button/button';
import { DropdownBuscadorComponent, DropdownOption } from '../../components/molecules/dropdown-buscador/dropdown-buscador';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';

interface Plantilla {
  id: string;
  nombre: string;
  contenido: string;
  idioma: string;
  categoria: string | null;
  activa: boolean;
}

// Placeholders disponibles para insertar en el mensaje
const PLACEHOLDERS: DropdownOption[] = [
  { value: '{NOMBRE}',            label: '{NOMBRE} — Nombre del huésped' },
  { value: '{APARTAMENTO}',       label: '{APARTAMENTO} — Nombre del apartamento' },
  { value: '{HORA_LLEGADA}',      label: '{HORA_LLEGADA} — Hora de llegada' },
  { value: '{IDIOMA}',            label: '{IDIOMA} — Idioma del huésped' },
  { value: '{PROTOCOLO_CHECKIN}', label: '{PROTOCOLO_CHECKIN} — Protocolo de check-in' },
];

// Textos rotativos para la confirmación de copiado (todos comunican lo mismo, dan variedad)
const MENSAJES_COPIADO = [
  '¡Copiado!',
  'Mensaje copiado',
  'Listo, ya puedes pegarlo',
  'En el portapapeles',
  'Copiado al portapapeles',
];

// ── INICIO DATOS MOCK ──────────────────────────────────────────────────────────
// TODO: Eliminar este bloque cuando GET /api/vault/plantillas esté integrado.
//       Sustituir por: this.http.get<Plantilla[]>('/api/vault/plantillas')
//       y usar toSignal() o subscribe para alimentar la señal `plantillas`.
const MOCK_PLANTILLAS: Plantilla[] = [
  {
    id: 'mock-vault-1',
    nombre: 'Bienvenida estándar',
    contenido: 'Hola {NOMBRE}, bienvenido/a a {APARTAMENTO}. Tu llegada está prevista para las {HORA_LLEGADA}. {PROTOCOLO_CHECKIN}',
    idioma: 'es',
    categoria: 'bienvenida',
    activa: true,
  },
  {
    id: 'mock-vault-2',
    nombre: 'Check-in tardío',
    contenido: 'Hola {NOMBRE}, hemos detectado que tu llegada a {APARTAMENTO} será más tarde del horario habitual. Aquí tienes las instrucciones de acceso: {PROTOCOLO_CHECKIN}',
    idioma: 'es',
    categoria: 'checkin_tardio',
    activa: true,
  },
  {
    id: 'mock-vault-3',
    nombre: 'Welcome message (EN)',
    contenido: 'Hello {NOMBRE}, welcome to {APARTAMENTO}! Your check-in is scheduled at {HORA_LLEGADA}. {PROTOCOLO_CHECKIN}',
    idioma: 'en',
    categoria: 'bienvenida',
    activa: true,
  },
  {
    id: 'mock-vault-4',
    nombre: 'Instrucciones de salida',
    contenido: 'Hola {NOMBRE}, recuerda que el check-out en {APARTAMENTO} es a las 11:00h. Por favor deja las llaves en el interior.',
    idioma: 'es',
    categoria: 'instrucciones',
    activa: true,
  },
  {
    id: 'mock-vault-5',
    nombre: 'Recordatorio de llegada',
    contenido: 'Hola {NOMBRE}, te recordamos que mañana te esperamos en {APARTAMENTO}. Hora estimada de llegada: {HORA_LLEGADA}. ¡Nos vemos pronto!',
    idioma: 'es',
    categoria: 'recordatorio',
    activa: false,
  },
];
// ── FIN DATOS MOCK ─────────────────────────────────────────────────────────────

const COOLDOWN_SEGUNDOS = 60;

@Component({
  selector: 'app-vault-comunicaciones',
  templateUrl: './vault-comunicaciones.html',
  styleUrl: './vault-comunicaciones.scss',
  standalone: true,
  imports: [PageHeaderComponent, ButtonComponent, AlertComponent, DropdownBuscadorComponent],
})
export class VaultComunicacionesPageComponent implements OnDestroy {
  // private readonly http = inject(HttpClient); // Descomentar al integrar el backend

  @ViewChild('mensajeTextarea') private mensajeTextareaRef!: ElementRef<HTMLTextAreaElement>;

  // ── INICIO DATOS MOCK ────────────────────────────────────────────────────────
  // TODO: Reemplazar por llamada real al backend (GET /api/vault/plantillas)
  readonly plantillas = signal<Plantilla[]>(MOCK_PLANTILLAS);
  // ── FIN DATOS MOCK ───────────────────────────────────────────────────────────

  readonly searchPlantillas      = signal('');
  readonly plantillaSeleccionada = signal<Plantilla | null>(null);
  readonly mensajeActual         = signal('');
  readonly placeholderSeleccionado = signal<DropdownOption | null>(null);
  readonly placeholderOpciones: DropdownOption[] = PLACEHOLDERS;

  readonly nombreActual          = signal('');
  readonly isNueva               = signal(false);
  readonly guardando             = signal(false);

  readonly cargandoIA           = signal(false);
  readonly cooldownActivo        = signal(false);
  readonly cooldownRestante      = signal(0);
  readonly mensajeCopiadoVisible = signal(false);
  readonly mensajeCopiadoTexto   = signal('');
  readonly toastVisible          = signal(false);
  readonly toastMensaje          = signal('');

  // True cuando el editor debe mostrarse: plantilla seleccionada O modo nueva
  readonly isEditing = computed(() => !!this.plantillaSeleccionada() || this.isNueva());

  // Posición del cursor en el textarea (se actualiza en blur/click/keyup)
  private cursorPos = 0;
  private cooldownInterval: ReturnType<typeof setInterval> | null = null;
  private toastTimeout: ReturnType<typeof setTimeout> | null = null;

  readonly plantillasFiltradas = computed(() => {
    const q = this.searchPlantillas().toLowerCase().trim();
    if (!q) return this.plantillas();
    return this.plantillas().filter(
      p =>
        p.nombre.toLowerCase().includes(q) ||
        (p.categoria?.toLowerCase().includes(q) ?? false),
    );
  });

  ngOnDestroy(): void {
    if (this.cooldownInterval) clearInterval(this.cooldownInterval);
    if (this.toastTimeout)     clearTimeout(this.toastTimeout);
  }

  seleccionarPlantilla(plantilla: Plantilla): void {
    this.plantillaSeleccionada.set(plantilla);
    this.nombreActual.set(plantilla.nombre);
    this.mensajeActual.set(plantilla.contenido);
    this.cursorPos = plantilla.contenido.length;
    this.isNueva.set(false);
  }

  nuevaPlantilla(): void {
    this.plantillaSeleccionada.set(null);
    this.nombreActual.set('');
    this.mensajeActual.set('');
    this.cursorPos = 0;
    this.isNueva.set(true);
  }

  onNombreInput(event: Event): void {
    this.nombreActual.set((event.target as HTMLInputElement).value);
  }

  guardarPlantilla(): void {
    const nombre    = this.nombreActual().trim();
    const contenido = this.mensajeActual();
    if (!nombre) return;

    this.guardando.set(true);

    if (this.isNueva()) {
      // TODO: Integrar con POST /api/vault/plantillas cuando el backend esté listo.
      //   Body:  { nombre, contenido, idioma: 'es', categoria: null }
      //   Resp:  { ok: boolean, plantilla: Plantilla }
      //
      // this.http.post<{ ok: boolean; plantilla: Plantilla }>(
      //   '/api/vault/plantillas',
      //   { nombre, contenido, idioma: 'es', categoria: null }
      // ).subscribe({
      //   next: res => {
      //     this.plantillas.update(list => [res.plantilla, ...list]);
      //     this.seleccionarPlantilla(res.plantilla);
      //     this.guardando.set(false);
      //   },
      //   error: () => {
      //     this.guardando.set(false);
      //     this.mostrarToast('Error al crear la plantilla. Inténtalo de nuevo.');
      //   },
      // });

      // ── INICIO DATOS MOCK ──────────────────────────────────────────────────
      // TODO: Eliminar este bloque al integrar POST /api/vault/plantillas
      setTimeout(() => {
        const creada: Plantilla = {
          id: `mock-nueva-${Date.now()}`,
          nombre,
          contenido,
          idioma: 'es',
          categoria: null,
          activa: true,
        };
        this.plantillas.update(list => [creada, ...list]);
        this.seleccionarPlantilla(creada);
        this.guardando.set(false);
      }, 500);
      // ── FIN DATOS MOCK ────────────────────────────────────────────────────

    } else {
      const id = this.plantillaSeleccionada()!.id;

      // TODO: Integrar con PUT /api/vault/plantillas/<id> cuando el backend esté listo.
      //   Body:  { nombre, contenido }
      //   Resp:  { ok: boolean, plantilla: Plantilla }
      //
      // this.http.put<{ ok: boolean; plantilla: Plantilla }>(
      //   `/api/vault/plantillas/${id}`,
      //   { nombre, contenido }
      // ).subscribe({
      //   next: res => {
      //     this.plantillas.update(list => list.map(p => p.id === id ? res.plantilla : p));
      //     this.plantillaSeleccionada.set(res.plantilla);
      //     this.nombreActual.set(res.plantilla.nombre);
      //     this.guardando.set(false);
      //   },
      //   error: () => {
      //     this.guardando.set(false);
      //     this.mostrarToast('Error al guardar los cambios. Inténtalo de nuevo.');
      //   },
      // });

      // ── INICIO DATOS MOCK ──────────────────────────────────────────────────
      // TODO: Eliminar este bloque al integrar PUT /api/vault/plantillas/<id>
      setTimeout(() => {
        const actualizada: Plantilla = { ...this.plantillaSeleccionada()!, nombre, contenido };
        this.plantillas.update(list => list.map(p => p.id === id ? actualizada : p));
        this.plantillaSeleccionada.set(actualizada);
        this.nombreActual.set(actualizada.nombre);
        this.guardando.set(false);
      }, 500);
      // ── FIN DATOS MOCK ────────────────────────────────────────────────────
    }
  }

  onSearchPlantillas(event: Event): void {
    this.searchPlantillas.set((event.target as HTMLInputElement).value);
  }

  onMensajeInput(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    this.mensajeActual.set(textarea.value);
    this.cursorPos = textarea.selectionStart ?? this.mensajeActual().length;
  }

  // Registra la última posición del cursor para saber dónde insertar el placeholder
  onMensajeCursorChange(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    this.cursorPos = textarea.selectionStart ?? this.mensajeActual().length;
  }

  onPlaceholderSeleccionado(option: DropdownOption): void {
    this.placeholderSeleccionado.set(option);
  }

  // Inserta el placeholder seleccionado en la posición donde estaba el cursor
  insertarPlaceholder(): void {
    const placeholder = this.placeholderSeleccionado();
    if (!placeholder) return;

    const msg   = this.mensajeActual();
    const pos   = this.cursorPos;
    const nuevo = msg.slice(0, pos) + placeholder.value + msg.slice(pos);
    const nuevoCursor = pos + placeholder.value.length;

    this.mensajeActual.set(nuevo);
    this.cursorPos = nuevoCursor;

    // Restaurar foco y posición del cursor en el textarea tras actualizar el DOM
    const el = this.mensajeTextareaRef?.nativeElement;
    if (el) {
      el.value = nuevo;
      setTimeout(() => {
        el.focus();
        el.setSelectionRange(nuevoCursor, nuevoCursor);
      });
    }
  }

  refinarConIA(): void {
    // Si el cooldown está activo, mostrar toast explicativo en lugar de hacer la petición
    if (this.cooldownActivo()) {
      this.mostrarToast(`Espera ${this.cooldownRestante()} segundos antes de volver a refinar.`);
      return;
    }

    const contenido = this.mensajeActual();
    if (!contenido.trim()) return;

    this.cargandoIA.set(true);

    // TODO: Integrar con POST /api/vault/generar-mensaje cuando el backend esté listo.
    //   Body:   { plantilla_id: string | null, contenido: string, opciones: {} }
    //   Resp:   { ok: boolean, mensaje: string, modelo_ia: string }
    //
    // this.http.post<{ ok: boolean; mensaje: string; modelo_ia: string }>(
    //   '/api/vault/generar-mensaje',
    //   {
    //     plantilla_id: this.plantillaSeleccionada()?.id ?? null,
    //     contenido,
    //     opciones: {},
    //   }
    // ).subscribe({
    //   next: res => {
    //     this.mensajeActual.set(res.mensaje);
    //     this.cargandoIA.set(false);
    //     this.iniciarCooldown();
    //   },
    //   error: () => {
    //     this.cargandoIA.set(false);
    //     this.mostrarToast('Error al conectar con la IA. Inténtalo de nuevo.');
    //   },
    // });

    // ── INICIO DATOS MOCK ────────────────────────────────────────────────────
    // TODO: Eliminar este bloque y descomentar la llamada HTTP de arriba
    setTimeout(() => {
      this.mensajeActual.set(contenido + '\n\n[Texto refinado por IA — simulación mock. Borrar al integrar backend.]');
      this.cargandoIA.set(false);
      this.iniciarCooldown();
    }, 1500);
    // ── FIN DATOS MOCK ────────────────────────────────────────────────────────
  }

  copiarMensaje(): void {
    const texto = this.mensajeActual();
    if (!texto.trim()) return;

    navigator.clipboard.writeText(texto).then(() => {
      const idx = Math.floor(Math.random() * MENSAJES_COPIADO.length);
      this.mensajeCopiadoTexto.set(MENSAJES_COPIADO[idx]);
      this.mensajeCopiadoVisible.set(true);
      setTimeout(() => this.mensajeCopiadoVisible.set(false), 2500);
    });
  }

  private iniciarCooldown(): void {
    this.cooldownActivo.set(true);
    this.cooldownRestante.set(COOLDOWN_SEGUNDOS);

    this.cooldownInterval = setInterval(() => {
      const restante = this.cooldownRestante() - 1;
      if (restante <= 0) {
        this.cooldownActivo.set(false);
        this.cooldownRestante.set(0);
        clearInterval(this.cooldownInterval!);
        this.cooldownInterval = null;
      } else {
        this.cooldownRestante.set(restante);
      }
    }, 1000);
  }

  private mostrarToast(mensaje: string): void {
    this.toastMensaje.set(mensaje);
    this.toastVisible.set(true);

    if (this.toastTimeout) clearTimeout(this.toastTimeout);
    this.toastTimeout = setTimeout(() => this.toastVisible.set(false), 4000);
  }
}
