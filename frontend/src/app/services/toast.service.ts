import { Injectable, signal } from '@angular/core';

export type ToastVariant = 'success' | 'error' | 'warning' | 'info';

export interface Toast {
  id: number;
  variant: ToastVariant;
  mensaje: string;
}

const DURACION_DEFECTO_MS = 4000;

@Injectable({ providedIn: 'root' })
export class ToastService {
  private readonly _toasts = signal<Toast[]>([]);
  readonly toasts = this._toasts.asReadonly();

  private nextId = 1;
  private readonly timers = new Map<number, ReturnType<typeof setTimeout>>();

  showSuccess(mensaje: string, duracion?: number): void {
    this.show('success', mensaje, duracion);
  }

  showError(mensaje: string, duracion?: number): void {
    this.show('error', mensaje, duracion);
  }

  showInfo(mensaje: string, duracion?: number): void {
    this.show('info', mensaje, duracion);
  }

  showWarning(mensaje: string, duracion?: number): void {
    this.show('warning', mensaje, duracion);
  }

  dismiss(id: number): void {
    const timer = this.timers.get(id);
    if (timer) {
      clearTimeout(timer);
      this.timers.delete(id);
    }
    this._toasts.update(list => list.filter(t => t.id !== id));
  }

  clear(): void {
    this.timers.forEach(t => clearTimeout(t));
    this.timers.clear();
    this._toasts.set([]);
  }

  private show(variant: ToastVariant, mensaje: string, duracion?: number): void {
    const id = this.nextId++;
    const ms = duracion ?? DURACION_DEFECTO_MS;
    this._toasts.update(list => [...list, { id, variant, mensaje }]);

    if (ms > 0) {
      const timer = setTimeout(() => this.dismiss(id), ms);
      this.timers.set(id, timer);
    }
  }
}
