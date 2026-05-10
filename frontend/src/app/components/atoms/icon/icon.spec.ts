import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IconComponent } from './icon';

describe('IconComponent', () => {
  let fixture: ComponentFixture<IconComponent>;
  let component: IconComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [IconComponent] }).compileComponents();
    fixture = TestBed.createComponent(IconComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('hostClasses', () => {
    it('debería contener svg--sm con el tamaño por defecto', () => {
      expect(component.hostClasses).toContain('svg--sm');
    });

    it('debería contener svg--lg cuando size es lg', () => {
      component.size = 'lg';
      expect(component.hostClasses).toContain('svg--lg');
    });

    it('debería contener svg--xs cuando size es xs', () => {
      component.size = 'xs';
      expect(component.hostClasses).toContain('svg--xs');
    });

    it('debería incluir siempre la clase base svg', () => {
      expect(component.hostClasses).toContain('svg');
    });

    it('debería actualizar la clase cuando cambia el tamaño', () => {
      component.size = 'xl';
      expect(component.hostClasses).toContain('svg--xl');
      expect(component.hostClasses).not.toContain('svg--sm');
    });
  });
});
