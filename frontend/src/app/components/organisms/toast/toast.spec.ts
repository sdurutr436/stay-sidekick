import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ToastComponent } from './toast';
import { ToastService } from '../../../services/toast.service';

describe('ToastComponent', () => {
  let fixture: ComponentFixture<ToastComponent>;
  let toastService: ToastService;

  beforeEach(async () => {
    vi.useFakeTimers();
    await TestBed.configureTestingModule({ imports: [ToastComponent] }).compileComponents();
    fixture = TestBed.createComponent(ToastComponent);
    toastService = TestBed.inject(ToastService);
    toastService.clear();
    fixture.detectChanges();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('Renderizado', () => {
    it('NO debería renderizar la pila cuando no hay toasts', () => {
      expect(fixture.debugElement.query(By.css('.toast-stack'))).toBeNull();
    });

    it('debería renderizar un toast por cada elemento de la pila', () => {
      toastService.showSuccess('A');
      toastService.showError('B');
      fixture.detectChanges();
      const items = fixture.debugElement.queryAll(By.css('.toast'));
      expect(items.length).toBe(2);
    });

    it('debería aplicar la clase BEM toast--{variant}', () => {
      toastService.showWarning('Aviso');
      fixture.detectChanges();
      const item = fixture.debugElement.query(By.css('.toast'));
      expect((item.nativeElement as HTMLElement).classList.contains('toast--warning')).toBe(true);
    });

    it('debería mostrar el mensaje', () => {
      toastService.showInfo('Hola mundo');
      fixture.detectChanges();
      const mensaje = fixture.debugElement.query(By.css('.toast__mensaje'));
      expect(mensaje.nativeElement.textContent.trim()).toBe('Hola mundo');
    });
  });

  describe('Cierre manual', () => {
    it('debería retirar el toast al pulsar el botón de cerrar', () => {
      toastService.showSuccess('A');
      fixture.detectChanges();
      const btn = fixture.debugElement.query(By.css('.toast__cerrar')).nativeElement as HTMLButtonElement;
      btn.click();
      fixture.detectChanges();
      expect(fixture.debugElement.queryAll(By.css('.toast')).length).toBe(0);
    });
  });

  describe('Accesibilidad', () => {
    it('debería usar aria-live="assertive" en error', () => {
      toastService.showError('Err');
      fixture.detectChanges();
      const item = fixture.debugElement.query(By.css('.toast'));
      expect(item.nativeElement.getAttribute('aria-live')).toBe('assertive');
    });

    it('debería usar aria-live="polite" en success', () => {
      toastService.showSuccess('OK');
      fixture.detectChanges();
      const item = fixture.debugElement.query(By.css('.toast'));
      expect(item.nativeElement.getAttribute('aria-live')).toBe('polite');
    });
  });
});
