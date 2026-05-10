import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormFieldComponent } from './form-field';

describe('FormFieldComponent', () => {
  let fixture: ComponentFixture<FormFieldComponent>;
  let component: FormFieldComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormFieldComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormFieldComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('fieldClasses (getter)', () => {
    it('debería retornar form-field sin modificador cuando no hay error', () => {
      component.hasError = false;
      expect(component.fieldClasses).toBe('form-field');
    });

    it('debería retornar form-field--error cuando hasError es true', () => {
      component.hasError = true;
      expect(component.fieldClasses).toContain('form-field--error');
    });
  });

  describe('errorId (getter)', () => {
    it('debería construir el id de error como for + -error', () => {
      component.for = 'campo-nombre';
      expect(component.errorId).toBe('campo-nombre-error');
    });
  });

  describe('Mensaje de error condicional (OnPush)', () => {
    it('NO debería mostrar el error cuando hasError es false', () => {
      fixture.componentRef.setInput('hasError', false);
      fixture.componentRef.setInput('error', 'Campo requerido');
      fixture.detectChanges();
      expect(fixture.debugElement.query(By.css('.form-field__error'))).toBeNull();
    });

    it('debería mostrar el error cuando hasError y error están definidos', () => {
      fixture.componentRef.setInput('hasError', true);
      fixture.componentRef.setInput('error', 'Campo requerido');
      fixture.detectChanges();
      const errorEl = fixture.debugElement.query(By.css('.form-field__error'));
      expect(errorEl).not.toBeNull();
      expect(errorEl.nativeElement.textContent).toContain('Campo requerido');
    });

    it('NO debería mostrar error si hasError es true pero error está vacío', () => {
      fixture.componentRef.setInput('hasError', true);
      fixture.componentRef.setInput('error', '');
      fixture.detectChanges();
      expect(fixture.debugElement.query(By.css('.form-field__error'))).toBeNull();
    });
  });
});
