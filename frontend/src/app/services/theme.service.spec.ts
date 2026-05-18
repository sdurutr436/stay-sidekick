import { TestBed } from '@angular/core/testing';
import { ThemeService } from './theme.service';

describe('ThemeService', () => {
  let service: ThemeService;

  beforeEach(() => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
    document.documentElement.removeAttribute('data-theme');
    TestBed.configureTestingModule({});
    service = TestBed.inject(ThemeService);
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('theme (signal)', () => {
    it('debería tener un valor inicial válido (light o dark)', () => {
      expect(['light', 'dark']).toContain(service.theme());
    });
  });

  describe('setTheme', () => {
    it('debería aplicar la clase dark en el documento al elegir dark', () => {
      service.setTheme('dark');
      expect(document.documentElement.classList.contains('dark')).toBe(true);
      expect(document.documentElement.getAttribute('data-theme')).toBe('dark');
    });

    it('debería quitar la clase dark al elegir light', () => {
      service.setTheme('dark');
      service.setTheme('light');
      expect(document.documentElement.classList.contains('dark')).toBe(false);
      expect(document.documentElement.getAttribute('data-theme')).toBe('light');
    });

    it('debería persistir la preferencia en localStorage', () => {
      service.setTheme('dark');
      expect(localStorage.getItem('theme')).toBe('dark');
      service.setTheme('light');
      expect(localStorage.getItem('theme')).toBe('light');
    });
  });

  describe('toggle', () => {
    it('debería invertir el tema en cada llamada', () => {
      const initial = service.theme();
      service.toggle();
      expect(service.theme()).not.toBe(initial);
      service.toggle();
      expect(service.theme()).toBe(initial);
    });
  });

  describe('isDark', () => {
    it('debería reflejar el estado actual del tema', () => {
      service.setTheme('dark');
      expect(service.isDark()).toBe(true);
      service.setTheme('light');
      expect(service.isDark()).toBe(false);
    });
  });

  describe('persistencia desde localStorage', () => {
    it('debería leer el valor guardado en la inicialización', () => {
      localStorage.setItem('theme', 'dark');
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({});
      const fresh = TestBed.inject(ThemeService);
      expect(fresh.theme()).toBe('dark');
    });
  });

  describe('fallback a prefers-color-scheme', () => {
    let originalMatchMedia: typeof window.matchMedia;

    beforeEach(() => { originalMatchMedia = window.matchMedia; });
    afterEach(() => { window.matchMedia = originalMatchMedia; });

    it('debería resolver a dark si prefers-color-scheme:dark coincide y no hay valor guardado', () => {
      localStorage.removeItem('theme');
      window.matchMedia = ((query: string) => ({
        matches: query === '(prefers-color-scheme: dark)',
        media: query,
        addEventListener: () => {},
        removeEventListener: () => {},
      })) as unknown as typeof window.matchMedia;
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({});
      const fresh = TestBed.inject(ThemeService);
      expect(fresh.theme()).toBe('dark');
    });

    it('debería resolver a light si prefers-color-scheme:dark NO coincide y no hay valor guardado', () => {
      localStorage.removeItem('theme');
      window.matchMedia = ((query: string) => ({
        matches: false,
        media: query,
        addEventListener: () => {},
        removeEventListener: () => {},
      })) as unknown as typeof window.matchMedia;
      TestBed.resetTestingModule();
      TestBed.configureTestingModule({});
      const fresh = TestBed.inject(ThemeService);
      expect(fresh.theme()).toBe('light');
    });
  });
});
