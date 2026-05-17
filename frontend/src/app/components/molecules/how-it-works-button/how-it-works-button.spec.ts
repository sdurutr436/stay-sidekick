import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { provideIcons } from '@ng-icons/core';
import { phosphorInfo } from '@ng-icons/phosphor-icons/regular';
import { HowItWorksButtonComponent } from './how-it-works-button';

describe('HowItWorksButtonComponent', () => {
  let fixture: ComponentFixture<HowItWorksButtonComponent>;
  let component: HowItWorksButtonComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HowItWorksButtonComponent],
      providers: [provideIcons({ phosphorInfo })],
    }).compileComponents();

    fixture = TestBed.createComponent(HowItWorksButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });

    it('debería renderizar el botón con la clase how-it-works-btn', () => {
      const btn = fixture.debugElement.query(By.css('.how-it-works-btn'));
      expect(btn).not.toBeNull();
    });

    it('debería mostrar el label por defecto "¿Cómo se usa?"', () => {
      const label = fixture.debugElement.query(By.css('.how-it-works-btn__label'));
      expect(label.nativeElement.textContent).toContain('¿Cómo se usa?');
    });
  });

  describe('Estado del modal', () => {
    it('debería iniciar cerrado (open = false)', () => {
      expect(component.open()).toBe(false);
    });

    it('abrir() debería poner open en true', () => {
      component.abrir();
      expect(component.open()).toBe(true);
    });

    it('cerrar() debería poner open en false', () => {
      component.abrir();
      component.cerrar();
      expect(component.open()).toBe(false);
    });

    it('clic en el botón debería abrir el modal', () => {
      const btn = fixture.debugElement.query(By.css('.how-it-works-btn'));
      btn.nativeElement.click();
      expect(component.open()).toBe(true);
    });
  });

  describe('@Input label personalizado', () => {
    it('debería reflejar un label personalizado en el DOM', () => {
      fixture.componentRef.setInput('label', 'Ayuda');
      fixture.detectChanges();
      const label = fixture.debugElement.query(By.css('.how-it-works-btn__label'));
      expect(label.nativeElement.textContent).toContain('Ayuda');
    });
  });
});
