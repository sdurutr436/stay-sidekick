import { Component, inject } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { SidenavComponent } from '../../components/organisms/sidenav/sidenav';
import { SidenavService } from '../../services/sidenav.service';

@Component({
  selector: 'app-menu-page',
  templateUrl: './menu.html',
  styleUrl: './menu.scss',
  standalone: true,
  imports: [SidenavComponent, RouterOutlet],
})
export class MenuPageComponent {
  readonly sidenavService = inject(SidenavService);
}
