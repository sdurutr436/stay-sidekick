import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { ButtonComponent } from './button';

describe('ButtonComponent', () => {
  let fixture: ComponentFixture<ButtonComponent>;
  let component: ButtonComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [ButtonComponent] }).compileComponents();
    fixture = TestBed.createComponent(ButtonComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses (getter — no requiere setInput)', () => {
    it('debería tener clases btn--primary y btn--md por defecto', () => {
      expect(component.hostClasses).toContain('btn--primary');
      expect(component.hostClasses).toContain('btn--md');
    });

    it('debería reflejar variante danger', () => {
      component.variant = 'danger';
      expect(component.hostClasses).toContain('btn--danger');
    });

    it('debería reflejar variante ghost con tamaño sm', () => {
      component.variant = 'ghost';
      component.size = 'sm';
      expect(component.hostClasses).toContain('btn--ghost');
      expect(component.hostClasses).toContain('btn--sm');
    });

    it('debería incluir siempre la clase base btn', () => {
      expect(component.hostClasses).toContain('btn');
    });
  });

  describe('@Input disabled (OnPush — requiere setInput para DOM)', () => {
    it('debería reflejar disabled=false por defecto', () => {
      const btn = fixture.debugElement.query(By.css('button'));
      expect((btn.nativeElement as HTMLButtonElement).disabled).toBe(false);
    });

    it('debería aplicar disabled al elemento nativo cuando es true', () => {
      fixture.componentRef.setInput('disabled', true);
      fixture.detectChanges();
      const btn = fixture.debugElement.query(By.css('button'));
      expect((btn.nativeElement as HTMLButtonElement).disabled).toBe(true);
    });
  });

  describe('@Input type (OnPush — requiere setInput para DOM)', () => {
    it('debería renderizar el botón con type button por defecto', () => {
      const btn = fixture.debugElement.query(By.css('button'));
      expect((btn.nativeElement as HTMLButtonElement).type).toBe('button');
    });

    it('debería renderizar el botón con type submit cuando se especifica', () => {
      fixture.componentRef.setInput('type', 'submit');
      fixture.detectChanges();
      const btn = fixture.debugElement.query(By.css('button'));
      expect((btn.nativeElement as HTMLButtonElement).type).toBe('submit');
    });
  });
});
