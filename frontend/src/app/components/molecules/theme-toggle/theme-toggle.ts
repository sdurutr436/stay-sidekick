import { ChangeDetectionStrategy, Component, inject } from '@angular/core';
import { NgIconComponent } from '@ng-icons/core';
import { ButtonComponent } from '../../atoms/button/button';
import { ThemeService } from '../../../services/theme.service';

@Component({
  selector: 'app-theme-toggle',
  templateUrl: './theme-toggle.html',
  styleUrl: './theme-toggle.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
  imports: [ButtonComponent, NgIconComponent],
})
export class ThemeToggleComponent {
  readonly themeService = inject(ThemeService);

  toggle(): void {
    this.themeService.toggle();
  }
}
