import { Component, computed, signal } from '@angular/core';

interface Apartamento {
  id: string;
  id_externo: string | null;
  nombre: string;
  direccion: string | null;
  ciudad: string | null;
  pms_origen: 'smoobu' | 'manual' | 'xlsx' | null;
}

type ImportEstado =
  | { status: 'idle' }
  | { status: 'pendiente'; archivo: File }
  | { status: 'cargando' }
  | { status: 'exito'; creados: number; actualizados: number; advertencias: string[] }
  | { status: 'error'; mensaje: string };

// ── MOCK DATA ──────────────────────────────────────────────────────────────────
// TODO: Eliminar este bloque completo cuando la integración con el backend esté activa.
//       Sustituir `apartamentos` por la señal del servicio de API:
//       readonly apartamentos = toSignal(this.apartamentosService.listar(), { initialValue: [] });
//       Sustituir `pmsProveedor` por el proveedor devuelto por GET /api/pms/config.
const MOCK_APARTAMENTOS: Apartamento[] = [
  {
    id: 'mock-1',
    id_externo: '12345',
    nombre: 'Apartamento Sol y Mar',
    direccion: 'Calle del Mar 12, 2ºA',
    ciudad: 'Málaga',
    pms_origen: 'smoobu',
  },
  {
    id: 'mock-2',
    id_externo: null,
    nombre: 'Casa Rural El Almendro',
    direccion: 'Camino de la Fuente s/n',
    ciudad: 'Ronda',
    pms_origen: 'manual',
  },
  {
    id: 'mock-3',
    id_externo: '67890',
    nombre: 'Ático Centro Histórico',
    direccion: 'Plaza Mayor 3, 4ºB',
    ciudad: 'Sevilla',
    pms_origen: 'xlsx',
  },
];
// ── FIN MOCK DATA ──────────────────────────────────────────────────────────────

const PMS_LABELS: Record<string, string> = {
  smoobu:    'Smoobu',
  beds24:    'Beds24',
  hostaway:  'Hostaway',
  cloudbeds: 'Cloudbeds',
};

@Component({
  selector: 'app-maestro-apartamentos',
  templateUrl: './maestro-apartamentos.html',
  styleUrl: './maestro-apartamentos.scss',
  standalone: true,
})
export class MaestroApartamentosPageComponent {

  // ── MOCK PMS CONFIG ────────────────────────────────────────────────────────
  // TODO: Reemplazar con el proveedor de GET /api/pms/config (eliminar junto al bloque anterior)
  readonly pmsProveedor = signal<string | null>('smoobu');
  // ── FIN MOCK PMS CONFIG ────────────────────────────────────────────────────

  readonly pmsLabel = computed(() => {
    const p = this.pmsProveedor();
    return p ? (PMS_LABELS[p] ?? p) : null;
  });

  // ── MOCK DATA BINDING ──────────────────────────────────────────────────────
  // TODO: Reemplazar con datos reales del backend (eliminar junto al bloque anterior)
  readonly apartamentos = signal<Apartamento[]>(MOCK_APARTAMENTOS);
  // ── FIN MOCK DATA BINDING ──────────────────────────────────────────────────

  readonly searchQuery  = signal('');
  readonly selectedIds  = signal<Set<string>>(new Set());
  readonly importEstado = signal<ImportEstado>({ status: 'idle' });

  readonly filteredApartamentos = computed(() => {
    const q = this.searchQuery().toLowerCase().trim();
    if (!q) return this.apartamentos();
    return this.apartamentos().filter(
      apt =>
        apt.nombre.toLowerCase().includes(q) ||
        (apt.ciudad?.toLowerCase().includes(q) ?? false) ||
        (apt.direccion?.toLowerCase().includes(q) ?? false),
    );
  });

  readonly selectedCount  = computed(() => this.selectedIds().size);

  readonly isAllSelected = computed(() => {
    const filtered = this.filteredApartamentos();
    return (
      filtered.length > 0 &&
      filtered.every(apt => this.selectedIds().has(apt.id))
    );
  });

  // Helpers de acceso tipado para el @switch del template
  readonly importArchivo = computed(() => {
    const s = this.importEstado();
    return s.status === 'pendiente' ? s.archivo : null;
  });

  readonly importResultado = computed(() => {
    const s = this.importEstado();
    return s.status === 'exito' ? s : null;
  });

  readonly importError = computed(() => {
    const s = this.importEstado();
    return s.status === 'error' ? s.mensaje : null;
  });

  // ── Selección de filas ─────────────────────────────────────────────────────

  isSelected(id: string): boolean {
    return this.selectedIds().has(id);
  }

  toggleSelect(id: string): void {
    const next = new Set(this.selectedIds());
    next.has(id) ? next.delete(id) : next.add(id);
    this.selectedIds.set(next);
  }

  toggleSelectAll(): void {
    if (this.isAllSelected()) {
      this.selectedIds.set(new Set());
    } else {
      this.selectedIds.set(new Set(this.filteredApartamentos().map(a => a.id)));
    }
  }

  onSearch(event: Event): void {
    this.searchQuery.set((event.target as HTMLInputElement).value);
    this.selectedIds.set(new Set());
  }

  // ── Importación XLSX ───────────────────────────────────────────────────────

  triggerXlsxImport(input: HTMLInputElement): void {
    input.click();
  }

  onXlsxFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file  = input.files?.[0];
    if (!file) return;
    this.importEstado.set({ status: 'pendiente', archivo: file });
    input.value = ''; // permite volver a seleccionar el mismo archivo
  }

  confirmarImportacion(): void {
    this.importEstado.set({ status: 'cargando' });

    // TODO: POST /api/apartamentos/import/xlsx con multipart/form-data
    //       Cuando esté integrado, sustituir el setTimeout por la llamada HTTP
    //       y mapear la respuesta a los estados 'exito' / 'error'.
    setTimeout(() => {
      this.importEstado.set({
        status: 'exito',
        creados: 5,
        actualizados: 2,
        advertencias: [],
      });
    }, 1200);
  }

  cancelarImportacion(): void {
    this.importEstado.set({ status: 'idle' });
  }

  // ── Sincronización con PMS ─────────────────────────────────────────────────

  syncPms(): void {
    // TODO: POST /api/apartamentos/sync/smoobu (u otro proveedor según pmsProveedor())
    console.warn('[maestro-apartamentos] sincronizar PMS — pendiente de integrar');
  }

  // ── CRUD ───────────────────────────────────────────────────────────────────

  openAddDialog(): void {
    // TODO: Abrir modal/diálogo de alta manual de apartamento
    console.warn('[maestro-apartamentos] añadir apartamento — pendiente de implementar');
  }

  deleteSelected(): void {
    if (this.selectedCount() === 0) return;
    // TODO: DELETE /api/apartamentos/<id> para cada id seleccionado
    console.warn('[maestro-apartamentos] eliminar seleccionados — pendiente de integrar');
  }

  originLabel(origen: string | null): string {
    const labels: Record<string, string> = {
      smoobu: 'Smoobu',
      manual: 'Manual',
      xlsx:   'Excel',
    };
    return labels[origen ?? 'manual'] ?? 'Manual';
  }
}
