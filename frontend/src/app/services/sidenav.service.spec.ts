import { TestBed } from '@angular/core/testing';
import { SidenavService } from './sidenav.service';

describe('SidenavService', () => {
  let service: SidenavService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(SidenavService);
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(service).toBeTruthy();
    });
  });

  describe('isOpen (signal)', () => {
    it('debería tener valor inicial true', () => {
      expect(service.isOpen()).toBe(true);
    });

    it('debería cambiar a false tras llamar toggle()', () => {
      service.toggle();
      expect(service.isOpen()).toBe(false);
    });

    it('debería volver a true tras dos llamadas a toggle()', () => {
      service.toggle();
      service.toggle();
      expect(service.isOpen()).toBe(true);
    });
  });

  describe('isCollapsed (signal)', () => {
    it('debería tener valor inicial false', () => {
      expect(service.isCollapsed()).toBe(false);
    });

    it('debería cambiar a true tras llamar toggleCollapse()', () => {
      service.toggleCollapse();
      expect(service.isCollapsed()).toBe(true);
    });

    it('debería volver a false tras dos llamadas a toggleCollapse()', () => {
      service.toggleCollapse();
      service.toggleCollapse();
      expect(service.isCollapsed()).toBe(false);
    });
  });

  describe('toggle', () => {
    it('debería invertir el estado de isOpen en cada llamada', () => {
      expect(service.isOpen()).toBe(true);
      service.toggle();
      expect(service.isOpen()).toBe(false);
      service.toggle();
      expect(service.isOpen()).toBe(true);
    });
  });

  describe('toggleCollapse', () => {
    it('debería invertir el estado de isCollapsed en cada llamada', () => {
      expect(service.isCollapsed()).toBe(false);
      service.toggleCollapse();
      expect(service.isCollapsed()).toBe(true);
      service.toggleCollapse();
      expect(service.isCollapsed()).toBe(false);
    });
  });
});
