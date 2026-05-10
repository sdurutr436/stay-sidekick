import { TestBed } from '@angular/core/testing';
import { ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { authGuard } from './auth.guard';
import { AuthService } from '../services/auth.service';

function buildAuthMock(overrides: { isLoggedIn?: boolean; debeChangiarPassword?: boolean } = {}): Partial<AuthService> {
  return {
    isLoggedIn: () => overrides.isLoggedIn ?? true,
    get debeChangiarPassword() {
      return overrides.debeChangiarPassword ?? false;
    },
  };
}

const emptyRoute = {} as ActivatedRouteSnapshot;
const emptyState = {} as RouterStateSnapshot;

describe('authGuard', () => {
  afterEach(() => {
    vi.unstubAllGlobals();
    vi.restoreAllMocks();
  });

  it('debería retornar true cuando el usuario está autenticado y no debe cambiar contraseña', () => {
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: buildAuthMock({ isLoggedIn: true, debeChangiarPassword: false }) }],
    });
    const result = TestBed.runInInjectionContext(() => authGuard(emptyRoute, emptyState));
    expect(result).toBe(true);
  });

  it('debería retornar false y redirigir a /login cuando el usuario no está autenticado', () => {
    vi.stubGlobal('location', { href: '' });
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: buildAuthMock({ isLoggedIn: false }) }],
    });

    const result = TestBed.runInInjectionContext(() => authGuard(emptyRoute, emptyState));

    expect(result).toBe(false);
    expect((window.location as { href: string }).href).toContain('/login');
  });

  it('debería retornar false y redirigir a /cambio-password cuando debe cambiar contraseña', () => {
    vi.stubGlobal('location', { href: '' });
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: buildAuthMock({ isLoggedIn: true, debeChangiarPassword: true }) }],
    });

    const result = TestBed.runInInjectionContext(() => authGuard(emptyRoute, emptyState));

    expect(result).toBe(false);
    expect((window.location as { href: string }).href).toContain('/cambio-password');
  });

  it('debería comprobar isLoggedIn antes que debeChangiarPassword', () => {
    vi.stubGlobal('location', { href: '' });
    TestBed.configureTestingModule({
      providers: [{ provide: AuthService, useValue: buildAuthMock({ isLoggedIn: false, debeChangiarPassword: true }) }],
    });

    const result = TestBed.runInInjectionContext(() => authGuard(emptyRoute, emptyState));

    expect(result).toBe(false);
    expect((window.location as { href: string }).href).toContain('/login');
  });
});
