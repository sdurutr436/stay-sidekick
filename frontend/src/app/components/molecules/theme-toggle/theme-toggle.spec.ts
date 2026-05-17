import { ComponentFixture, TestBed } from '@angular/core/testing';
import { provideIcons } from '@ng-icons/core';
import { phosphorSun, phosphorMoon } from '@ng-icons/phosphor-icons/regular';
import { ThemeToggleComponent } from './theme-toggle';
import { ThemeService } from '../../../services/theme.service';

describe('ThemeToggleComponent', () => {
  let fixture: ComponentFixture<ThemeToggleComponent>;
  let component: ThemeToggleComponent;
  let service: ThemeService;

  beforeEach(async () => {
    localStorage.clear();
    document.documentElement.classList.remove('dark');
    document.documentElement.removeAttribute('data-theme');

    await TestBed.configureTestingModule({
      imports: [ThemeToggleComponent],
      providers: [provideIcons({ phosphorSun, phosphorMoon })],
    }).compileComponents();

    fixture = TestBed.createComponent(ThemeToggleComponent);
    component = fixture.componentInstance;
    service = TestBed.inject(ThemeService);
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });

    it('debería exponer el ThemeService inyectado', () => {
      expect(component.themeService).toBe(service);
    });
  });

  describe('toggle()', () => {
    it('debería invocar ThemeService.toggle al pulsar el botón', () => {
      const spy = vi.spyOn(service, 'toggle');
      component.toggle();
      expect(spy).toHaveBeenCalledTimes(1);
    });

    it('debería alternar el estado isDark al llamar toggle dos veces', () => {
      const initial = service.isDark();
      component.toggle();
      expect(service.isDark()).toBe(!initial);
      component.toggle();
      expect(service.isDark()).toBe(initial);
    });
  });
});
