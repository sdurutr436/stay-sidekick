import { TestBed } from '@angular/core/testing';
import { AuthService } from './auth.service';

function makeToken(overrides: Record<string, unknown> = {}, expired = false): string {
  const exp = expired
    ? Math.floor(Date.now() / 1000) - 100
    : Math.floor(Date.now() / 1000) + 3600;
  const payload = { exp, sub: 'u1', user_id: '1', empresa_id: 'e1', rol: 'operativo', ...overrides };
  return `hdr.${btoa(JSON.stringify(payload))}.sig`;
}

describe('AuthService', () => {
  let service: AuthService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AuthService);
    localStorage.clear();
  });

  afterEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  describe('getToken', () => {
    it('debería retornar null cuando no hay token almacenado', () => {
      expect(service.getToken()).toBeNull();
    });

    it('debería retornar el token almacenado en localStorage', () => {
      localStorage.setItem('ss_token', 'abc.def.ghi');
      expect(service.getToken()).toBe('abc.def.ghi');
    });
  });

  describe('isLoggedIn', () => {
    it('debería retornar false cuando no hay token', () => {
      expect(service.isLoggedIn()).toBe(false);
    });

    it('debería retornar false cuando el token no tiene formato JWT válido', () => {
      localStorage.setItem('ss_token', 'tokeninvalido');
      expect(service.isLoggedIn()).toBe(false);
    });

    it('debería retornar false cuando el payload base64 no es JSON válido', () => {
      localStorage.setItem('ss_token', 'hdr.!!!.sig');
      expect(service.isLoggedIn()).toBe(false);
    });

    it('debería retornar false cuando el token está expirado', () => {
      localStorage.setItem('ss_token', makeToken({}, true));
      expect(service.isLoggedIn()).toBe(false);
    });

    it('debería retornar true cuando el token es válido y no ha expirado', () => {
      localStorage.setItem('ss_token', makeToken());
      expect(service.isLoggedIn()).toBe(true);
    });
  });

  describe('getUser', () => {
    it('debería retornar null cuando no hay token', () => {
      expect(service.getUser()).toBeNull();
    });

    it('debería retornar el payload decodificado del token', () => {
      localStorage.setItem('ss_token', makeToken({ rol: 'admin', empresa_id: 'emp99' }));
      const user = service.getUser();
      expect(user?.rol).toBe('admin');
      expect(user?.empresa_id).toBe('emp99');
    });
  });

  describe('isAdmin', () => {
    it('debería retornar true cuando el rol es admin', () => {
      localStorage.setItem('ss_token', makeToken({ rol: 'admin' }));
      expect(service.isAdmin).toBe(true);
    });

    it('debería retornar false cuando el rol no es admin', () => {
      localStorage.setItem('ss_token', makeToken({ rol: 'operativo' }));
      expect(service.isAdmin).toBe(false);
    });

    it('debería retornar false cuando no hay token', () => {
      expect(service.isAdmin).toBe(false);
    });
  });

  describe('esSuperAdmin', () => {
    it('debería retornar true cuando es_superadmin es true', () => {
      localStorage.setItem('ss_token', makeToken({ es_superadmin: true }));
      expect(service.esSuperAdmin).toBe(true);
    });

    it('debería retornar false cuando es_superadmin es false', () => {
      localStorage.setItem('ss_token', makeToken({ es_superadmin: false }));
      expect(service.esSuperAdmin).toBe(false);
    });

    it('debería retornar false cuando no hay token', () => {
      expect(service.esSuperAdmin).toBe(false);
    });
  });

  describe('debeChangiarPassword', () => {
    it('debería retornar true cuando debe_cambiar_password es true', () => {
      localStorage.setItem('ss_token', makeToken({ debe_cambiar_password: true }));
      expect(service.debeChangiarPassword).toBe(true);
    });

    it('debería retornar false cuando debe_cambiar_password no está definido', () => {
      localStorage.setItem('ss_token', makeToken());
      expect(service.debeChangiarPassword).toBe(false);
    });
  });

  describe('logout', () => {
    it('debería eliminar el token de localStorage y redirigir a /login', () => {
      localStorage.setItem('ss_token', makeToken());
      const removeSpy = vi.spyOn(Storage.prototype, 'removeItem');
      vi.stubGlobal('location', { href: '' });

      service.logout();

      expect(removeSpy).toHaveBeenCalledWith('ss_token');
      expect((window.location as { href: string }).href).toBe('/login');
    });
  });
});
