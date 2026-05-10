import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormInputComponent } from './form-input';

describe('FormInputComponent', () => {
  let fixture: ComponentFixture<FormInputComponent>;
  let component: FormInputComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormInputComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormInputComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input (OnPush)', () => {
    it('debería reflejar el atributo id en el input nativo', () => {
      fixture.componentRef.setInput('id', 'mi-input');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).id).toBe('mi-input');
    });

    it('debería reflejar el type en el input nativo', () => {
      fixture.componentRef.setInput('type', 'email');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).type).toBe('email');
    });

    it('debería reflejar el placeholder', () => {
      fixture.componentRef.setInput('placeholder', 'Escribe aquí');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).placeholder).toBe('Escribe aquí');
    });

    it('debería reflejar el value', () => {
      fixture.componentRef.setInput('value', 'texto inicial');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).value).toBe('texto inicial');
    });

    it('debería deshabilitar el input cuando disabled es true', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).disabled).toBe(true);
    });

    it('debería soportar type password', () => {
      fixture.componentRef.setInput('type', 'password');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).type).toBe('password');
    });
  });

  describe('@Output valueChange', () => {
    it('debería emitir el valor del input cuando el usuario escribe', () => {
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const input = fixture.debugElement.query(By.css('input'));
      const nativeInput = input.nativeElement as HTMLInputElement;
      nativeInput.value = 'nuevo texto';
      nativeInput.dispatchEvent(new Event('input'));
      expect(emitted).toBe('nuevo texto');
    });

    it('debería emitir cadena vacía cuando el usuario borra el contenido', () => {
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const input = fixture.debugElement.query(By.css('input'));
      const nativeInput = input.nativeElement as HTMLInputElement;
      nativeInput.value = '';
      nativeInput.dispatchEvent(new Event('input'));
      expect(emitted).toBe('');
    });
  });
});
