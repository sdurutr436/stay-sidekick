import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { MapaCalorService, DiaCalor, UmbralesCalor, ConfigXlsx } from './mapa-calor.service';

const mockDia: DiaCalor = { fecha: '2024-06-01', checkins: 5, checkouts: 3, mesAdyacente: false };
const mockUmbrales: UmbralesCalor = { nivel1: 10, nivel2: 20, nivel3: 30 };

describe('MapaCalorService', () => {
  let service: MapaCalorService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(MapaCalorService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('generarDesdePms', () => {
    it('debería incluir parámetros desde/hasta en la petición', () => {
      service.generarDesdePms('2024-06-01', '2024-06-30').subscribe();
      const req = httpTesting.expectOne(r => r.url === '/api/heatmap');
      expect(req.request.params.get('desde')).toBe('2024-06-01');
      expect(req.request.params.get('hasta')).toBe('2024-06-30');
      req.flush({ ok: true, dias: [mockDia] });
    });

    it('debería mapear res.dias en la respuesta', () => {
      let result: { dias: DiaCalor[] } | undefined;
      service.generarDesdePms('2024-06-01', '2024-06-30').subscribe(r => (result = r));
      httpTesting.expectOne(r => r.url === '/api/heatmap').flush({ ok: true, dias: [mockDia] });
      expect(result?.dias).toEqual([mockDia]);
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.generarDesdePms('2024-06-01', '2024-06-30').subscribe({ error: e => (err = e) });
      httpTesting.expectOne(r => r.url === '/api/heatmap').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('generarDesdeXlsx', () => {
    it('debería enviar checkins como FormData y opcionalmente checkouts', () => {
      const checkins = new File(['data'], 'ci.xlsx');
      const checkouts = new File(['data'], 'co.xlsx');
      service.generarDesdeXlsx(checkins, checkouts, '2024-06-01', '2024-06-30').subscribe();
      const req = httpTesting.expectOne('/api/heatmap/xlsx');
      expect(req.request.body instanceof FormData).toBe(true);
      req.flush({ ok: true, dias: [mockDia] });
    });

    it('debería funcionar sin archivo de checkouts', () => {
      const checkins = new File(['data'], 'ci.xlsx');
      service.generarDesdeXlsx(checkins, undefined, '2024-06-01', '2024-06-30').subscribe();
      const req = httpTesting.expectOne('/api/heatmap/xlsx');
      expect(req.request.body instanceof FormData).toBe(true);
      req.flush({ ok: true, dias: [] });
    });

    it('debería propagar warnings de la respuesta', () => {
      let result: { dias: DiaCalor[]; warnings?: string[] } | undefined;
      const checkins = new File(['data'], 'ci.xlsx');
      service.generarDesdeXlsx(checkins, undefined, '2024-06-01', '2024-06-30').subscribe(r => (result = r));
      httpTesting.expectOne('/api/heatmap/xlsx').flush({ ok: true, dias: [], warnings: ['sin datos de checkout'] });
      expect(result?.warnings).toContain('sin datos de checkout');
    });
  });

  describe('getUmbrales', () => {
    it('debería retornar los umbrales de calor', () => {
      let result: UmbralesCalor | undefined;
      service.getUmbrales().subscribe(r => (result = r));
      httpTesting.expectOne('/api/heatmap/umbrales').flush({ ok: true, umbrales: mockUmbrales });
      expect(result).toEqual(mockUmbrales);
    });

    it('debería propagar error 404', () => {
      let err: unknown;
      service.getUmbrales().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/heatmap/umbrales').flush('Not found', { status: 404, statusText: 'Not Found' });
      expect(err).toBeTruthy();
    });
  });

  describe('saveUmbrales', () => {
    it('debería enviar los umbrales con PUT y retornarlos', () => {
      let result: UmbralesCalor | undefined;
      service.saveUmbrales(mockUmbrales).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/heatmap/umbrales');
      expect(req.request.method).toBe('PUT');
      req.flush({ ok: true, umbrales: mockUmbrales });
      expect(result).toEqual(mockUmbrales);
    });
  });

  describe('getConfigXlsx', () => {
    it('debería retornar la configuración de columnas XLSX', () => {
      const config: ConfigXlsx = { col_fecha_checkin: 'A', col_fecha_checkout: 'B' };
      let result: ConfigXlsx | undefined;
      service.getConfigXlsx().subscribe(r => (result = r));
      httpTesting.expectOne('/api/heatmap/config-xlsx').flush({ ok: true, config });
      expect(result).toEqual(config);
    });
  });

  describe('saveConfigXlsx', () => {
    it('debería guardar la configuración XLSX y retornarla', () => {
      const config: ConfigXlsx = { col_fecha_checkin: 'A', col_fecha_checkout: null };
      let result: ConfigXlsx | undefined;
      service.saveConfigXlsx(config).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/heatmap/config-xlsx');
      expect(req.request.method).toBe('PUT');
      req.flush({ ok: true, config });
      expect(result).toEqual(config);
    });
  });
});
