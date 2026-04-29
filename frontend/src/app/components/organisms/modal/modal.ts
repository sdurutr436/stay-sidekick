import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-modal',
  templateUrl: './modal.html',
  styleUrl: './modal.scss',
  standalone: true,
})
export class ModalComponent {
  @Input() title = '';
  @Input() open = false;

  @Output() cerrar = new EventEmitter<void>();

  onOverlayClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal__overlay')) {
      this.cerrar.emit();
    }
  }
}
