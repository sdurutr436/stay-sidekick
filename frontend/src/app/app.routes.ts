import { Routes } from '@angular/router';
import { MenuPageComponent } from './pages/menu/menu';
import { MenuDefaultPageComponent } from './pages/menu-default/menu-default';
import { MaestroApartamentosPageComponent } from './pages/maestro-apartamentos/maestro-apartamentos';
import { SincronizadorContactosPageComponent } from './pages/sincronizador-contactos/sincronizador-contactos';
import { NotFoundComponent } from './pages/not-found/not-found';
import { authGuard } from './guards/auth.guard';

export const routes: Routes = [
  {
    path: '',
    component: MenuPageComponent,
    canActivate: [authGuard],
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
        path: 'hoja-estilos',
        loadComponent: () => import('./pages/hoja-estilos/hoja-estilos').then(m => m.HojaEstilosPageComponent),
        children: [
          { path: '', redirectTo: 'tipografia', pathMatch: 'full' },
          { path: 'tipografia', loadComponent: () => import('./pages/hoja-estilos/secciones/tipografia/tipografia').then(m => m.DsTipografiaComponent) },
          { path: 'atomos',     loadComponent: () => import('./pages/hoja-estilos/secciones/atomos/atomos').then(m => m.DsAtomosComponent)             },
          { path: 'moleculas',  loadComponent: () => import('./pages/hoja-estilos/secciones/moleculas/moleculas').then(m => m.DsMoleculasComponent)     },
          { path: 'organismos', loadComponent: () => import('./pages/hoja-estilos/secciones/organismos/organismos').then(m => m.DsOrganismosComponent)  },
        ],
      },
      {
        path: 'mapa-calor',
        loadComponent: () =>
          import('./pages/mapa-calor/mapa-calor').then(m => m.MapaCalorPageComponent),
      },
      {
        path: 'vault-comunicaciones',
        loadComponent: () =>
          import('./pages/vault-comunicaciones/vault-comunicaciones').then(
            m => m.VaultComunicacionesPageComponent
          ),
      },
      {
        path: 'perfil',
        loadComponent: () => import('./pages/perfil/perfil').then(m => m.PerfilPageComponent),
      },
      {
        path: 'gestion-usuarios',
        loadComponent: () =>
          import('./pages/gestion-usuarios/gestion-usuarios').then(
            m => m.GestionUsuariosPageComponent
          ),
      },
    ],
  },
  { path: '**', component: NotFoundComponent },
];
