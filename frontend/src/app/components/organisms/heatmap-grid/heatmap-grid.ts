import { Component, computed, input } from '@angular/core';
import type { DiaCalor, UmbralesCalor } from '../../../services/mapa-calor.service';

const MESES_ABREV = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
const DIAS_SEMANA = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];

interface FilaCalendario {
  dias: DiaCalor[];
  labelMes: string | null;
}

@Component({
  selector: 'app-heatmap-grid',
  templateUrl: './heatmap-grid.html',
  styleUrl: './heatmap-grid.scss',
  standalone: true,
})
export class HeatmapGridComponent {
  readonly dias     = input<DiaCalor[]>([]);
  readonly umbrales = input<UmbralesCalor>({ nivel1: 10, nivel2: 20, nivel3: 30 });

  readonly diasSemana = DIAS_SEMANA;

  // Si todos los días tienen checkouts === 0, se asume que no hay datos de checkout
  readonly soloCheckins = computed(() => this.dias().every(d => d.checkouts === 0));

  readonly filas = computed((): FilaCalendario[] => {
    const dias = this.dias();
    if (!dias.length) return [];

    const sorted = [...dias].sort((a, b) => a.fecha.localeCompare(b.fecha));
    const filas: FilaCalendario[] = [];
    let mesActual = '';

    for (let i = 0; i < sorted.length; i += 7) {
      const slice = sorted.slice(i, i + 7);
      let labelMes: string | null = null;

      for (const dia of slice) {
        if (!dia.mesAdyacente) {
          const mesKey = dia.fecha.substring(0, 7); // YYYY-MM
          if (mesKey !== mesActual) {
            mesActual = mesKey;
            labelMes = MESES_ABREV[parseInt(dia.fecha.split('-')[1]) - 1];
            break;
          }
        }
      }

      filas.push({ dias: slice, labelMes });
    }

    return filas;
  });

  clasesCheckins(valor: number): string {
    return `heatmap-grid__checkins heatmap-grid__checkins--i${this._intensidad(valor)}`;
  }

  clasesCheckinsSolo(valor: number): string {
    return `heatmap-grid__checkins heatmap-grid__checkins--solo heatmap-grid__checkins--i${this._intensidad(valor)}`;
  }

  clasesCheckouts(valor: number): string {
    return `heatmap-grid__checkouts heatmap-grid__checkouts--i${this._intensidad(valor)}`;
  }

  diaDeMes(fecha: string): string {
    return String(parseInt(fecha.split('-')[2]));
  }

  mesAbrev(fecha: string): string {
    return MESES_ABREV[parseInt(fecha.split('-')[1]) - 1].substring(0, 3).toUpperCase();
  }

  private _intensidad(valor: number): string {
    if (valor <= 0) return '0';
    const um = this.umbrales();
    if (valor <= um.nivel1) return '25';
    if (valor <= um.nivel2) return '50';
    if (valor <= um.nivel3) return '75';
    return '100';
  }
}
