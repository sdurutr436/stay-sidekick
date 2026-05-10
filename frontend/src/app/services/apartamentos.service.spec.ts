import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ApartamentosService, Apartamento, ImportacionPreview, PmsConfig, XlsxColumnas } from './apartamentos.service';

const mockApt: Apartamento = { id: '1', id_pms: null, id_externo: 'ext1', nombre: 'Apto 1', direccion: null, ciudad: 'Madrid', pms_origen: 'manual', activo: true };

describe('ApartamentosService', () => {
  let service: ApartamentosService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(ApartamentosService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('listar', () => {
    it('debería retornar la lista de apartamentos mapeando res.apartamentos', () => {
      let result: Apartamento[] | undefined;
      service.listar().subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos').flush({ ok: true, apartamentos: [mockApt] });
      expect(result).toEqual([mockApt]);
    });

    it('debería propagar error 404', () => {
      let err: unknown;
      service.listar().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/apartamentos').flush('Not found', { status: 404, statusText: 'Not Found' });
      expect(err).toBeTruthy();
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.listar().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/apartamentos').flush('Server error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('crear', () => {
    it('debería retornar el apartamento creado', () => {
      let result: Apartamento | undefined;
      service.crear({ nombre: 'Nuevo' }).subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos').flush({ ok: true, apartamento: mockApt });
      expect(result).toEqual(mockApt);
    });

    it('debería propagar error 400', () => {
      let err: unknown;
      service.crear({ nombre: '' }).subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/apartamentos').flush({ errors: ['nombre requerido'] }, { status: 400, statusText: 'Bad Request' });
      expect(err).toBeTruthy();
    });
  });

  describe('actualizar', () => {
    it('debería retornar el apartamento actualizado', () => {
      let result: Apartamento | undefined;
      service.actualizar('1', { nombre: 'Actualizado' }).subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos/1').flush({ ok: true, apartamento: { ...mockApt, nombre: 'Actualizado' } });
      expect(result?.nombre).toBe('Actualizado');
    });
  });

  describe('eliminar', () => {
    it('debería completar sin valor cuando la eliminación es exitosa', () => {
      let completed = false;
      service.eliminar('1').subscribe({ complete: () => (completed = true) });
      httpTesting.expectOne('/api/apartamentos/1').flush({ ok: true });
      expect(completed).toBe(true);
    });
  });

  describe('sincronizarSmoobu', () => {
    it('debería retornar el resultado de la sincronización', () => {
      let result: { total: number; nuevos: number; actualizados: number } | undefined;
      service.sincronizarSmoobu().subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos/sincronizacion/smoobu').flush({ ok: true, resultado: { total: 10, nuevos: 2, actualizados: 3 } });
      expect(result).toEqual({ total: 10, nuevos: 2, actualizados: 3 });
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.sincronizarSmoobu().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/apartamentos/sincronizacion/smoobu').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('importarXlsx', () => {
    it('debería retornar el resultado con warnings cuando los hay', () => {
      let result: { total: number; warnings?: string[] } | undefined;
      const file = new File(['data'], 'test.xlsx');
      service.importarXlsx(file).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/apartamentos/importacion');
      expect(req.request.body instanceof FormData).toBe(true);
      req.flush({ ok: true, resultado: { total: 5, nuevos: 3, actualizados: 2 }, warnings: ['warning1'] });
      expect(result?.total).toBe(5);
      expect(result?.warnings).toContain('warning1');
    });
  });

  describe('previewXlsx', () => {
    it('debería retornar el preview de la importación', () => {
      const preview: ImportacionPreview = { nuevos: [], actualizados: [], sin_cambios: [], errores: [] };
      let result: ImportacionPreview | undefined;
      const file = new File(['data'], 'test.xlsx');
      service.previewXlsx(file).subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos/importacion/preview').flush({ ok: true, preview });
      expect(result).toEqual(preview);
    });
  });

  describe('getPmsStatus', () => {
    it('debería retornar la config PMS', () => {
      const pms: PmsConfig = { proveedor: 'smoobu', endpoint: null, activo: true, ultimo_sync: null };
      let result: PmsConfig | null | undefined;
      service.getPmsStatus().subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos/pms').flush({ ok: true, config: pms });
      expect(result).toEqual(pms);
    });

    it('debería retornar null cuando no hay PMS configurado', () => {
      let result: PmsConfig | null | undefined;
      service.getPmsStatus().subscribe(r => (result = r));
      httpTesting.expectOne('/api/apartamentos/pms').flush({ ok: true, config: null });
      expect(result).toBeNull();
    });
  });

  describe('getXlsxColumnas', () => {
    it('debería retornar la configuración de columnas', () => {
      const config: XlsxColumnas = { col_id_externo: 0, col_nombre: 1, col_direccion: 2, col_ciudad: 3 };
      let result: XlsxColumnas | null | undefined;
      service.getXlsxColumnas().subscribe(r => (result = r));
      httpTesting.expectOne('/api/perfil/xlsx-apartamentos').flush({ ok: true, config });
      expect(result).toEqual(config);
    });
  });

  describe('saveXlsxColumnas', () => {
    it('debería enviar la configuración y completar sin valor', () => {
      let completed = false;
      const config: XlsxColumnas = { col_id_externo: 0, col_nombre: 1, col_direccion: 2, col_ciudad: 3 };
      service.saveXlsxColumnas(config).subscribe({ complete: () => (completed = true) });
      const req = httpTesting.expectOne('/api/perfil/xlsx-apartamentos');
      expect(req.request.method).toBe('PUT');
      req.flush({ ok: true });
      expect(completed).toBe(true);
    });
  });
});
