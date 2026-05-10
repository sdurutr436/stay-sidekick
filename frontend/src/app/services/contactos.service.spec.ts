import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { ContactosService, PreferenciasContactos, PREFS_CONTACTOS_DEFECTO } from './contactos.service';

const mockPrefs: PreferenciasContactos = {
  plantilla: '{FECHA} - {APT} - {NOMBRE}',
  separador_apt: ', ',
  formato_fecha_salida: 'YYMMDD',
  xlsx_reservas: { col_checkin: 1, col_nombre: 2, col_tipologia: 3, col_telefono: 4 },
};

describe('ContactosService', () => {
  let service: ContactosService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(ContactosService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('PREFS_CONTACTOS_DEFECTO', () => {
    it('debería tener la plantilla por defecto correcta', () => {
      expect(PREFS_CONTACTOS_DEFECTO.plantilla).toBe('{FECHA} - {APT} - {NOMBRE}');
    });

    it('debería tener todas las columnas XLSX inicializadas a 0', () => {
      const { xlsx_reservas } = PREFS_CONTACTOS_DEFECTO;
      expect(xlsx_reservas.col_checkin).toBe(0);
      expect(xlsx_reservas.col_nombre).toBe(0);
      expect(xlsx_reservas.col_tipologia).toBe(0);
      expect(xlsx_reservas.col_telefono).toBe(0);
    });
  });

  describe('getPreferencias', () => {
    it('debería retornar las preferencias mapeando res.preferencias', () => {
      let result: PreferenciasContactos | undefined;
      service.getPreferencias().subscribe(r => (result = r));
      httpTesting.expectOne('/api/contactos/preferencias').flush({ ok: true, preferencias: mockPrefs });
      expect(result).toEqual(mockPrefs);
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.getPreferencias().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/contactos/preferencias').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('savePreferencias', () => {
    it('debería enviar las preferencias parciales y retornar las preferencias actualizadas', () => {
      let result: PreferenciasContactos | undefined;
      const partial: Partial<PreferenciasContactos> = { separador_apt: ' | ' };
      service.savePreferencias(partial).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/contactos/preferencias');
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(partial);
      req.flush({ ok: true, preferencias: { ...mockPrefs, separador_apt: ' | ' } });
      expect(result?.separador_apt).toBe(' | ');
    });

    it('debería propagar error 400', () => {
      let err: unknown;
      service.savePreferencias({}).subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/contactos/preferencias').flush({ errors: ['plantilla inválida'] }, { status: 400, statusText: 'Bad Request' });
      expect(err).toBeTruthy();
    });
  });
});
