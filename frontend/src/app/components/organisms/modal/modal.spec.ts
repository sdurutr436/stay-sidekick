import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ModalComponent } from './modal';

describe('ModalComponent', () => {
  let fixture: ComponentFixture<ModalComponent>;
  let component: ModalComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [ModalComponent] }).compileComponents();
    fixture = TestBed.createComponent(ModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Visibilidad (OnPush)', () => {
    it('NO debería renderizar el overlay cuando open es false por defecto', () => {
      expect(fixture.debugElement.query(By.css('.modal__overlay'))).toBeNull();
    });

    it('debería renderizar el overlay cuando open es true', () => {
      fixture.componentRef.setInput('open', true);
      fixture.detectChanges();
      expect(fixture.debugElement.query(By.css('.modal__overlay'))).not.toBeNull();
    });
  });

  describe('@Input title (OnPush)', () => {
    it('debería mostrar el título en el header del modal', () => {
      fixture.componentRef.setInput('open', true);
      fixture.componentRef.setInput('title', 'Mi Modal');
      fixture.detectChanges();
      const title = fixture.debugElement.query(By.css('.modal__title'));
      expect(title.nativeElement.textContent).toContain('Mi Modal');
    });
  });

  describe('Botón de cierre', () => {
    it('debería emitir cerrar al hacer clic en el botón de cerrar', () => {
      fixture.componentRef.setInput('open', true);
      fixture.detectChanges();
      let cerrado = false;
      component.cerrar.subscribe(() => (cerrado = true));
      fixture.debugElement.query(By.css('.modal__close')).nativeElement.click();
      expect(cerrado).toBe(true);
    });
  });

  describe('onOverlayClick', () => {
    it('debería emitir cerrar cuando se hace clic en el overlay', () => {
      fixture.componentRef.setInput('open', true);
      fixture.detectChanges();
      let cerrado = false;
      component.cerrar.subscribe(() => (cerrado = true));

      const overlay = fixture.debugElement.query(By.css('.modal__overlay'));
      const fakeEvent = { target: overlay.nativeElement } as MouseEvent;
      component.onOverlayClick(fakeEvent);

      expect(cerrado).toBe(true);
    });

    it('NO debería emitir cerrar cuando se hace clic dentro del panel', () => {
      fixture.componentRef.setInput('open', true);
      fixture.detectChanges();
      let cerrado = false;
      component.cerrar.subscribe(() => (cerrado = true));

      const panel = fixture.debugElement.query(By.css('.modal__panel'));
      const fakeEvent = { target: panel.nativeElement } as MouseEvent;
      component.onOverlayClick(fakeEvent);

      expect(cerrado).toBe(false);
    });
  });
});
