import { Component, inject } from '@angular/core';
import { SidenavComponent } from '../../components/sidenav/sidenav';
import { SidenavService } from '../../services/sidenav.service';

@Component({
  selector: 'app-menu-page',
  templateUrl: './menu.html',
  styleUrl: './menu.scss',
  standalone: true,
  imports: [SidenavComponent],
})
export class MenuPageComponent {
  readonly sidenavService = inject(SidenavService);
}
