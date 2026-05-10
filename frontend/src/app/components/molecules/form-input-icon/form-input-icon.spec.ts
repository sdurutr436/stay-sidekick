import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormInputIconComponent } from './form-input-icon';

describe('FormInputIconComponent', () => {
  let fixture: ComponentFixture<FormInputIconComponent>;
  let component: FormInputIconComponent;

  function createWith(inputs: Partial<{ id: string; type: 'text' | 'email' | 'password'; placeholder: string; value: string }>) {
    fixture = TestBed.createComponent(FormInputIconComponent);
    component = fixture.componentInstance;
    Object.assign(component, inputs);
    fixture.detectChanges();
  }

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormInputIconComponent] }).compileComponents();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      createWith({});
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input', () => {
    it('debería reflejar el id en el input nativo', () => {
      createWith({ id: 'icon-input' });
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).id).toBe('icon-input');
    });

    it('debería reflejar el tipo password', () => {
      createWith({ type: 'password' });
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).type).toBe('password');
    });

    it('debería reflejar el placeholder', () => {
      createWith({ placeholder: 'Introduce tu email' });
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).placeholder).toBe('Introduce tu email');
    });

    it('debería reflejar el value', () => {
      createWith({ value: 'test@example.com' });
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).value).toBe('test@example.com');
    });
  });

  describe('@Output valueChange', () => {
    it('debería emitir el valor cuando el usuario escribe', () => {
      createWith({});
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const input = fixture.debugElement.query(By.css('input'));
      const nativeInput = input.nativeElement as HTMLInputElement;
      nativeInput.value = 'nuevo valor';
      nativeInput.dispatchEvent(new Event('input'));
      expect(emitted).toBe('nuevo valor');
    });
  });
});
