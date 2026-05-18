import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { TagComponent } from './tag';

describe('TagComponent', () => {
  let fixture: ComponentFixture<TagComponent>;
  let component: TagComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TagComponent] }).compileComponents();
    fixture = TestBed.createComponent(TagComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses (getter)', () => {
    it('debería tener clase base "tag" y variante "default" por defecto', () => {
      expect(component.hostClasses).toBe('tag tag--default');
    });

    it('debería reflejar variante "success"', () => {
      component.variant = 'success';
      expect(component.hostClasses).toContain('tag--success');
    });

    it('debería reflejar variante "warning"', () => {
      component.variant = 'warning';
      expect(component.hostClasses).toContain('tag--warning');
    });

    it('debería reflejar variante "danger"', () => {
      component.variant = 'danger';
      expect(component.hostClasses).toContain('tag--danger');
    });
  });

  describe('Renderizado', () => {
    it('debería renderizar un span con la clase aplicada', () => {
      const tag = fixture.debugElement.query(By.css('span.tag'));
      expect(tag).not.toBeNull();
      expect(tag.nativeElement.className).toContain('tag--default');
    });

    it('debería tener un span interno con clase tag__label para el contenido', () => {
      const label = fixture.debugElement.query(By.css('.tag__label'));
      expect(label).not.toBeNull();
    });
  });
});
