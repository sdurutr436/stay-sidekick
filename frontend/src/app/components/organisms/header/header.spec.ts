import { ComponentFixture, TestBed } from '@angular/core/testing';
import { RouterLink, provideRouter } from '@angular/router';
import { HeaderComponent } from './header';
import { AuthService } from '../../../services/auth.service';
import { SidenavService } from '../../../services/sidenav.service';

const authMock: Partial<AuthService> = {
  isLoggedIn: () => true,
  getToken: () => null,
  get isAdmin() { return false; },
  get esSuperAdmin() { return false; },
  get debeChangiarPassword() { return false; },
};

describe('HeaderComponent', () => {
  let fixture: ComponentFixture<HeaderComponent>;
  let component: HeaderComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [HeaderComponent],
      providers: [
        provideRouter([]),
        { provide: AuthService, useValue: authMock },
      ],
    }).overrideComponent(HeaderComponent, {
      set: {
        imports: [RouterLink],
        template: '<header><a routerLink="/">Inicio</a></header>',
      },
    }).compileComponents();

    fixture = TestBed.createComponent(HeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Propiedades inyectadas', () => {
    it('debería tener acceso al SidenavService', () => {
      const sidenavService = TestBed.inject(SidenavService);
      expect(component.sidenavService).toBe(sidenavService);
    });

    it('debería tener acceso al AuthService', () => {
      expect(component.auth).toBeTruthy();
    });
  });

  describe('isMenuPage (signal)', () => {
    it('debería tener valor inicial true', () => {
      expect(component.isMenuPage()).toBe(true);
    });
  });
});
