import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

type AlertType = 'success' | 'error' | 'warning' | 'info';

@Component({
  selector: 'app-alert',
  templateUrl: './alert.html',
  styleUrl: './alert.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class AlertComponent {
  @Input() type: AlertType = 'info';
  @Input() dismissible = false;

  visible = true;

  @Output() dismissed = new EventEmitter<void>();

  get hostClasses(): string {
    return `alert alert--${this.type}`;
  }

  dismiss(): void {
    this.visible = false;
    this.dismissed.emit();
  }
}
