import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AccordionItemComponent } from './accordion-item';

describe('AccordionItemComponent', () => {
  let fixture: ComponentFixture<AccordionItemComponent>;
  let component: AccordionItemComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [AccordionItemComponent] }).compileComponents();
    fixture = TestBed.createComponent(AccordionItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Valores iniciales', () => {
    it('debería tener titulo vacío por defecto', () => {
      expect(component.titulo).toBe('');
    });

    it('debería tener count 0 por defecto', () => {
      expect(component.count).toBe(0);
    });

    it('debería estar cerrado por defecto (abierto=false)', () => {
      expect(component.abierto).toBe(false);
    });
  });

  describe('@Input titulo', () => {
    it('debería reflejar el titulo en el componente', () => {
      component.titulo = 'Sección principal';
      fixture.detectChanges();
      expect(component.titulo).toBe('Sección principal');
    });
  });

  describe('@Input count', () => {
    it('debería reflejar el count en el componente', () => {
      component.count = 5;
      fixture.detectChanges();
      expect(component.count).toBe(5);
    });
  });

  describe('@Input abierto', () => {
    it('debería reflejar abierto=true cuando se establece', () => {
      component.abierto = true;
      fixture.detectChanges();
      expect(component.abierto).toBe(true);
    });
  });
});
