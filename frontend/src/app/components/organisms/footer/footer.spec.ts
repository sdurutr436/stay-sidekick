import { ComponentFixture, TestBed } from '@angular/core/testing';
import { FooterComponent } from './footer';

describe('FooterComponent', () => {
  let fixture: ComponentFixture<FooterComponent>;
  let component: FooterComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [FooterComponent] }).compileComponents();
    fixture = TestBed.createComponent(FooterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });
  });

  describe('Datos estáticos', () => {
    it('debería tener el año actual', () => {
      expect((component as unknown as { year: number }).year).toBe(new Date().getFullYear());
    });

    it('debería tener 3 secciones en footerNav', () => {
      const nav = (component as unknown as { footerNav: readonly unknown[] }).footerNav;
      expect(nav.length).toBe(3);
    });

    it('debería tener 2 redes sociales', () => {
      const social = (component as unknown as { social: readonly unknown[] }).social;
      expect(social.length).toBe(2);
    });

    it('debería tener la sección Legal en footerNav', () => {
      const nav = (component as unknown as { footerNav: readonly { label: string }[] }).footerNav;
      expect(nav.some(s => s.label === 'Legal')).toBe(true);
    });

    it('debería tener GitHub entre las redes sociales', () => {
      const social = (component as unknown as { social: readonly { text: string }[] }).social;
      expect(social.some(s => s.text === 'GitHub')).toBe(true);
    });
  });
});
