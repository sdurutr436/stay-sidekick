import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { FormTextareaComponent } from './form-textarea';

describe('FormTextareaComponent', () => {
  let fixture: ComponentFixture<FormTextareaComponent>;
  let component: FormTextareaComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FormTextareaComponent] }).compileComponents();
    fixture = TestBed.createComponent(FormTextareaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input (OnPush)', () => {
    it('debería reflejar el id en el textarea nativo', () => {
      fixture.componentRef.setInput('id', 'ta-test');
      fixture.detectChanges();
      const ta = fixture.debugElement.query(By.css('textarea'));
      expect((ta.nativeElement as HTMLTextAreaElement).id).toBe('ta-test');
    });

    it('debería reflejar el placeholder', () => {
      fixture.componentRef.setInput('placeholder', 'Escribe tu mensaje');
      fixture.detectChanges();
      const ta = fixture.debugElement.query(By.css('textarea'));
      expect((ta.nativeElement as HTMLTextAreaElement).placeholder).toBe('Escribe tu mensaje');
    });

    it('debería reflejar el value', () => {
      fixture.componentRef.setInput('value', 'contenido inicial');
      fixture.detectChanges();
      const ta = fixture.debugElement.query(By.css('textarea'));
      expect((ta.nativeElement as HTMLTextAreaElement).value).toBe('contenido inicial');
    });

    it('debería deshabilitar el textarea cuando disabled es true', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();
      const ta = fixture.debugElement.query(By.css('textarea'));
      expect((ta.nativeElement as HTMLTextAreaElement).disabled).toBe(true);
    });
  });

  describe('@Output valueChange', () => {
    it('debería emitir el texto cuando el usuario escribe en el textarea', () => {
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const ta = fixture.debugElement.query(By.css('textarea'));
      const nativeTa = ta.nativeElement as HTMLTextAreaElement;
      nativeTa.value = 'texto nuevo';
      nativeTa.dispatchEvent(new Event('input'));
      expect(emitted).toBe('texto nuevo');
    });
  });
});
