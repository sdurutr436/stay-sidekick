import { Component, EventEmitter, Input, Output } from '@angular/core';

@Component({
  selector: 'app-form-input-icon',
  templateUrl: './form-input-icon.html',
  styleUrl: './form-input-icon.scss',
  standalone: true,
})
export class FormInputIconComponent {
  @Input() id = '';
  @Input() type: 'text' | 'email' | 'password' | 'search' | 'tel' | 'url' | 'number' = 'text';
  @Input() placeholder = '';
  @Input() value = '';

  @Output() valueChange = new EventEmitter<string>();

  onInput(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.valueChange.emit(target.value);
  }
}
