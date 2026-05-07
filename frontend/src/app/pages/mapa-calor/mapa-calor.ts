// Date picker: flatpickr — elegido por ser ligero, sin Material Design,
// con CSS completamente sobreescribible y compatible con cualquier versión de Angular.
import { AfterViewInit, Component, ElementRef, OnDestroy, OnInit, ViewChild, WritableSignal, computed, inject, signal } from '@angular/core';
import flatpickr from 'flatpickr';
import { forkJoin, catchError, of } from 'rxjs';
import { NgIconComponent } from '@ng-icons/core';
import { BadgeComponent } from '../../components/atoms/badge/badge';
import { ButtonComponent } from '../../components/atoms/button/button';
import { AlertComponent } from '../../components/molecules/alert/alert';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { PanelSeccionComponent } from '../../components/organisms/panel-seccion/panel-seccion';
import { HeatmapGridComponent } from '../../components/organisms/heatmap-grid/heatmap-grid';
import { ApartamentosService } from '../../services/apartamentos.service';
import { MapaCalorService, DiaCalor, UmbralesCalor } from '../../services/mapa-calor.service';

@Component({
  selector: 'app-mapa-calor',
  templateUrl: './mapa-calor.html',
  styleUrl: './mapa-calor.scss',
  standalone: true,
  imports: [
    NgIconComponent,
    PageHeaderComponent,
    PanelSeccionComponent,
    BadgeComponent,
    ButtonComponent,
    AlertComponent,
    HeatmapGridComponent,
  ],
})
export class MapaCalorPageComponent implements OnInit, AfterViewInit, OnDestroy {

  private readonly apartamentosService = inject(ApartamentosService);
  private readonly mapaCalorService    = inject(MapaCalorService);

  readonly pmsActivo    = signal(false);
  readonly pmsProveedor = signal<string | null>(null);
  readonly cargando     = signal(false);
  readonly error        = signal<string | null>(null);
  readonly fechaDesde   = signal<string | null>(null);
  readonly fechaHasta   = signal<string | null>(null);
  readonly archivoCheckins  = signal<File | null>(null);
  readonly archivoCheckouts = signal<File | null>(null);
  readonly diasCalor    = signal<DiaCalor[]>([]);
  readonly umbrales     = signal<UmbralesCalor>({ nivel1: 10, nivel2: 20, nivel3: 30 });
  readonly alertaValidacion = signal<string | null>(null);

  readonly puedeGenerar = computed(() => {
    const fechasOk = !!this.fechaDesde() && !!this.fechaHasta();
    if (this.pmsActivo()) return fechasOk;
    return fechasOk && !!this.archivoCheckins();
  });

  @ViewChild('inputDesde') private readonly inputDesdeRef!: ElementRef<HTMLInputElement>;
  @ViewChild('inputHasta') private readonly inputHastaRef!: ElementRef<HTMLInputElement>;

  private _pickerDesde?: flatpickr.Instance;
  private _pickerHasta?: flatpickr.Instance;

  ngOnInit(): void {
    forkJoin({
      pms:      this.apartamentosService.getPmsStatus().pipe(catchError(() => of(null))),
      umbrales: this.mapaCalorService.getUmbrales().pipe(catchError(() => of(null))),
    }).subscribe(({ pms, umbrales }) => {
      this.pmsActivo.set(!!(pms && pms.activo));
      this.pmsProveedor.set(pms?.proveedor ?? null);
      if (umbrales) this.umbrales.set(umbrales);
    });
  }

  ngAfterViewInit(): void {
    const baseConfig = { dateFormat: 'Y-m-d', locale: { firstDayOfWeek: 1 } };

    this._pickerDesde = flatpickr(this.inputDesdeRef.nativeElement, {
      ...baseConfig,
      onChange: ([date]) => {
        const val = date ? date.toISOString().split('T')[0] : null;
        this.fechaDesde.set(val);
        if (val) this._pickerHasta?.set('minDate', val);
      },
    }) as flatpickr.Instance;

    this._pickerHasta = flatpickr(this.inputHastaRef.nativeElement, {
      ...baseConfig,
      onChange: ([date]) => {
        this.fechaHasta.set(date ? date.toISOString().split('T')[0] : null);
      },
    }) as flatpickr.Instance;
  }

  ngOnDestroy(): void {
    this._pickerDesde?.destroy();
    this._pickerHasta?.destroy();
  }

  onArchivoSeleccionado(event: Event, target: WritableSignal<File | null>): void {
    const input = event.target as HTMLInputElement;
    target.set(input.files?.[0] ?? null);
    input.value = '';
  }

  generar(): void {
    this.alertaValidacion.set(null);

    if (!this.puedeGenerar()) {
      this.alertaValidacion.set(
        !this.pmsActivo() && !this.archivoCheckins()
          ? 'Sube el archivo de check-ins antes de generar el mapa.'
          : 'Selecciona una fecha de inicio y una fecha de fin para continuar.'
      );
      return;
    }

    this.cargando.set(true);
    this.error.set(null);

    const fuente$ = this.pmsActivo()
      ? this.mapaCalorService.generarDesdePms(this.fechaDesde()!, this.fechaHasta()!)
      : this.mapaCalorService.generarDesdeXlsx(
          this.archivoCheckins()!,
          this.archivoCheckouts() ?? undefined,
          this.fechaDesde()!,
          this.fechaHasta()!,
        );

    fuente$.subscribe({
      next: res => {
        this.diasCalor.set(res.dias);
        this.cargando.set(false);
      },
      error: err => {
        this.error.set(err?.error?.errors?.[0] ?? err?.error?.message ?? 'Error al generar el mapa de calor.');
        this.cargando.set(false);
      },
    });
  }
}
