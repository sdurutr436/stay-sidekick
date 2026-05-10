import { ChangeDetectionStrategy, Component, Input } from '@angular/core';

@Component({
  selector: 'app-tarjeta-estado',
  templateUrl: './tarjeta-estado.html',
  styleUrl: './tarjeta-estado.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class TarjetaEstadoComponent {
  @Input() label = '';
  @Input() valor = '';
  @Input() sub = '';
  @Input() destacada = false;

  get hostClasses(): string {
    return this.destacada
      ? 'tarjeta-estado tarjeta-estado--destacada'
      : 'tarjeta-estado';
  }
}
