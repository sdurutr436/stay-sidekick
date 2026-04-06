import { Routes } from '@angular/router';
import { MenuPageComponent } from './pages/menu/menu';
import { MenuDefaultPageComponent } from './pages/menu-default/menu-default';
import { MaestroApartamentosPageComponent } from './pages/maestro-apartamentos/maestro-apartamentos';

export const routes: Routes = [
  {
    path: 'menu',
    component: MenuPageComponent,
    children: [
      { path: '', component: MenuDefaultPageComponent },
      { path: 'maestro-apartamentos', component: MaestroApartamentosPageComponent },
    ],
  },
];
