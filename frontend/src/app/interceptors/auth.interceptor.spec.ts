import { TestBed } from '@angular/core/testing';
import { provideHttpClient, withInterceptors, HttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { authInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';

function setupWithToken(token: string | null): { http: HttpClient; httpTesting: HttpTestingController } {
  TestBed.configureTestingModule({
    providers: [
      provideHttpClient(withInterceptors([authInterceptor])),
      provideHttpClientTesting(),
      { provide: AuthService, useValue: { getToken: () => token } },
    ],
  });
  return {
    http: TestBed.inject(HttpClient),
    httpTesting: TestBed.inject(HttpTestingController),
  };
}

describe('authInterceptor', () => {
  afterEach(() => TestBed.inject(HttpTestingController).verify());

  describe('con token presente', () => {
    it('debería añadir el header Authorization a peticiones /api/', () => {
      const { http, httpTesting } = setupWithToken('mi-token-jwt');
      http.get('/api/usuarios').subscribe();
      const req = httpTesting.expectOne('/api/usuarios');
      expect(req.request.headers.get('Authorization')).toBe('Bearer mi-token-jwt');
      req.flush({});
    });

    it('debería añadir el header a cualquier sub-ruta de /api/', () => {
      const { http, httpTesting } = setupWithToken('tok123');
      http.get('/api/perfil/integraciones').subscribe();
      const req = httpTesting.expectOne('/api/perfil/integraciones');
      expect(req.request.headers.get('Authorization')).toBe('Bearer tok123');
      req.flush({});
    });

    it('NO debería añadir Authorization a URLs que no contienen /api/', () => {
      const { http, httpTesting } = setupWithToken('mi-token-jwt');
      http.get('/assets/logo.svg').subscribe();
      const req = httpTesting.expectOne('/assets/logo.svg');
      expect(req.request.headers.get('Authorization')).toBeNull();
      req.flush('');
    });
  });

  describe('sin token', () => {
    it('NO debería añadir Authorization aunque la URL contenga /api/', () => {
      const { http, httpTesting } = setupWithToken(null);
      http.get('/api/usuarios').subscribe();
      const req = httpTesting.expectOne('/api/usuarios');
      expect(req.request.headers.get('Authorization')).toBeNull();
      req.flush({});
    });
  });

  describe('propagación de respuesta', () => {
    it('debería dejar pasar la respuesta original sin modificarla', () => {
      const { http, httpTesting } = setupWithToken('tok');
      let body: unknown;
      http.get('/api/test').subscribe(r => (body = r));
      httpTesting.expectOne('/api/test').flush({ ok: true, data: 42 });
      expect(body).toEqual({ ok: true, data: 42 });
    });
  });
});
