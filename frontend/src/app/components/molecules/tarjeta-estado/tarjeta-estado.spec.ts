import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TarjetaEstadoComponent } from './tarjeta-estado';

describe('TarjetaEstadoComponent', () => {
  let fixture: ComponentFixture<TarjetaEstadoComponent>;
  let component: TarjetaEstadoComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TarjetaEstadoComponent] }).compileComponents();
    fixture = TestBed.createComponent(TarjetaEstadoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses', () => {
    it('debería retornar solo tarjeta-estado cuando destacada es false', () => {
      component.destacada = false;
      expect(component.hostClasses).toBe('tarjeta-estado');
    });

    it('debería incluir tarjeta-estado--destacada cuando destacada es true', () => {
      component.destacada = true;
      expect(component.hostClasses).toContain('tarjeta-estado--destacada');
    });
  });

  describe('@Input label, valor y sub', () => {
    it('debería reflejar los valores de entrada', () => {
      component.label = 'Total checkins';
      component.valor = '42';
      component.sub = 'esta semana';
      fixture.detectChanges();
      expect(component.label).toBe('Total checkins');
      expect(component.valor).toBe('42');
      expect(component.sub).toBe('esta semana');
    });
  });
});
