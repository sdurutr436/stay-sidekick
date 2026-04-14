import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-form-input',
  templateUrl: './form-input.html',
  styleUrl: './form-input.scss',
  standalone: true,
})
export class FormInputComponent {
  @Input() id = '';
  @Input() type: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url' | 'number' = 'text';
  @Input() placeholder = '';
  @Input() value = '';
  @Input() disabled = false;
  @Input() ariaLabel = '';

  @Output() valueChange = new EventEmitter<string>();

  onInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.valueChange.emit(target.value);
  }
}
