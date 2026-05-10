import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-form-checkbox',
  templateUrl: './form-checkbox.html',
  styleUrl: './form-checkbox.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FormCheckboxComponent {
  @Input() checked = false;
  @Input() disabled = false;
  @Input() ariaLabel = '';

  @Output() checkedChange = new EventEmitter<boolean>();

  onChange(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.checkedChange.emit(target.checked);
  }
}
