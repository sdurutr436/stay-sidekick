import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterLink, RouterLinkActive, provideRouter } from '@angular/router';
import { SidenavComponent } from './sidenav';
import { SidenavService } from '../../../services/sidenav.service';
import { AuthService } from '../../../services/auth.service';

function createAuthMock(isAdmin: boolean): Partial<AuthService> {
  return { get isAdmin() { return isAdmin; } };
}

describe('SidenavComponent', () => {
  let fixture: ComponentFixture<SidenavComponent>;
  let component: SidenavComponent;

  async function setup(isAdmin: boolean) {
    TestBed.resetTestingModule();
    await TestBed.configureTestingModule({
      imports: [SidenavComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: createAuthMock(isAdmin) },
      ],
    }).overrideComponent(SidenavComponent, {
      set: {
        imports: [RouterLink, RouterLinkActive],
        template: `
          <nav>
            @for (tool of visibleTools(); track tool.id) {
              <a [routerLink]="tool.route">{{ tool.label }}</a>
            }
          </nav>
        `,
      },
    }).compileComponents();

    fixture = TestBed.createComponent(SidenavComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  }

  afterEach(() => TestBed.resetTestingModule());

  describe('Creación', () => {
    it('debería crearse correctamente', async () => {
      await setup(false);
      expect(component).toBeTruthy();
    });
  });

  describe('visibleTools (computed)', () => {
    it('debería excluir herramientas adminOnly cuando el usuario no es admin', async () => {
      await setup(false);
      const tools = component.visibleTools();
      expect(tools.every(t => !t.adminOnly)).toBe(true);
    });

    it('debería incluir herramientas adminOnly cuando el usuario es admin', async () => {
      await setup(true);
      const tools = component.visibleTools();
      expect(tools.some(t => t.adminOnly)).toBe(true);
    });

    it('debería incluir la herramienta gestion-usuarios solo para admin', async () => {
      await setup(false);
      const sinAdmin = component.visibleTools().map(t => t.id);
      expect(sinAdmin).not.toContain('gestion-usuarios');

      await setup(true);
      const conAdmin = component.visibleTools().map(t => t.id);
      expect(conAdmin).toContain('gestion-usuarios');
    });

    it('debería incluir herramientas comunes sin importar el rol', async () => {
      await setup(false);
      const ids = component.visibleTools().map(t => t.id);
      expect(ids).toContain('maestro-apartamentos');
      expect(ids).toContain('sincronizador-contactos');
    });
  });

  describe('SidenavService integration', () => {
    it('debería tener acceso al SidenavService para el estado del sidenav', async () => {
      await setup(false);
      const sidenavService = TestBed.inject(SidenavService);
      expect(sidenavService).toBeTruthy();
      expect(sidenavService.isCollapsed()).toBe(false);
    });
  });
});
