import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { provideHttpClientTesting, HttpTestingController } from '@angular/common/http/testing';
import { GestionUsuariosService, Usuario, EmpresaItem } from './gestion-usuarios.service';

const mockUsuario: Usuario = { id: 'u1', email: 'u@test.com', rol: 'admin', activo: true, created_at: '2024-01-01' };
const mockEmpresa: EmpresaItem = { id: 'e1', nombre: 'Empresa Test', email: 'e@test.com' };

describe('GestionUsuariosService', () => {
  let service: GestionUsuariosService;
  let httpTesting: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    service = TestBed.inject(GestionUsuariosService);
    httpTesting = TestBed.inject(HttpTestingController);
  });

  afterEach(() => httpTesting.verify());

  describe('getEmpresas', () => {
    it('debería retornar la lista de empresas', () => {
      let result: EmpresaItem[] | undefined;
      service.getEmpresas().subscribe(r => (result = r));
      httpTesting.expectOne('/api/empresas').flush({ ok: true, empresas: [mockEmpresa] });
      expect(result).toEqual([mockEmpresa]);
    });

    it('debería propagar error 403', () => {
      let err: unknown;
      service.getEmpresas().subscribe({ error: e => (err = e) });
      httpTesting.expectOne('/api/empresas').flush('Forbidden', { status: 403, statusText: 'Forbidden' });
      expect(err).toBeTruthy();
    });
  });

  describe('getUsuarios', () => {
    it('debería retornar usuarios y max_usuarios sin empresaId', () => {
      let result: { usuarios: Usuario[]; max_usuarios: number } | undefined;
      service.getUsuarios().subscribe(r => (result = r));
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios');
      expect(req.request.params.get('empresa_id')).toBeNull();
      req.flush({ ok: true, usuarios: [mockUsuario], max_usuarios: 5 });
      expect(result?.usuarios).toEqual([mockUsuario]);
      expect(result?.max_usuarios).toBe(5);
    });

    it('debería incluir empresa_id como parámetro cuando se especifica', () => {
      service.getUsuarios('e99').subscribe();
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios');
      expect(req.request.params.get('empresa_id')).toBe('e99');
      req.flush({ ok: true, usuarios: [], max_usuarios: 3 });
    });
  });

  describe('crearUsuario', () => {
    it('debería crear un usuario y retornar el usuario y la contraseña temporal', () => {
      let result: { usuario: Usuario; password_temporal: string } | undefined;
      service.crearUsuario({ email: 'nuevo@test.com', rol: 'operativo' }).subscribe(r => (result = r));
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios');
      expect(req.request.method).toBe('POST');
      req.flush({ ok: true, usuario: mockUsuario, password_temporal: 'temp123' });
      expect(result?.password_temporal).toBe('temp123');
    });

    it('debería propagar error 400 cuando el email ya existe', () => {
      let err: unknown;
      service.crearUsuario({ email: 'dup@test.com', rol: 'admin' }).subscribe({ error: e => (err = e) });
      httpTesting.expectOne(r => r.url === '/api/usuarios').flush({ errors: ['email duplicado'] }, { status: 400, statusText: 'Bad Request' });
      expect(err).toBeTruthy();
    });
  });

  describe('eliminarUsuario', () => {
    it('debería enviar DELETE y completar sin valor', () => {
      let completed = false;
      service.eliminarUsuario('u1').subscribe({ complete: () => (completed = true) });
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios/u1');
      expect(req.request.method).toBe('DELETE');
      req.flush({ ok: true });
      expect(completed).toBe(true);
    });
  });

  describe('editarRol', () => {
    it('debería enviar el nuevo rol y retornar el usuario actualizado', () => {
      let result: Usuario | undefined;
      service.editarRol('u1', 'operativo').subscribe(r => (result = r));
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios/u1');
      expect(req.request.method).toBe('PATCH');
      expect(req.request.body).toEqual({ rol: 'operativo' });
      req.flush({ ok: true, usuario: { ...mockUsuario, rol: 'operativo' } });
      expect(result?.rol).toBe('operativo');
    });
  });

  describe('resetearPassword', () => {
    it('debería retornar la contraseña temporal al resetear', () => {
      let result: { password_temporal: string } | undefined;
      service.resetearPassword('u1').subscribe(r => (result = r));
      const req = httpTesting.expectOne(r => r.url === '/api/usuarios/u1/contrasena');
      expect(req.request.method).toBe('PATCH');
      req.flush({ ok: true, password_temporal: 'newtemp456' });
      expect(result?.password_temporal).toBe('newtemp456');
    });

    it('debería propagar error 500', () => {
      let err: unknown;
      service.resetearPassword('u1').subscribe({ error: e => (err = e) });
      httpTesting.expectOne(r => r.url === '/api/usuarios/u1/contrasena').flush('Error', { status: 500, statusText: 'Internal Server Error' });
      expect(err).toBeTruthy();
    });
  });

  describe('crearEmpresa', () => {
    it('debería crear una empresa y retornarla', () => {
      let result: EmpresaItem | undefined;
      service.crearEmpresa({ nombre: 'Nueva Empresa', email: 'nueva@empresa.com' }).subscribe(r => (result = r));
      const req = httpTesting.expectOne('/api/empresas');
      expect(req.request.method).toBe('POST');
      req.flush({ ok: true, empresa: mockEmpresa });
      expect(result).toEqual(mockEmpresa);
    });
  });
});
