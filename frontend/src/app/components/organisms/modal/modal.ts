import {
  ChangeDetectionStrategy, Component, ElementRef, EventEmitter,
  HostListener, inject, Input, OnChanges, Output, SimpleChanges,
} from '@angular/core';

@Component({
  selector: 'app-modal',
  templateUrl: './modal.html',
  styleUrl: './modal.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ModalComponent implements OnChanges {
  @Input() title = '';
  @Input() open = false;

  @Output() cerrar = new EventEmitter<void>();

  private readonly elRef = inject(ElementRef<HTMLElement>);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['open']?.currentValue === true) {
      setTimeout(() => {
        const panel = this.elRef.nativeElement.querySelector('.modal__panel');
        const firstFocusable = panel?.querySelector<HTMLElement>(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        firstFocusable?.focus();
      });
    }
  }

  @HostListener('keydown.escape')
  onEscape(): void {
    if (this.open) {
      this.cerrar.emit();
    }
  }

  onOverlayClick(event: MouseEvent): void {
    if ((event.target as HTMLElement).classList.contains('modal__overlay')) {
      this.cerrar.emit();
    }
  }
}
