import { Component } from '@angular/core';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';

@Component({
  selector: 'app-menu-default',
  templateUrl: './menu-default.html',
  standalone: true,
  imports: [PageHeaderComponent],
})
export class MenuDefaultPageComponent {}
