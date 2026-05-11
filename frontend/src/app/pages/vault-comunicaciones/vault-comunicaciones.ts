import { Component, ElementRef, OnDestroy, OnInit, ViewChild, computed, inject, signal } from '@angular/core';
import { NgIconComponent } from '@ng-icons/core';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ButtonComponent } from '../../components/atoms/button/button';
import { DropdownBuscadorComponent, DropdownOption } from '../../components/molecules/dropdown-buscador/dropdown-buscador';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { VaultService, Plantilla } from '../../services/vault.service';
import { PerfilService } from '../../services/perfil.service';

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

const COOLDOWN_SEGUNDOS = 60;

@Component({
  selector: 'app-vault-comunicaciones',
  templateUrl: './vault-comunicaciones.html',
  styleUrl: './vault-comunicaciones.scss',
  standalone: true,
  imports: [NgIconComponent, PageHeaderComponent, ButtonComponent, AlertComponent, DropdownBuscadorComponent],
})
export class VaultComunicacionesPageComponent implements OnInit, OnDestroy {
  private readonly vault  = inject(VaultService);
  private readonly perfil = inject(PerfilService);

  @ViewChild('mensajeTextarea') private mensajeTextareaRef!: ElementRef<HTMLTextAreaElement>;

  readonly plantillas = signal<Plantilla[]>([]);

  readonly searchPlantillas         = signal('');
  readonly plantillaSeleccionada    = signal<Plantilla | null>(null);
  readonly mensajeActual            = signal('');
  readonly placeholderSeleccionado  = signal<DropdownOption | null>(null);
  readonly placeholderOpciones      = signal<DropdownOption[]>(PLACEHOLDERS);

  readonly panelNuevaVariable  = signal(false);
  readonly nuevaVariableNombre = signal('');
  readonly guardandoVariable   = signal(false);

  readonly nombreActual = signal('');
  readonly isNueva      = signal(false);
  readonly guardando    = signal(false);

  readonly cargandoIA            = signal(false);
  readonly cooldownActivo        = signal(false);
  readonly cooldownRestante      = signal(0);
  readonly mensajeCopiadoVisible = signal(false);
  readonly mensajeCopiadoTexto   = signal('');
  readonly toastVisible          = signal(false);
  readonly toastMensaje          = signal('');

  readonly filtroCategoria = signal<string | null>(null);
  readonly filtroIdioma    = signal<string | null>(null);
  readonly editorIdioma    = signal('es');
  readonly editorCategoria = signal<string | null>(null);
  readonly idiomaDestino   = signal<string | null>(null);
  readonly traduciendo     = signal(false);
  readonly byokActivo      = signal(false);
  readonly usoIA           = signal<{ uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number } | null>(null);

  // True cuando el editor debe mostrarse: plantilla seleccionada O modo nueva
  readonly isEditing = computed(() => !!this.plantillaSeleccionada() || this.isNueva());

  // Posición del cursor en el textarea (se actualiza en blur/click/keyup)
  private cursorPos = 0;
  private cooldownInterval: ReturnType<typeof setInterval> | null = null;
  private toastTimeout: ReturnType<typeof setTimeout> | null = null;

  readonly plantillasFiltradas = computed(() => {
    const q    = this.searchPlantillas().toLowerCase().trim();
    const cat  = this.filtroCategoria();
    const lang = this.filtroIdioma();
    return this.plantillas().filter(p => {
      if (cat  && p.categoria !== cat)  return false;
      if (lang && p.idioma    !== lang) return false;
      if (q && !p.nombre.toLowerCase().includes(q) && !(p.categoria?.toLowerCase().includes(q) ?? false)) return false;
      return true;
    });
  });

  ngOnInit(): void {
    this.vault.getPlantillas().subscribe({ next: res => this.plantillas.set(res.plantillas) });
    this.perfil.getIntegraciones().subscribe({
      next: res => {
        this.byokActivo.set(res.data.ia.configurado);
        if (!this.byokActivo()) this.cargarUso();
      },
    });
  }

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
    this.editorIdioma.set(plantilla.idioma);
    this.editorCategoria.set(plantilla.categoria);
  }

  nuevaPlantilla(): void {
    this.plantillaSeleccionada.set(null);
    this.nombreActual.set('');
    this.mensajeActual.set('');
    this.cursorPos = 0;
    this.isNueva.set(true);
    this.editorIdioma.set('es');
    this.editorCategoria.set(null);
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
      this.vault.crearPlantilla({ nombre, contenido, idioma: this.editorIdioma(), categoria: this.editorCategoria() }).subscribe({
        next: res => {
          this.plantillas.update(list => [res.plantilla, ...list]);
          this.seleccionarPlantilla(res.plantilla);
          this.guardando.set(false);
        },
        error: () => {
          this.guardando.set(false);
          this.mostrarToast('Error al crear la plantilla. Inténtalo de nuevo.');
        },
      });
    } else {
      const id = this.plantillaSeleccionada()!.id;
      this.vault.actualizarPlantilla(id, { nombre, contenido, idioma: this.editorIdioma(), categoria: this.editorCategoria() }).subscribe({
        next: res => {
          this.plantillas.update(list => list.map(p => p.id === id ? res.plantilla : p));
          this.plantillaSeleccionada.set(res.plantilla);
          this.nombreActual.set(res.plantilla.nombre);
          this.guardando.set(false);
        },
        error: () => {
          this.guardando.set(false);
          this.mostrarToast('Error al guardar los cambios. Inténtalo de nuevo.');
        },
      });
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

  togglePanelNuevaVariable(): void {
    this.panelNuevaVariable.update(v => !v);
    if (!this.panelNuevaVariable()) this.nuevaVariableNombre.set('');
  }

  cerrarPanelNuevaVariable(): void {
    this.panelNuevaVariable.set(false);
    this.nuevaVariableNombre.set('');
  }

  onNuevaVariableNombre(event: Event): void {
    // Forzar mayúsculas y solo letras/números/guión bajo (formato de placeholder)
    const raw = (event.target as HTMLInputElement).value.toUpperCase().replace(/[^A-Z0-9_]/g, '');
    this.nuevaVariableNombre.set(raw);
    (event.target as HTMLInputElement).value = raw;
  }

  guardarNuevaVariable(): void {
    const clave = this.nuevaVariableNombre().trim();
    if (!clave) return;

    const valor = `{${clave}}`;

    // Evitar duplicados
    if (this.placeholderOpciones().some(o => o.value === valor)) {
      this.cerrarPanelNuevaVariable();
      return;
    }

    this.guardandoVariable.set(true);
    const nueva: DropdownOption = { value: valor, label: `${valor} — Variable personalizada` };
    this.placeholderOpciones.update(list => [...list, nueva]);
    this.guardandoVariable.set(false);
    this.cerrarPanelNuevaVariable();
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
    if (!this.plantillaSeleccionada()) return;

    this.cargandoIA.set(true);

    this.vault.mejorar(
      this.plantillaSeleccionada()!.id,
      this.mensajeActual(),
      this.editorIdioma(),
    ).subscribe({
      next: res => {
        this.mensajeActual.set(res.contenido);
        this.cargandoIA.set(false);
        this.iniciarCooldown();
        if (!this.byokActivo()) this.cargarUso();
      },
      error: err => {
        const msg = err?.error?.errors?.[0] ?? 'Error al conectar con la IA. Inténtalo de nuevo.';
        this.cargandoIA.set(false);
        this.mostrarToast(msg);
      },
    });
  }

  traducirConIA(): void {
    if (!this.idiomaDestino()) {
      this.mostrarToast('Selecciona un idioma de destino.');
      return;
    }
    if (this.cooldownActivo()) {
      this.mostrarToast(`Espera ${this.cooldownRestante()} segundos antes de traducir.`);
      return;
    }
    if (!this.plantillaSeleccionada()) return;

    this.traduciendo.set(true);

    this.vault.traducir(
      this.plantillaSeleccionada()!.id,
      this.mensajeActual(),
      this.idiomaDestino()!,
    ).subscribe({
      next: res => {
        this.mensajeActual.set(res.contenido);
        this.traduciendo.set(false);
        this.iniciarCooldown();
        if (!this.byokActivo()) this.cargarUso();
      },
      error: err => {
        const msg = err?.error?.errors?.[0] ?? 'Error al traducir. Inténtalo de nuevo.';
        this.traduciendo.set(false);
        this.mostrarToast(msg);
      },
    });
  }

  selectValue(event: Event): string {
    return (event.target as HTMLSelectElement).value;
  }

  onFiltroCategoria(value: string): void { this.filtroCategoria.set(value || null); }
  onFiltroIdioma(value: string):    void { this.filtroIdioma.set(value    || null); }
  onIdiomaDestino(value: string):   void { this.idiomaDestino.set(value   || null); }
  onEditorIdioma(value: string):    void { this.editorIdioma.set(value); }
  onEditorCategoria(value: string): void { this.editorCategoria.set(value || null); }

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

  private cargarUso(): void {
    this.vault.getUso().subscribe({ next: res => this.usoIA.set(res) });
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
