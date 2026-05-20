import { TestBed } from '@angular/core/testing';
import { ToastService } from './toast.service';

describe('ToastService', () => {
  let service: ToastService;

  beforeEach(() => {
    vi.useFakeTimers();
    TestBed.configureTestingModule({});
    service = TestBed.inject(ToastService);
    service.clear();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  describe('showSuccess', () => {
    it('debería emitir un toast con variante success', () => {
      service.showSuccess('¡Listo!');
      const toasts = service.toasts();
      expect(toasts.length).toBe(1);
      expect(toasts[0].variant).toBe('success');
      expect(toasts[0].mensaje).toBe('¡Listo!');
    });
  });

  describe('showError', () => {
    it('debería emitir un toast con variante error', () => {
      service.showError('Falló algo');
      const toasts = service.toasts();
      expect(toasts.length).toBe(1);
      expect(toasts[0].variant).toBe('error');
      expect(toasts[0].mensaje).toBe('Falló algo');
    });
  });

  describe('showWarning', () => {
    it('debería emitir un toast con variante warning', () => {
      service.showWarning('Atención');
      expect(service.toasts()[0].variant).toBe('warning');
    });
  });

  describe('showInfo', () => {
    it('debería emitir un toast con variante info', () => {
      service.showInfo('Info');
      expect(service.toasts()[0].variant).toBe('info');
    });
  });

  describe('Auto-dismiss', () => {
    it('debería eliminar el toast tras la duración indicada', () => {
      service.showSuccess('A', 1000);
      expect(service.toasts().length).toBe(1);
      vi.advanceTimersByTime(999);
      expect(service.toasts().length).toBe(1);
      vi.advanceTimersByTime(1);
      expect(service.toasts().length).toBe(0);
    });

    it('debería usar la duración por defecto cuando no se pasa parámetro', () => {
      service.showInfo('B');
      vi.advanceTimersByTime(4000);
      expect(service.toasts().length).toBe(0);
    });

    it('NO debería programar timeout cuando duracion es 0 (persistente)', () => {
      service.showWarning('Persistente', 0);
      vi.advanceTimersByTime(60000);
      expect(service.toasts().length).toBe(1);
    });
  });

  describe('dismiss', () => {
    it('debería retirar un toast por id', () => {
      service.showError('E1');
      const id = service.toasts()[0].id;
      service.dismiss(id);
      expect(service.toasts().length).toBe(0);
    });

    it('debería ser idempotente si el id no existe', () => {
      service.showSuccess('A');
      service.dismiss(9999);
      expect(service.toasts().length).toBe(1);
    });
  });

  describe('Apilamiento', () => {
    it('debería permitir múltiples toasts simultáneos con ids únicos', () => {
      service.showSuccess('A');
      service.showError('B');
      service.showWarning('C');
      const ids = service.toasts().map(t => t.id);
      expect(ids.length).toBe(3);
      expect(new Set(ids).size).toBe(3);
    });
  });

  describe('clear', () => {
    it('debería vaciar la pila y cancelar timeouts', () => {
      service.showSuccess('A');
      service.showError('B');
      service.clear();
      expect(service.toasts().length).toBe(0);
    });
  });
});
