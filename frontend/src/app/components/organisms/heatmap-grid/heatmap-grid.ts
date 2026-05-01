import { ChangeDetectionStrategy, Component, computed, input } from '@angular/core';
import type { DiaCalor, UmbralesCalor } from '../../../services/mapa-calor.service';

const MESES_ABREV = ['ENE', 'FEB', 'MAR', 'ABR', 'MAY', 'JUN', 'JUL', 'AGO', 'SEP', 'OCT', 'NOV', 'DIC'];
const DIAS_SEMANA = ['L', 'M', 'X', 'J', 'V', 'S', 'D'];

function intensidad(valor: number, um: UmbralesCalor): string {
  if (valor <= 0) return '0';
  if (valor <= um.nivel1) return '25';
  if (valor <= um.nivel2) return '50';
  if (valor <= um.nivel3) return '75';
  return '100';
}

interface DiaCalorEnGrid extends DiaCalor {
  diaDeMes: string;
  mesAbrev: string;
  clasesCheckins: string;
  clasesCheckinsSolo: string;
  clasesCheckouts: string;
}

interface FilaCalendario {
  dias: DiaCalorEnGrid[];
  labelMes: string | null;
}

@Component({
  selector: 'app-heatmap-grid',
  templateUrl: './heatmap-grid.html',
  styleUrl: './heatmap-grid.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HeatmapGridComponent {
  readonly dias     = input<DiaCalor[]>([]);
  readonly umbrales = input<UmbralesCalor>({ nivel1: 10, nivel2: 20, nivel3: 30 });

  readonly diasSemana = DIAS_SEMANA;

  readonly soloCheckins = computed(() =>
    this.dias().length > 0 && this.dias().every(d => d.checkouts === 0)
  );

  readonly filas = computed((): FilaCalendario[] => {
    const dias = this.dias();
    if (!dias.length) return [];

    const um = this.umbrales();
    const sorted = [...dias].sort((a, b) => a.fecha.localeCompare(b.fecha));
    const filas: FilaCalendario[] = [];
    let mesActual = '';

    for (let i = 0; i < sorted.length; i += 7) {
      const slice = sorted.slice(i, i + 7);
      let labelMes: string | null = null;

      const diasEnGrid: DiaCalorEnGrid[] = slice.map(dia => {
        const mesIdx = parseInt(dia.fecha.split('-')[1]) - 1;
        const iC = intensidad(dia.checkins, um);
        const iO = intensidad(dia.checkouts, um);
        return {
          ...dia,
          diaDeMes: String(parseInt(dia.fecha.split('-')[2])),
          mesAbrev: MESES_ABREV[mesIdx],
          clasesCheckins:     `heatmap-grid__checkins heatmap-grid__checkins--i${iC}`,
          clasesCheckinsSolo: `heatmap-grid__checkins heatmap-grid__checkins--solo heatmap-grid__checkins--i${iC}`,
          clasesCheckouts:    `heatmap-grid__checkouts heatmap-grid__checkouts--i${iO}`,
        };
      });

      for (const dia of diasEnGrid) {
        if (!dia.mesAdyacente) {
          const mesKey = dia.fecha.substring(0, 7);
          if (mesKey !== mesActual) {
            mesActual = mesKey;
            labelMes = MESES_ABREV[parseInt(dia.fecha.split('-')[1]) - 1];
            break;
          }
        }
      }

      filas.push({ dias: diasEnGrid, labelMes });
    }

    return filas;
  });
}
