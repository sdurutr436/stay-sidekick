import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { TablaCrudComponent, TablaCrudColumn } from './tabla-crud';

const COLS: TablaCrudColumn[] = [
  { key: 'nombre', label: 'Nombre' },
  { key: 'ciudad', label: 'Ciudad', modifier: 'muted' },
];

describe('TablaCrudComponent', () => {
  let fixture: ComponentFixture<TablaCrudComponent>;
  let component: TablaCrudComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TablaCrudComponent] }).compileComponents();
    fixture = TestBed.createComponent(TablaCrudComponent);
    component = fixture.componentInstance;
    component.columns = COLS;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Valores iniciales', () => {
    it('debería tener resultCount 0 por defecto', () => {
      expect(component.resultCount).toBe(0);
    });

    it('debería tener searchValue vacío por defecto', () => {
      expect(component.searchValue).toBe('');
    });
  });

  describe('@Input searchPlaceholder', () => {
    it('debería reflejar el placeholder de búsqueda por defecto', () => {
      const searchBar = fixture.debugElement.query(By.css('app-search-bar'));
      expect(searchBar).not.toBeNull();
    });
  });

  describe('@Output searchChange', () => {
    it('debería emitir searchChange cuando el SearchBar emite valueChange', () => {
      let emitted: string | undefined;
      component.searchChange.subscribe((v: string) => (emitted = v));
      component.onSearchInput('nuevo filtro');
      expect(emitted).toBe('nuevo filtro');
    });

    it('debería emitir cadena vacía cuando el usuario limpia la búsqueda', () => {
      let emitted: string | undefined;
      component.searchChange.subscribe((v: string) => (emitted = v));
      component.onSearchInput('');
      expect(emitted).toBe('');
    });
  });
});
