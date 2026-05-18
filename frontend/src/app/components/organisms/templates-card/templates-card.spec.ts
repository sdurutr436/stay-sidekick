import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { TemplatesCardComponent } from './templates-card';

describe('TemplatesCardComponent', () => {
  let fixture: ComponentFixture<TemplatesCardComponent>;
  let component: TemplatesCardComponent;

  beforeEach(async () => {
    await TestBed.configureTestingModule({ imports: [TemplatesCardComponent] }).compileComponents();
    fixture = TestBed.createComponent(TemplatesCardComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  describe('Creación', () => {
    it('debería crearse correctamente', () => {
      expect(component).toBeTruthy();
    });

    it('debería renderizar el título por defecto "Plantillas"', () => {
      const title = fixture.debugElement.query(By.css('.templates-card__title'));
      expect(title.nativeElement.textContent).toContain('Plantillas');
    });
  });

  describe('@Input title (OnPush)', () => {
    it('debería mostrar el título personalizado', () => {
      fixture.componentRef.setInput('title', 'Mis plantillas');
      fixture.detectChanges();
      const title = fixture.debugElement.query(By.css('.templates-card__title'));
      expect(title.nativeElement.textContent).toContain('Mis plantillas');
    });
  });

  describe('@Input total (OnPush)', () => {
    it('NO debería mostrar el contador cuando total es null', () => {
      const count = fixture.debugElement.query(By.css('.templates-card__count'));
      expect(count).toBeNull();
    });

    it('debería mostrar "1 plantilla" cuando total es 1', () => {
      fixture.componentRef.setInput('total', 1);
      fixture.detectChanges();
      const count = fixture.debugElement.query(By.css('.templates-card__count'));
      expect(count.nativeElement.textContent.trim()).toContain('1 plantilla');
    });

    it('debería mostrar "5 plantillas" cuando total es 5', () => {
      fixture.componentRef.setInput('total', 5);
      fixture.detectChanges();
      const count = fixture.debugElement.query(By.css('.templates-card__count'));
      expect(count.nativeElement.textContent.trim()).toContain('5 plantillas');
    });
  });

  describe('@Input isEmpty (OnPush)', () => {
    it('NO debería mostrar el mensaje vacío por defecto', () => {
      const empty = fixture.debugElement.query(By.css('.templates-card__empty'));
      expect(empty).toBeNull();
    });

    it('debería mostrar el emptyMessage cuando isEmpty es true', () => {
      fixture.componentRef.setInput('isEmpty', true);
      fixture.componentRef.setInput('emptyMessage', 'Sin resultados aquí.');
      fixture.detectChanges();
      const empty = fixture.debugElement.query(By.css('.templates-card__empty'));
      expect(empty.nativeElement.textContent).toContain('Sin resultados aquí.');
    });
  });
});
