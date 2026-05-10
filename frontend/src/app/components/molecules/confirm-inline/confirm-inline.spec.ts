import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ConfirmInlineComponent } from './confirm-inline';

describe('ConfirmInlineComponent', () => {
  let fixture: ComponentFixture<ConfirmInlineComponent>;
  let component: ConfirmInlineComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [ConfirmInlineComponent] }).compileComponents();
    fixture = TestBed.createComponent(ConfirmInlineComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Visibilidad (OnPush)', () => {
    it('NO debería renderizar el componente cuando visible es false por defecto', () => {
      expect(fixture.debugElement.query(By.css('[role="group"]'))).toBeNull();
    });

    it('debería renderizar el componente cuando visible es true', () => {
      fixture.componentRef.setInput('visible', true);
      fixture.detectChanges();
      expect(fixture.debugElement.query(By.css('[role="group"]'))).not.toBeNull();
    });
  });

  describe('@Input mensaje (OnPush)', () => {
    it('debería mostrar el mensaje por defecto', () => {
      fixture.componentRef.setInput('visible', true);
      fixture.detectChanges();
      const span = fixture.debugElement.query(By.css('.confirm-inline__mensaje'));
      expect(span.nativeElement.textContent).toContain('¿Confirmar acción?');
    });

    it('debería mostrar el mensaje personalizado', () => {
      fixture.componentRef.setInput('visible', true);
      fixture.componentRef.setInput('mensaje', '¿Eliminar este registro?');
      fixture.detectChanges();
      const span = fixture.debugElement.query(By.css('.confirm-inline__mensaje'));
      expect(span.nativeElement.textContent).toContain('¿Eliminar este registro?');
    });
  });

  describe('@Output confirmado', () => {
    it('debería emitir confirmado al hacer clic en el botón de confirmar', () => {
      fixture.componentRef.setInput('visible', true);
      fixture.detectChanges();
      let emitted = false;
      component.confirmado.subscribe(() => (emitted = true));
      const btns = fixture.debugElement.queryAll(By.css('app-button'));
      btns[0].nativeElement.click();
      expect(emitted).toBe(true);
    });
  });

  describe('@Output cancelado', () => {
    it('debería emitir cancelado al hacer clic en el botón de cancelar', () => {
      fixture.componentRef.setInput('visible', true);
      fixture.detectChanges();
      let emitted = false;
      component.cancelado.subscribe(() => (emitted = true));
      const btns = fixture.debugElement.queryAll(By.css('app-button'));
      btns[1].nativeElement.click();
      expect(emitted).toBe(true);
    });
  });
});
