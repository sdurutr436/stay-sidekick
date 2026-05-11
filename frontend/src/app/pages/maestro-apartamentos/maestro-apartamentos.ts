import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { forkJoin, of } from 'rxjs';
import { catchError, map } from 'rxjs/operators';

import { NgIconComponent } from '@ng-icons/core';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { FormInputComponent } from '../../components/atoms/form-input/form-input';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { ConfirmInlineComponent } from '../../components/molecules/confirm-inline/confirm-inline';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { TablaCrudComponent } from '../../components/organisms/tabla-crud/tabla-crud';
import { ModalImportacionXlsxComponent } from './modal-importacion-xlsx/modal-importacion-xlsx';
import { ApartamentosService, Apartamento, ImportacionPreview } from '../../services/apartamentos.service';
import { AuthService } from '../../services/auth.service';

interface FilaEntrada {
  id: string;
  nombre: string;
  ciudad: string;
  direccion: string;
  idexterno: string;
  errores: { nombre?: boolean };
}

let _filaCounter = 0;

function crearFila(): FilaEntrada {
  return {
    id: `nueva-${++_filaCounter}`,
    nombre: '',
    ciudad: '',
    direccion: '',
    idexterno: '',
    errores: {},
  };
}

@Component({
  selector: 'app-maestro-apartamentos',
  templateUrl: './maestro-apartamentos.html',
  styleUrl: './maestro-apartamentos.scss',
  standalone: true,
  imports: [
    RouterLink,
    NgIconComponent,
    PageHeaderComponent,
    ButtonComponent,
    FormInputComponent,
    BadgeComponent,
    TablaCrudComponent,
    AlertComponent,
    ConfirmInlineComponent,
    ModalImportacionXlsxComponent,
  ],
})
export class MaestroApartamentosPageComponent implements OnInit {
  private readonly apartamentosService = inject(ApartamentosService);
  private readonly auth = inject(AuthService);

  readonly isAdmin = this.auth.isAdmin;

  readonly searchQuery = signal('');
  readonly selectedIds = signal<Set<string>>(new Set());
  readonly apartamentos = signal<Apartamento[]>([]);
  readonly cargando = signal(true);
  readonly error = signal<string | null>(null);
  readonly pmsActivo = signal(false);

  // ── Paginación ────────────────────────────────────────────────────────
  readonly PAGE_SIZE = 20;
  readonly paginaActual = signal(1);

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

  readonly totalPaginas = computed(() =>
    Math.max(1, Math.ceil(this.filteredApartamentos().length / this.PAGE_SIZE)),
  );

  readonly apartamentosPaginados = computed(() => {
    const page = this.paginaActual();
    const start = (page - 1) * this.PAGE_SIZE;
    return this.filteredApartamentos().slice(start, start + this.PAGE_SIZE);
  });

  readonly selectedCount = computed(() => this.selectedIds().size);

  readonly isAllSelected = computed(() => {
    const paginados = this.apartamentosPaginados();
    return paginados.length > 0 && paginados.every(apt => this.selectedIds().has(apt.id));
  });

  // ── Modo creación inline ──────────────────────────────────────────────
  readonly modoCreacion = signal(false);
  readonly filasEntrada = signal<FilaEntrada[]>([]);
  readonly guardando = signal(false);

  // ── Eliminar con confirmación ─────────────────────────────────────────
  readonly confirmandoEliminar = signal(false);
  readonly eliminando = signal(false);
  readonly alertaEliminar = signal<{ tipo: 'warning' | 'error'; mensaje: string } | null>(null);

  // ── Sincronización Smoobu ─────────────────────────────────────────────
  readonly sincronizando = signal(false);
  readonly syncAlerta = signal<{ tipo: 'success' | 'error'; mensaje: string } | null>(null);

  // ── Importación XLSX ──────────────────────────────────────────────────
  readonly xlsxPreview = signal<ImportacionPreview | null>(null);
  readonly xlsxModalAbierto = signal(false);
  readonly xlsxCargando = signal(false);
  private _xlsxFileParaConfirmar: File | null = null;

  ngOnInit(): void {
    this._cargarDatos();
  }

  private _cargarDatos(): void {
    this.cargando.set(true);
    this.error.set(null);
    forkJoin({
      lista: this.apartamentosService.listar().pipe(catchError(() => of(null))),
      pms: this.apartamentosService.getPmsStatus().pipe(catchError(() => of(undefined))),
    }).subscribe(({ lista, pms }) => {
      if (lista === null) {
        this.error.set('No se pudieron cargar los apartamentos. Inténtalo de nuevo.');
      } else {
        this.apartamentos.set(lista);
      }
      this.pmsActivo.set(!!(pms && pms.activo));
      this.cargando.set(false);
    });
  }

  // ── Selección ─────────────────────────────────────────────────────────

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
      this.selectedIds.set(new Set(this.apartamentosPaginados().map(apt => apt.id)));
    }
  }

  // ── Búsqueda y paginación ─────────────────────────────────────────────

  onSearch(value: string): void {
    this.searchQuery.set(value);
    this.selectedIds.set(new Set());
    this.paginaActual.set(1);
  }

  irPagina(n: number): void {
    this.paginaActual.set(Math.max(1, Math.min(n, this.totalPaginas())));
  }

  // ── Añadir apartamentos inline ────────────────────────────────────────

  activarModoCreacion(): void {
    this.filasEntrada.set([crearFila()]);
    this.modoCreacion.set(true);
  }

  cancelarCreacion(): void {
    this.modoCreacion.set(false);
    this.filasEntrada.set([]);
  }

  agregarFila(): void {
    this.filasEntrada.update(filas => [...filas, crearFila()]);
  }

  eliminarFila(id: string): void {
    this.filasEntrada.update(filas => filas.filter(f => f.id !== id));
  }

  actualizarFila(id: string, campo: keyof Omit<FilaEntrada, 'id' | 'errores'>, valor: string): void {
    this.filasEntrada.update(filas =>
      filas.map(f => {
        if (f.id !== id) return f;
        const actualizada = { ...f, [campo]: valor };
        if (campo === 'nombre') {
          actualizada.errores = { ...f.errores, nombre: false };
        }
        return actualizada;
      }),
    );
  }

  guardarCreacion(): void {
    const filas = this.filasEntrada();
    let hayError = false;
    const filasValidadas = filas.map(f => {
      const errores: FilaEntrada['errores'] = {};
      if (!f.nombre.trim()) {
        errores.nombre = true;
        hayError = true;
      }
      return { ...f, errores };
    });

    if (hayError) {
      this.filasEntrada.set(filasValidadas);
      return;
    }

    this.guardando.set(true);
    forkJoin(
      filas.map(f =>
        this.apartamentosService
          .crear({
            nombre: f.nombre.trim(),
            ciudad: f.ciudad.trim() || undefined,
            direccion: f.direccion.trim() || undefined,
            id_externo: f.idexterno.trim() || undefined,
          })
          .pipe(
            map(() => ({ ok: true })),
            catchError(() => of({ ok: false })),
          ),
      ),
    ).subscribe(() => {
      this.guardando.set(false);
      this.cancelarCreacion();
      this._cargarDatos();
    });
  }

  // ── Eliminar seleccionados ────────────────────────────────────────────

  pedirConfirmacionEliminar(): void {
    this.confirmandoEliminar.set(true);
    this.alertaEliminar.set(null);
  }

  cancelarEliminar(): void {
    this.confirmandoEliminar.set(false);
  }

  confirmarEliminar(): void {
    const ids = Array.from(this.selectedIds());
    if (!ids.length) return;

    this.eliminando.set(true);
    forkJoin(
      ids.map(id =>
        this.apartamentosService.eliminar(id).pipe(
          map(() => ({ id, ok: true as const })),
          catchError(() => of({ id, ok: false as const })),
        ),
      ),
    ).subscribe(resultados => {
      const fallidos = resultados.filter(r => !r.ok);
      this.eliminando.set(false);
      this.confirmandoEliminar.set(false);
      this.selectedIds.set(new Set());
      this._cargarDatos();

      if (fallidos.length > 0) {
        this.alertaEliminar.set({
          tipo: fallidos.length === ids.length ? 'error' : 'warning',
          mensaje: `No se pudieron eliminar ${fallidos.length} de ${ids.length} apartamento${ids.length !== 1 ? 's' : ''}.`,
        });
      }
    });
  }

  // ── Sincronización Smoobu ─────────────────────────────────────────────

  syncSmoobu(): void {
    this.sincronizando.set(true);
    this.syncAlerta.set(null);
    this.apartamentosService.sincronizarSmoobu().subscribe({
      next: resultado => {
        this.sincronizando.set(false);
        this._cargarDatos();
        this.syncAlerta.set({
          tipo: 'success',
          mensaje: `Sincronización completada: ${resultado.nuevos} nuevos, ${resultado.actualizados} actualizados.`,
        });
        setTimeout(() => this.syncAlerta.set(null), 5000);
      },
      error: () => {
        this.sincronizando.set(false);
        this.syncAlerta.set({ tipo: 'error', mensaje: 'Error al sincronizar con Smoobu.' });
      },
    });
  }

  // ── Importación XLSX ──────────────────────────────────────────────────

  triggerXlsxImport(input: HTMLInputElement): void {
    input.click();
  }

  onXlsxFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;
    const file = input.files?.[0];
    input.value = '';
    if (!file) return;

    this._xlsxFileParaConfirmar = file;
    this.xlsxCargando.set(true);
    this.apartamentosService.previewXlsx(file).subscribe({
      next: preview => {
        this.xlsxPreview.set(preview);
        this.xlsxCargando.set(false);
        this.xlsxModalAbierto.set(true);
      },
      error: () => {
        this.xlsxCargando.set(false);
        this._xlsxFileParaConfirmar = null;
        this.syncAlerta.set({ tipo: 'error', mensaje: 'No se pudo leer el archivo Excel.' });
      },
    });
  }

  confirmarImportacion(): void {
    const file = this._xlsxFileParaConfirmar;
    if (!file) return;

    this.xlsxCargando.set(true);
    this.apartamentosService.importarXlsx(file).subscribe({
      next: resultado => {
        this.xlsxCargando.set(false);
        this.xlsxModalAbierto.set(false);
        this.xlsxPreview.set(null);
        this._xlsxFileParaConfirmar = null;
        this._cargarDatos();
        this.syncAlerta.set({
          tipo: 'success',
          mensaje: `Importación completada: ${resultado.nuevos} nuevos, ${resultado.actualizados} actualizados.`,
        });
        setTimeout(() => this.syncAlerta.set(null), 5000);
      },
      error: () => {
        this.xlsxCargando.set(false);
        this.xlsxModalAbierto.set(false);
        this._xlsxFileParaConfirmar = null;
        this.syncAlerta.set({ tipo: 'error', mensaje: 'Error al importar el archivo Excel.' });
      },
    });
  }

  cerrarModalXlsx(): void {
    this.xlsxModalAbierto.set(false);
    this.xlsxPreview.set(null);
    this._xlsxFileParaConfirmar = null;
  }

  // ── Helpers ───────────────────────────────────────────────────────────

  originLabel(origen: string | null): string {
    const labels: Record<string, string> = {
      smoobu: 'Smoobu',
      manual: 'Manual',
      xlsx: 'Excel',
    };
    return labels[origen ?? 'manual'] ?? 'Manual';
  }
}
