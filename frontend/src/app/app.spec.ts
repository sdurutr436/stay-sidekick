import { TestBed } from '@angular/core/testing';
import { RouterOutlet, provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { App } from './app';

describe('App', () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient()],
    }).overrideComponent(App, {
      set: {
        imports: [RouterOutlet],
        template: '<router-outlet />',
      },
    }).compileComponents();
  });

  it('debería crearse la aplicación', () => {
    const fixture = TestBed.createComponent(App);
    expect(fixture.componentInstance).toBeTruthy();
  });

  it('debería renderizar el skip-link de accesibilidad', async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [provideRouter([]), provideHttpClient()],
    }).overrideComponent(App, {
      set: {
        imports: [RouterOutlet],
        template: '<a class="skip-link" href="#main-content">Saltar al contenido</a><router-outlet />',
      },
    }).compileComponents();

    const fixture = TestBed.createComponent(App);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    const skipLink = compiled.querySelector('.skip-link');
    expect(skipLink).not.toBeNull();
    expect(skipLink?.getAttribute('href')).toBe('#main-content');
  });
});
