import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormCheckboxComponent } from './form-checkbox';

describe('FormCheckboxComponent', () => {
  let fixture: ComponentFixture<FormCheckboxComponent>;
  let component: FormCheckboxComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormCheckboxComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormCheckboxComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input (OnPush)', () => {
    it('debería reflejar checked=false por defecto', () => {
      const cb = fixture.debugElement.query(By.css('input[type="checkbox"]'));
      expect((cb.nativeElement as HTMLInputElement).checked).toBe(false);
    });

    it('debería reflejar checked=true cuando se establece vía setInput', () => {
      fixture.componentRef.setInput('checked', true);
      fixture.detectChanges();
      const cb = fixture.debugElement.query(By.css('input[type="checkbox"]'));
      expect((cb.nativeElement as HTMLInputElement).checked).toBe(true);
    });

    it('debería deshabilitar el checkbox cuando disabled es true', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();
      const cb = fixture.debugElement.query(By.css('input[type="checkbox"]'));
      expect((cb.nativeElement as HTMLInputElement).disabled).toBe(true);
    });
  });

  describe('@Output checkedChange', () => {
    it('debería emitir true cuando el usuario marca el checkbox', () => {
      let emitted: boolean | undefined;
      component.checkedChange.subscribe((v: boolean) => (emitted = v));
      const cb = fixture.debugElement.query(By.css('input[type="checkbox"]'));
      const nativeCb = cb.nativeElement as HTMLInputElement;
      nativeCb.checked = true;
      nativeCb.dispatchEvent(new Event('change'));
      expect(emitted).toBe(true);
    });

    it('debería emitir false cuando el usuario desmarca el checkbox', () => {
      fixture.componentRef.setInput('checked', true);
      fixture.detectChanges();
      let emitted: boolean | undefined;
      component.checkedChange.subscribe((v: boolean) => (emitted = v));
      const cb = fixture.debugElement.query(By.css('input[type="checkbox"]'));
      const nativeCb = cb.nativeElement as HTMLInputElement;
      nativeCb.checked = false;
      nativeCb.dispatchEvent(new Event('change'));
      expect(emitted).toBe(false);
    });
  });
});
