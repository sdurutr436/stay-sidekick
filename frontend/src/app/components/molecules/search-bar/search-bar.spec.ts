import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { SearchBarComponent } from './search-bar';

describe('SearchBarComponent', () => {
  let fixture: ComponentFixture<SearchBarComponent>;
  let component: SearchBarComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [SearchBarComponent] }).compileComponents();
    fixture = TestBed.createComponent(SearchBarComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Bindings de @Input (OnPush)', () => {
    it('debería tener el placeholder por defecto "Buscar…"', () => {
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).placeholder).toBe('Buscar…');
    });

    it('debería reflejar un placeholder personalizado', () => {
      fixture.componentRef.setInput('placeholder', 'Filtrar lista');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).placeholder).toBe('Filtrar lista');
    });

    it('debería reflejar el value inicial', () => {
      fixture.componentRef.setInput('value', 'texto buscado');
      fixture.detectChanges();
      const input = fixture.debugElement.query(By.css('input'));
      expect((input.nativeElement as HTMLInputElement).value).toBe('texto buscado');
    });
  });

  describe('@Output valueChange', () => {
    it('debería emitir el texto cuando el usuario escribe', () => {
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const input = fixture.debugElement.query(By.css('input'));
      const nativeInput = input.nativeElement as HTMLInputElement;
      nativeInput.value = 'búsqueda';
      nativeInput.dispatchEvent(new Event('input'));
      expect(emitted).toBe('búsqueda');
    });

    it('debería emitir cadena vacía al borrar el contenido', () => {
      let emitted: string | undefined;
      component.valueChange.subscribe((v: string) => (emitted = v));
      const input = fixture.debugElement.query(By.css('input'));
      const nativeInput = input.nativeElement as HTMLInputElement;
      nativeInput.value = '';
      nativeInput.dispatchEvent(new Event('input'));
      expect(emitted).toBe('');
    });
  });
});
