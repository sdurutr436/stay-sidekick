import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { ButtonComponent } from '../../atoms/button/button';

@Component({
  selector: 'app-confirm-inline',
  templateUrl: './confirm-inline.html',
  styleUrl: './confirm-inline.scss',
  standalone: true,
  imports: [ButtonComponent],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ConfirmInlineComponent {
  @Input() mensaje = '¿Confirmar acción?';
  @Input() visible = false;
  @Input() cargando = false;

  @Output() confirmado = new EventEmitter<void>();
  @Output() cancelado = new EventEmitter<void>();
}
