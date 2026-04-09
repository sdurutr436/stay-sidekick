import { Component, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';

// Formatos disponibles para las preferencias
type FormatoNombre = 'nombre_apellidos' | 'apellidos_nombre' | 'nombre_solo';
type FormatoApartamento = 'nota' | 'etiqueta' | 'ninguno';

interface PreferenciasContactos {
  formato_nombre_contacto: FormatoNombre;
  incluir_apartamento_contacto: boolean;
  formato_apartamento_contacto: FormatoApartamento;
  incluir_checkin_contacto: boolean;
}

// ── MOCK STATE ─────────────────────────────────────────────────────────────────
// TODO: Eliminar este bloque y sustituir por llamadas reales al backend:
//   - GET /api/contactos/google/status       → googleConectado, ultimoSync
//   - GET /api/contactos/preferencias         → preferencias
//   - POST /api/contactos/sync                → lanzar sincronizacion
//   - DELETE /api/contactos/google/disconnect → desconectar
//   - POST /api/contactos/export/csv          → descargar CSV
const MOCK_GOOGLE_ESTADO = {
  conectado: false,
  ultimoSync: null as string | null,
};

const MOCK_PREFERENCIAS: PreferenciasContactos = {
  formato_nombre_contacto: 'nombre_apellidos',
  incluir_apartamento_contacto: true,
  formato_apartamento_contacto: 'nota',
  incluir_checkin_contacto: true,
};
// ── FIN MOCK STATE ─────────────────────────────────────────────────────────────

@Component({
  selector: 'app-sincronizador-contactos',
  templateUrl: './sincronizador-contactos.html',
  styleUrl: './sincronizador-contactos.scss',
  standalone: true,
  imports: [FormsModule],
})
export class SincronizadorContactosPageComponent {

  // Estado de conexion con Google
  readonly googleConectado = signal(MOCK_GOOGLE_ESTADO.conectado);
  readonly ultimoSync = signal<string | null>(MOCK_GOOGLE_ESTADO.ultimoSync);
  readonly syncEnCurso = signal(false);

  // Preferencias del formulario
  readonly preferencias = signal<PreferenciasContactos>({ ...MOCK_PREFERENCIAS });

  // Computed para saber si el formulario de apartamento es relevante
  readonly mostrarFormatoApartamento = computed(
    () => this.preferencias().incluir_apartamento_contacto,
  );

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

  // ── Conexion Google ──────────────────────────────────────────────────────────

  connectarGoogle(): void {
    // TODO: GET /api/contactos/google/auth → obtener URL → window.location.href = url
    console.warn('[sincronizador-contactos] conectar Google — pendiente de integrar');
  }

  desconectarGoogle(): void {
    // TODO: DELETE /api/contactos/google/disconnect → googleConectado.set(false)
    console.warn('[sincronizador-contactos] desconectar Google — pendiente de integrar');
  }

  // ── Preferencias ─────────────────────────────────────────────────────────────

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
    // TODO: PUT /api/contactos/preferencias con preferencias()
    console.warn('[sincronizador-contactos] guardar preferencias — pendiente de integrar', this.preferencias());
  }

  // ── Sincronizacion ────────────────────────────────────────────────────────────

  lanzarSync(): void {
    if (this.syncEnCurso()) return;
    // TODO: POST /api/contactos/sync → actualizar ultimoSync tras respuesta
    this.syncEnCurso.set(true);
    console.warn('[sincronizador-contactos] lanzar sync — pendiente de integrar');
    // Mock: simula fin de operacion
    setTimeout(() => {
      this.syncEnCurso.set(false);
      this.ultimoSync.set(new Date().toISOString());
    }, 1500);
  }

  exportarCsv(): void {
    // TODO: POST /api/contactos/export/csv → descargar fichero CSV de la respuesta
    console.warn('[sincronizador-contactos] exportar CSV — pendiente de integrar');
  }
}
