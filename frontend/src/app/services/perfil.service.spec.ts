import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { PerfilService, PerfilData, IntegracionesData } from './perfil.service';

const mockPerfil: PerfilData = { email: 'u@test.com', rol: 'admin', empresa_id: 'e1', password_changed_at: null };
const mockIntegraciones: IntegracionesData = {
  pms: { configurado: true, proveedor: 'smoobu' },
  google: { configurado: false },
  ia: { configurado: true, proveedor: 'openai', modelo: 'gpt-4' },
};

describe('PerfilService', () => {
  let service: PerfilService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(PerfilService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('getPerfil', () => {
    it('debería retornar los datos del perfil de usuario', () => {
      let result: { ok: boolean; data: PerfilData } | undefined;
      service.getPerfil().subscribe(r => (result = r));
      httpTesting.expectOne('/api/perfil').flush({ ok: true, data: mockPerfil });
      expect(result?.data).toEqual(mockPerfil);
    });

    it('debería propagar error 401', () => {
      let err: unknown;
      service.getPerfil().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/perfil').flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
      expect(err).toBeTruthy();
    });
  });

  describe('cambiarPassword', () => {
    it('debería enviar las contraseñas y retornar ok true', () => {
      let result: { ok: boolean; errors?: string[] } | undefined;
      service.cambiarPassword('actual123', 'nueva456').subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/perfil/password');
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual({ password_actual: 'actual123', password_nueva: 'nueva456' });
      req.flush({ ok: true });
      expect(result?.ok).toBe(true);
    });

    it('debería retornar errors cuando la contraseña actual es incorrecta', () => {
      let result: { ok: boolean; errors?: string[] } | undefined;
      service.cambiarPassword('mal', 'nueva456').subscribe(r => (result = r));
      httpTesting.expectOne('/api/perfil/password').flush({ ok: false, errors: ['Contraseña actual incorrecta'] });
      expect(result?.errors).toContain('Contraseña actual incorrecta');
    });
  });

  describe('getIntegraciones', () => {
    it('debería retornar el estado de todas las integraciones', () => {
      let result: { ok: boolean; data: IntegracionesData } | undefined;
      service.getIntegraciones().subscribe(r => (result = r));
      httpTesting.expectOne('/api/perfil/integraciones').flush({ ok: true, data: mockIntegraciones });
      expect(result?.data.pms.configurado).toBe(true);
      expect(result?.data.google.configurado).toBe(false);
    });
  });

  describe('actualizarPMS', () => {
    it('debería enviar el proveedor y api_key para actualizar el PMS', () => {
      let result: { ok: boolean } | undefined;
      service.actualizarPMS('smoobu', 'key123').subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/perfil/integraciones/pms');
      expect(req.request.body).toEqual({ proveedor: 'smoobu', api_key: 'key123' });
      req.flush({ ok: true });
      expect(result?.ok).toBe(true);
    });

    it('debería propagar error 400 con errores de validación', () => {
      let err: unknown;
      service.actualizarPMS('', '').subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/perfil/integraciones/pms').flush({ errors: ['proveedor requerido'] }, { status: 400, statusText: 'Bad Request' });
      expect(err).toBeTruthy();
    });
  });

  describe('actualizarIA', () => {
    it('debería enviar proveedor, modelo y api_key', () => {
      service.actualizarIA('openai', 'gpt-4', 'sk-key').subscribe();
      const req = httpTesting.expectOne('/api/perfil/integraciones/ia');
      expect(req.request.body).toEqual({ proveedor: 'openai', modelo: 'gpt-4', api_key: 'sk-key' });
      req.flush({ ok: true });
    });

    it('debería enviar api_key null cuando no se especifica', () => {
      service.actualizarIA('openai', 'gpt-4').subscribe();
      const req = httpTesting.expectOne('/api/perfil/integraciones/ia');
      expect(req.request.body.api_key).toBeNull();
      req.flush({ ok: true });
    });
  });

  describe('eliminarPMS', () => {
    it('debería enviar DELETE y retornar ok', () => {
      let result: { ok: boolean } | undefined;
      service.eliminarPMS().subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/perfil/integraciones/pms');
      expect(req.request.method).toBe('DELETE');
      req.flush({ ok: true });
      expect(result?.ok).toBe(true);
    });
  });

  describe('eliminarIA', () => {
    it('debería enviar DELETE al endpoint de IA y retornar ok', () => {
      let result: { ok: boolean } | undefined;
      service.eliminarIA().subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/perfil/integraciones/ia');
      expect(req.request.method).toBe('DELETE');
      req.flush({ ok: true });
      expect(result?.ok).toBe(true);
    });
  });
});
