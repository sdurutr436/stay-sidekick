import { Component, EventEmitter, Input, Output } from '@angular/core';

interface SelectOption {
  value: string;
  label: string;
}

@Component({
  selector: 'app-form-select',
  templateUrl: './form-select.html',
  styleUrl: './form-select.scss',
  standalone: true,
})
export class FormSelectComponent {
  @Input() id = '';
  @Input() value = '';
  @Input() options: SelectOption[] = [];
  @Input() disabled = false;
  @Input() ariaLabel = '';

  @Output() valueChange = new EventEmitter<string>();

  onChange(event: Event): void {
    const target = event.target as HTMLSelectElement;
    this.valueChange.emit(target.value);
  }
}
