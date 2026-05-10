import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { AlertComponent } from './alert';

describe('AlertComponent', () => {
  let fixture: ComponentFixture<AlertComponent>;
  let component: AlertComponent;

  async function create(preset: { visible?: boolean; dismissible?: boolean; type?: 'info' | 'success' | 'error' | 'warning' } = {}) {
    await TestBed.configureTestingModule({ imports: [AlertComponent] }).compileComponents();
    fixture = TestBed.createComponent(AlertComponent);
    component = fixture.componentInstance;
    if (preset.visible !== undefined) component.visible = preset.visible;
    if (preset.dismissible !== undefined) component.dismissible = preset.dismissible;
    if (preset.type !== undefined) component.type = preset.type;
    fixture.detectChanges();
  }

  beforeEach(() => TestBed.resetTestingModule());

  describe('Creación', () => {
    it('debería crearse correctamente', async () => {
      await create();
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses (getter)', () => {
    it('debería incluir alert--info por defecto', async () => {
      await create();
      expect(component.hostClasses).toContain('alert--info');
    });

    it('debería incluir alert--error cuando type es error', async () => {
      await create({ type: 'error' });
      expect(component.hostClasses).toContain('alert--error');
    });

    it('debería incluir alert--success', async () => {
      await create({ type: 'success' });
      expect(component.hostClasses).toContain('alert--success');
    });

    it('debería incluir alert--warning', async () => {
      await create({ type: 'warning' });
      expect(component.hostClasses).toContain('alert--warning');
    });
  });

  describe('Visibilidad (@if visible)', () => {
    it('debería renderizar el alert cuando visible es true (por defecto)', async () => {
      await create();
      expect(fixture.debugElement.query(By.css('[role="alert"]'))).not.toBeNull();
    });

    it('NO debería renderizar el alert cuando visible=false en el renderizado inicial', async () => {
      await create({ visible: false });
      expect(fixture.debugElement.query(By.css('[role="alert"]'))).toBeNull();
    });
  });

  describe('Botón de cierre (@if dismissible)', () => {
    it('NO debería mostrar el botón de cierre cuando dismissible es false', async () => {
      await create({ dismissible: false });
      expect(fixture.debugElement.query(By.css('.alert__close'))).toBeNull();
    });

    it('debería mostrar el botón de cierre cuando dismissible es true', async () => {
      await create({ dismissible: true });
      expect(fixture.debugElement.query(By.css('.alert__close'))).not.toBeNull();
    });
  });

  describe('dismiss() via clic (evento Angular que marca OnPush dirty)', () => {
    it('debería emitir dismissed al hacer clic en el botón de cierre', async () => {
      await create({ dismissible: true });
      let dismissed = false;
      component.dismissed.subscribe(() => (dismissed = true));
      fixture.debugElement.query(By.css('.alert__close')).nativeElement.click();
      expect(dismissed).toBe(true);
    });

    it('debería establecer visible=false internamente tras dismiss()', async () => {
      await create({ dismissible: true });
      component.dismiss();
      expect(component.visible).toBe(false);
    });

    it('debería ocultar el alert del DOM tras clic en cerrar', async () => {
      await create({ dismissible: true });
      fixture.debugElement.query(By.css('.alert__close')).nativeElement.click();
      fixture.detectChanges();
      expect(fixture.debugElement.query(By.css('[role="alert"]'))).toBeNull();
    });
  });
});
