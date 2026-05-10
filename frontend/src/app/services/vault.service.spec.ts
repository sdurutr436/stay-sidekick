import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { VaultService, Plantilla } from './vault.service';

const mockPlantilla: Plantilla = { id: 'p1', nombre: 'Bienvenida', contenido: 'Hola {nombre}', idioma: 'es', categoria: 'checkin', activa: true };

describe('VaultService', () => {
  let service: VaultService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(VaultService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('getPlantillas', () => {
    it('debería obtener todas las plantillas sin filtros', () => {
      let result: { ok: boolean; plantillas: Plantilla[] } | undefined;
      service.getPlantillas().subscribe(r => (result = r));
      const req = httpTesting.expectOne(r => r.url === '/api/vault/plantillas');
      expect(req.request.params.keys().length).toBe(0);
      req.flush({ ok: true, plantillas: [mockPlantilla] });
      expect(result?.plantillas).toEqual([mockPlantilla]);
    });

    it('debería enviar parámetros de filtrado cuando se especifican', () => {
      service.getPlantillas('checkin', 'es').subscribe();
      const req = httpTesting.expectOne(r => r.url === '/api/vault/plantillas');
      expect(req.request.params.get('categoria')).toBe('checkin');
      expect(req.request.params.get('idioma')).toBe('es');
      req.flush({ ok: true, plantillas: [] });
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.getPlantillas().subscribe({ error: e => (err = e) });
      httpTesting.expectOne(r => r.url === '/api/vault/plantillas').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('crearPlantilla', () => {
    it('debería crear una nueva plantilla y retornarla', () => {
      let result: { ok: boolean; plantilla: Plantilla } | undefined;
      service.crearPlantilla({ nombre: 'Nueva', contenido: 'Hola', idioma: 'es', categoria: null }).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/vault/plantillas');
      expect(req.request.method).toBe('POST');
      req.flush({ ok: true, plantilla: mockPlantilla });
      expect(result?.plantilla).toEqual(mockPlantilla);
    });

    it('debería propagar error 400', () => {
      let err: unknown;
      service.crearPlantilla({ nombre: '', contenido: '', idioma: 'es', categoria: null }).subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/vault/plantillas').flush({ errors: ['nombre requerido'] }, { status: 400, statusText: 'Bad Request' });
      expect(err).toBeTruthy();
    });
  });

  describe('actualizarPlantilla', () => {
    it('debería actualizar una plantilla existente', () => {
      let result: { ok: boolean; plantilla: Plantilla } | undefined;
      service.actualizarPlantilla('p1', { nombre: 'Actualizada', contenido: 'Hola nuevo' }).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/vault/plantillas/p1');
      expect(req.request.method).toBe('PUT');
      req.flush({ ok: true, plantilla: { ...mockPlantilla, nombre: 'Actualizada' } });
      expect(result?.plantilla.nombre).toBe('Actualizada');
    });
  });

  describe('eliminarPlantilla', () => {
    it('debería eliminar una plantilla por id', () => {
      let result: { ok: boolean } | undefined;
      service.eliminarPlantilla('p1').subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/vault/plantillas/p1');
      expect(req.request.method).toBe('DELETE');
      req.flush({ ok: true });
      expect(result?.ok).toBe(true);
    });
  });

  describe('mejorar', () => {
    it('debería enviar el contenido para mejora y retornar el texto mejorado', () => {
      let result: { ok: boolean; contenido: string } | undefined;
      service.mejorar('p1', 'texto original', 'es').subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/vault/plantillas/p1/mejorar');
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ contenido: 'texto original', idioma: 'es' });
      req.flush({ ok: true, contenido: 'texto mejorado' });
      expect(result?.contenido).toBe('texto mejorado');
    });

    it('debería propagar error 500 en mejora de IA', () => {
      let err: unknown;
      service.mejorar('p1', 'texto', 'es').subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/vault/plantillas/p1/mejorar').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('traducir', () => {
    it('debería enviar el contenido para traducción y retornar el texto traducido', () => {
      let result: { ok: boolean; contenido: string } | undefined;
      service.traducir('p1', 'hola', 'en').subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/vault/plantillas/p1/traducir');
      expect(req.request.body).toEqual({ contenido: 'hola', idioma_destino: 'en' });
      req.flush({ ok: true, contenido: 'hello' });
      expect(result?.contenido).toBe('hello');
    });
  });

  describe('getUso', () => {
    it('debería retornar las métricas de uso de IA', () => {
      let result: { ok: boolean; uso_hoy: number; uso_semana: number; limite_diario: number; limite_semanal: number } | undefined;
      service.getUso().subscribe(r => (result = r));
      httpTesting.expectOne('/api/ai/uso').flush({ ok: true, uso_hoy: 3, uso_semana: 10, limite_diario: 50, limite_semanal: 200 });
      expect(result?.uso_hoy).toBe(3);
      expect(result?.limite_diario).toBe(50);
    });

    it('debería propagar error 404', () => {
      let err: unknown;
      service.getUso().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/ai/uso').flush('Not found', { status: 404, statusText: 'Not Found' });
      expect(err).toBeTruthy();
    });
  });
});
