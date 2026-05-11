import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { DropdownBuscadorComponent, DropdownOption } from './dropdown-buscador';

const OPTIONS: DropdownOption[] = [
  { value: 'es', label: 'Español' },
  { value: 'en', label: 'Inglés' },
  { value: 'fr', label: 'Francés' },
];

describe('DropdownBuscadorComponent', () => {
  let fixture: ComponentFixture<DropdownBuscadorComponent>;
  let component: DropdownBuscadorComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [DropdownBuscadorComponent] }).compileComponents();
    fixture = TestBed.createComponent(DropdownBuscadorComponent);
    component = fixture.componentInstance;
    component.options = OPTIONS;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('isOpen (signal)', () => {
    it('debería estar cerrado inicialmente', () => {
      expect(component.isOpen()).toBe(false);
    });

    it('debería abrirse al llamar toggle()', () => {
      component.toggle();
      expect(component.isOpen()).toBe(true);
    });

    it('debería cerrarse y limpiar searchQuery al llamar toggle() de nuevo', () => {
      component.toggle();
      component.searchQuery.set('texto');
      component.toggle();
      expect(component.isOpen()).toBe(false);
      expect(component.searchQuery()).toBe('');
    });
  });

  describe('triggerLabel', () => {
    it('debería mostrar el placeholder cuando no hay opción seleccionada', () => {
      component.placeholder = 'Selecciona idioma';
      expect(component.triggerLabel).toBe('Selecciona idioma');
    });

    it('debería mostrar el label de la opción seleccionada', () => {
      component.selectedOption.set(OPTIONS[1]);
      expect(component.triggerLabel).toBe('Inglés');
    });
  });

  describe('filteredOptions', () => {
    it('debería retornar todas las opciones cuando no hay búsqueda', () => {
      component.searchQuery.set('');
      expect(component.filteredOptions.length).toBe(3);
    });

    it('debería filtrar opciones por el término de búsqueda (case insensitive)', () => {
      component.searchQuery.set('es');
      const filtered = component.filteredOptions;
      expect(filtered.some(o => o.value === 'es')).toBe(true);
    });

    it('debería retornar lista vacía cuando no hay coincidencias', () => {
      component.searchQuery.set('zzz');
      expect(component.filteredOptions.length).toBe(0);
    });
  });

  describe('select()', () => {
    it('debería establecer selectedOption, emitir optionSelected y cerrar el panel', () => {
      let emitted: DropdownOption | undefined;
      component.optionSelected.subscribe((o: DropdownOption) => (emitted = o));
      component.toggle();
      component.select(OPTIONS[0]);
      expect(component.selectedOption()).toEqual(OPTIONS[0]);
      expect(emitted).toEqual(OPTIONS[0]);
      expect(component.isOpen()).toBe(false);
      expect(component.searchQuery()).toBe('');
    });
  });

  describe('onSearchInput()', () => {
    it('debería actualizar searchQuery con el valor del input', () => {
      const fakeEvent = { target: { value: 'franc' } } as unknown as Event;
      component.onSearchInput(fakeEvent);
      expect(component.searchQuery()).toBe('franc');
    });
  });

  describe('Panel condicional', () => {
    it('NO debería renderizar el panel cuando está cerrado', () => {
      const panel = fixture.debugElement.query(By.css('.dropdown-buscador__panel'));
      expect(panel).toBeNull();
    });

    it('debería renderizar el panel cuando está abierto', () => {
      component.toggle();
      fixture.detectChanges();
      const panel = fixture.debugElement.query(By.css('.dropdown-buscador__panel'));
      expect(panel).not.toBeNull();
    });

    it('debería mostrar el mensaje de sin resultados cuando filteredOptions está vacío', () => {
      component.toggle();
      component.searchQuery.set('zzz');
      fixture.detectChanges();
      const empty = fixture.debugElement.query(By.css('.dropdown-buscador__empty'));
      expect(empty).not.toBeNull();
    });
  });
});
