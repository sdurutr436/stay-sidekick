import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormLabelComponent } from './form-label';

describe('FormLabelComponent', () => {
  let fixture: ComponentFixture<FormLabelComponent>;
  let component: FormLabelComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormLabelComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormLabelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('@Input for (OnPush)', () => {
    it('debería tener el atributo for vacío por defecto', () => {
      const label = fixture.debugElement.query(By.css('label'));
      expect((label.nativeElement as HTMLLabelElement).htmlFor).toBe('');
    });

    it('debería reflejar el atributo for en el elemento label', () => {
      fixture.componentRef.setInput('for', 'mi-input-id');
      fixture.detectChanges();
      const label = fixture.debugElement.query(By.css('label'));
      expect((label.nativeElement as HTMLLabelElement).htmlFor).toBe('mi-input-id');
    });
  });
});
