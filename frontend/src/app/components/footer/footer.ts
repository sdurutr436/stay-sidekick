import { Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.html',
  styleUrl: './footer.scss',
  standalone: true,
})
export class FooterComponent {
  protected readonly year = new Date().getFullYear();
}
