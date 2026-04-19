import { Routes } from '@angular/router';
import { MenuPageComponent } from './pages/menu/menu';
import { MenuDefaultPageComponent } from './pages/menu-default/menu-default';
import { MaestroApartamentosPageComponent } from './pages/maestro-apartamentos/maestro-apartamentos';
import { SincronizadorContactosPageComponent } from './pages/sincronizador-contactos/sincronizador-contactos';

export const routes: Routes = [
  {
    path: 'menu',
    component: MenuPageComponent,
    children: [
      { path: '', component: MenuDefaultPageComponent },
      { path: 'maestro-apartamentos', component: MaestroApartamentosPageComponent },
      { path: 'sincronizador-contactos', component: SincronizadorContactosPageComponent },
      {
        path: 'notificaciones-checkin-tardio',
        loadComponent: () =>
          import('./pages/notificaciones-checkin-tardio/notificaciones-checkin-tardio').then(
            m => m.NotificacionesCheckinTardioPageComponent
          ),
      },
      {
        path: 'vault-comunicaciones',
        loadComponent: () =>
          import('./pages/vault-comunicaciones/vault-comunicaciones').then(
            m => m.VaultComunicacionesPageComponent
          ),
      },
    ],
  },
];
