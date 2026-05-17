import { Injectable, signal } from '@angular/core';

type Theme = 'light' | 'dark';
const STORAGE_KEY = 'theme';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  readonly theme = signal<Theme>(this._resolveInitial());

  constructor() {
    if (typeof document === 'undefined') return;
    this._apply(this.theme());

    // Sincronización entre pestañas/apps del mismo origen (Angular ↔ 11ty).
    // El evento 'storage' SOLO se dispara en otras pestañas, nunca en la que
    // hizo el setItem — exactamente lo que necesitamos para que la app espejo
    // se entere del cambio sin entrar en bucle.
    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (event: StorageEvent) => {
        if (event.key !== STORAGE_KEY) return;
        const next: Theme = event.newValue === 'dark' ? 'dark' : 'light';
        if (next !== this.theme()) {
          this.theme.set(next);
          this._apply(next);
        }
      });
    }
  }

  toggle(): void {
    this.setTheme(this.theme() === 'dark' ? 'light' : 'dark');
  }

  setTheme(theme: Theme): void {
    this.theme.set(theme);
    this._apply(theme);
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, theme);
    }
  }

  isDark(): boolean {
    return this.theme() === 'dark';
  }

  private _resolveInitial(): Theme {
    if (typeof localStorage !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored === 'light' || stored === 'dark') return stored;
    }
    if (typeof window !== 'undefined' && window.matchMedia) {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'light';
  }

  private _apply(theme: Theme): void {
    if (typeof document === 'undefined') return;
    const root = document.documentElement;
    root.classList.toggle('dark', theme === 'dark');
    root.setAttribute('data-theme', theme);
  }
}
