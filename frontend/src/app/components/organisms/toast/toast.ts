import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { ToastService } from '../../../services/toast.service';

@Component({
  selector: 'app-toast',
  templateUrl: './toast.html',
  styleUrl: './toast.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ToastComponent {
  private readonly toastService = inject(ToastService);

  readonly toasts = this.toastService.toasts;

  cerrar(id: number): void {
    this.toastService.dismiss(id);
  }

  ariaLive(variant: 'success' | 'error' | 'warning' | 'info'): 'assertive' | 'polite' {
    return variant === 'error' || variant === 'warning' ? 'assertive' : 'polite';
  }
}
