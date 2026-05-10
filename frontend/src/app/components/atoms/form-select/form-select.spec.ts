import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormSelectComponent } from './form-select';

describe('FormSelectComponent', () => {
  let fixture: ComponentFixture<FormSelectComponent>;
  let component: FormSelectComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormSelectComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormSelectComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input (OnPush)', () => {
    it('debería reflejar el id en el select nativo', () => {
      fixture.componentRef.setInput('id', 'sel-test');
      fixture.detectChanges();
      const sel = fixture.debugElement.query(By.css('select'));
      expect((sel.nativeElement as HTMLSelectElement).id).toBe('sel-test');
    });

    it('debería deshabilitar el select cuando disabled es true', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();
      const sel = fixture.debugElement.query(By.css('select'));
      expect((sel.nativeElement as HTMLSelectElement).disabled).toBe(true);
    });

    it('debería renderizar las opciones del @Input options', () => {
      fixture.componentRef.setInput('options', [
        { value: 'a', label: 'Opción A' },
        { value: 'b', label: 'Opción B' },
      ]);
      fixture.detectChanges();
      const opts = fixture.debugElement.queryAll(By.css('option'));
      expect(opts.length).toBe(2);
      expect((opts[0].nativeElement as HTMLOptionElement).value).toBe('a');
    });

    it('debería reflejar el value seleccionado', () => {
      fixture.componentRef.setInput('options', [{ value: 'x', label: 'X' }, { value: 'y', label: 'Y' }]);
      fixture.detectChanges();
      fixture.componentRef.setInput('value', 'y');
      fixture.detectChanges();
      const sel = fixture.debugElement.query(By.css('select'));
      expect((sel.nativeElement as HTMLSelectElement).value).toBe('y');
    });
  });

  describe('@Output valueChange', () => {
    it('debería emitir el valor seleccionado al cambiar la opción', () => {
      fixture.componentRef.setInput('options', [{ value: 'op1', label: 'Op 1' }, { value: 'op2', label: 'Op 2' }]);
      fixture.detectChanges();
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const sel = fixture.debugElement.query(By.css('select'));
      const nativeSel = sel.nativeElement as HTMLSelectElement;
      nativeSel.value = 'op2';
      nativeSel.dispatchEvent(new Event('change'));
      expect(emitted).toBe('op2');
    });
  });
});
