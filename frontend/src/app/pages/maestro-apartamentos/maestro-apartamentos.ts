import { Component, computed, signal } from '@angular/core';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { TablaCrudComponent } from '../../components/organisms/tabla-crud/tabla-crud';

interface Apartamento {
  id: string;
  id_externo: string | null;
  nombre: string;
  direccion: string | null;
  ciudad: string | null;
  pms_origen: 'smoobu' | 'manual' | 'xlsx' | null;
  activo: boolean;
}

// ── MOCK DATA ──────────────────────────────────────────────────────────────────
// TODO: Eliminar este bloque completo cuando la integración con el backend esté activa.
//       Sustituir `apartamentos` por la señal que devuelva el servicio de API:
//       readonly apartamentos = toSignal(this.apartamentosService.listar(), { initialValue: [] });
const MOCK_APARTAMENTOS: Apartamento[] = [
  {
    id: 'mock-1',
    id_externo: '12345',
    nombre: 'Apartamento Sol y Mar',
    direccion: 'Calle del Mar 12, 2ºA',
    ciudad: 'Málaga',
    pms_origen: 'smoobu',
    activo: true,
  },
  {
    id: 'mock-2',
    id_externo: null,
    nombre: 'Casa Rural El Almendro',
    direccion: 'Camino de la Fuente s/n',
    ciudad: 'Ronda',
    pms_origen: 'manual',
    activo: true,
  },
  {
    id: 'mock-3',
    id_externo: '67890',
    nombre: 'Ático Centro Histórico',
    direccion: 'Plaza Mayor 3, 4ºB',
    ciudad: 'Sevilla',
    pms_origen: 'xlsx',
    activo: false,
  },
];
// ── FIN MOCK DATA ──────────────────────────────────────────────────────────────

@Component({
  selector: 'app-maestro-apartamentos',
  templateUrl: './maestro-apartamentos.html',
  styleUrl: './maestro-apartamentos.scss',
  standalone: true,
  imports: [PageHeaderComponent, ButtonComponent, BadgeComponent, TablaCrudComponent],
})
export class MaestroApartamentosPageComponent {

  readonly searchQuery = signal('');
  readonly selectedIds = signal<Set<string>>(new Set());

  // ── MOCK DATA BINDING ──────────────────────────────────────────────────────
  // TODO: Reemplazar con datos reales del backend (eliminar junto al bloque anterior)
  readonly apartamentos = signal<Apartamento[]>(MOCK_APARTAMENTOS);
  // ── FIN MOCK DATA BINDING ──────────────────────────────────────────────────

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

  readonly selectedCount = computed(() => this.selectedIds().size);

  readonly isAllSelected = computed(() => {
    const filtered = this.filteredApartamentos();
    return (
      filtered.length > 0 &&
      filtered.every(apt => this.selectedIds().has(apt.id))
    );
  });

  isSelected(id: string): boolean {
    return this.selectedIds().has(id);
  }

  toggleSelect(id: string): void {
    const next = new Set(this.selectedIds());
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    this.selectedIds.set(next);
  }

  toggleSelectAll(): void {
    if (this.isAllSelected()) {
      this.selectedIds.set(new Set());
    } else {
      this.selectedIds.set(
        new Set(this.filteredApartamentos().map(apt => apt.id)),
      );
    }
  }

  onSearch(value: string): void {
    this.searchQuery.set(value);
    this.selectedIds.set(new Set());
  }

  triggerXlsxImport(input: HTMLInputElement): void {
    input.click();
  }

  onXlsxFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    if (!file) return;
    // TODO: POST /api/apartamentos/import/xlsx con multipart/form-data
    console.warn('[maestro-apartamentos] importar XLSX — pendiente de integrar', file.name);
    input.value = ''; // Permite volver a seleccionar el mismo archivo
  }

  openAddDialog(): void {
    // TODO: Abrir modal/diálogo de alta manual de apartamento
    console.warn('[maestro-apartamentos] añadir apartamento — pendiente de implementar');
  }

  deleteSelected(): void {
    if (this.selectedCount() === 0) return;
    // TODO: DELETE /api/apartamentos/<id> para cada id seleccionado
    console.warn('[maestro-apartamentos] eliminar seleccionados — pendiente de integrar');
  }

  syncSmoobu(): void {
    // TODO: POST /api/apartamentos/sync/smoobu
    console.warn('[maestro-apartamentos] sincronizar Smoobu — pendiente de integrar');
  }

  originLabel(origen: string | null): string {
    const labels: Record<string, string> = {
      smoobu: 'Smoobu',
      manual: 'Manual',
      xlsx: 'Excel',
    };
    return labels[origen ?? 'manual'] ?? 'Manual';
  }
}
