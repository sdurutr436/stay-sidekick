import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-form-label',
  templateUrl: './form-label.html',
  styleUrl: './form-label.scss',
  standalone: true,
})
export class FormLabelComponent {
  @Input() for = '';
}
