import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { BadgeComponent } from './badge';

describe('BadgeComponent', () => {
  let fixture: ComponentFixture<BadgeComponent>;
  let component: BadgeComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [BadgeComponent] }).compileComponents();
    fixture = TestBed.createComponent(BadgeComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses (getter — no requiere setInput)', () => {
    it('debería incluir badge--default con la variante por defecto', () => {
      expect(component.hostClasses).toContain('badge--default');
    });

    it('debería incluir badge--solid cuando variant es solid', () => {
      component.variant = 'solid';
      expect(component.hostClasses).toContain('badge--solid');
    });

    it('debería incluir badge--outline cuando variant es outline', () => {
      component.variant = 'outline';
      expect(component.hostClasses).toContain('badge--outline');
    });

    it('debería incluir siempre la clase base badge', () => {
      expect(component.hostClasses).toContain('badge');
    });
  });

  describe('@Input dot (OnPush — requiere setInput para DOM)', () => {
    it('NO debería renderizar .badge__dot cuando dot es false por defecto', () => {
      const dot = fixture.debugElement.query(By.css('.badge__dot'));
      expect(dot).toBeNull();
    });

    it('debería renderizar .badge__dot cuando dot es true', () => {
      fixture.componentRef.setInput('dot', true);
      fixture.detectChanges();
      const dot = fixture.debugElement.query(By.css('.badge__dot'));
      expect(dot).not.toBeNull();
    });

    it('debería eliminar .badge__dot al volver dot a false', () => {
      fixture.componentRef.setInput('dot', true);
      fixture.detectChanges();
      fixture.componentRef.setInput('dot', false);
      fixture.detectChanges();
      const dot = fixture.debugElement.query(By.css('.badge__dot'));
      expect(dot).toBeNull();
    });
  });
});
