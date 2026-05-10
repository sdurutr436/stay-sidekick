import { ComponentFixture, TestBed } from '@angular/core/testing';
import { HeatmapGridComponent } from './heatmap-grid';
import type { DiaCalor, UmbralesCalor } from '../../../services/mapa-calor.service';

const UMBRALES: UmbralesCalor = { nivel1: 5, nivel2: 10, nivel3: 15 };

function makeDia(fecha: string, checkins: number, checkouts: number, mesAdyacente = false): DiaCalor {
  return { fecha, checkins, checkouts, mesAdyacente };
}

function makeWeek(startDate: string, checkins: number, checkouts: number): DiaCalor[] {
  const days: DiaCalor[] = [];
  const base = new Date(startDate);
  for (let i = 0; i < 7; i++) {
    const d = new Date(base);
    d.setDate(base.getDate() + i);
    days.push(makeDia(d.toISOString().slice(0, 10), checkins, checkouts));
  }
  return days;
}

describe('HeatmapGridComponent', () => {
  let fixture: ComponentFixture<HeatmapGridComponent>;
  let component: HeatmapGridComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [HeatmapGridComponent] }).compileComponents();
    fixture = TestBed.createComponent(HeatmapGridComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('soloCheckins (computed)', () => {
    it('debería ser false cuando no hay días', () => {
      expect(component.soloCheckins()).toBe(false);
    });

    it('debería ser true cuando todos los días tienen checkout=0', () => {
      fixture.componentRef.setInput('dias', makeWeek('2024-06-03', 5, 0));
      expect(component.soloCheckins()).toBe(true);
    });

    it('debería ser false cuando algún día tiene checkout>0', () => {
      const dias = makeWeek('2024-06-03', 5, 0);
      dias[0].checkouts = 3;
      fixture.componentRef.setInput('dias', dias);
      expect(component.soloCheckins()).toBe(false);
    });
  });

  describe('filas (computed)', () => {
    it('debería retornar array vacío cuando no hay días', () => {
      fixture.componentRef.setInput('dias', []);
      expect(component.filas()).toEqual([]);
    });

    it('debería crear una fila para 7 días', () => {
      fixture.componentRef.setInput('dias', makeWeek('2024-06-03', 3, 1));
      fixture.componentRef.setInput('umbrales', UMBRALES);
      const filas = component.filas();
      expect(filas.length).toBe(1);
      expect(filas[0].dias.length).toBe(7);
    });

    it('debería crear dos filas para 14 días', () => {
      const dias = [
        ...makeWeek('2024-06-03', 3, 1),
        ...makeWeek('2024-06-10', 2, 0),
      ];
      fixture.componentRef.setInput('dias', dias);
      fixture.componentRef.setInput('umbrales', UMBRALES);
      expect(component.filas().length).toBe(2);
    });

    it('debería asignar la abreviatura del mes correctamente en cada día', () => {
      fixture.componentRef.setInput('dias', makeWeek('2024-01-01', 1, 1));
      fixture.componentRef.setInput('umbrales', UMBRALES);
      const dia = component.filas()[0].dias[0];
      expect(dia.mesAbrev).toBe('ENE');
    });
  });

  describe('clasesCheckins con umbrales', () => {
    it('debería asignar clase i0 cuando checkins es 0', () => {
      fixture.componentRef.setInput('dias', [makeDia('2024-06-01', 0, 0)]);
      fixture.componentRef.setInput('umbrales', UMBRALES);
      const dia = component.filas()[0].dias[0];
      expect(dia.clasesCheckins).toContain('--i0');
    });

    it('debería asignar clase i25 cuando checkins es igual al nivel1', () => {
      fixture.componentRef.setInput('dias', [makeDia('2024-06-01', 5, 0)]);
      fixture.componentRef.setInput('umbrales', UMBRALES);
      const dia = component.filas()[0].dias[0];
      expect(dia.clasesCheckins).toContain('--i25');
    });

    it('debería asignar clase i100 cuando checkins supera el nivel3', () => {
      fixture.componentRef.setInput('dias', [makeDia('2024-06-01', 20, 0)]);
      fixture.componentRef.setInput('umbrales', UMBRALES);
      const dia = component.filas()[0].dias[0];
      expect(dia.clasesCheckins).toContain('--i100');
    });
  });
});
