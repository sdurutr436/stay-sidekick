import { Routes } from '@angular/router';
import { MenuPageComponent } from './pages/menu/menu';
import { MenuDefaultPageComponent } from './pages/menu-default/menu-default';
import { MaestroApartamentosPageComponent } from './pages/maestro-apartamentos/maestro-apartamentos';
import { SincronizadorContactosPageComponent } from './pages/sincronizador-contactos/sincronizador-contactos';
import { HojaEstilosPageComponent } from './pages/hoja-estilos/hoja-estilos';
import { DsTipografiaComponent } from './pages/hoja-estilos/secciones/tipografia/tipografia';
import { DsAtomosComponent } from './pages/hoja-estilos/secciones/atomos/atomos';
import { DsMoleculasComponent } from './pages/hoja-estilos/secciones/moleculas/moleculas';
import { DsOrganismosComponent } from './pages/hoja-estilos/secciones/organismos/organismos';

export const routes: Routes = [
  {
    path: 'menu',
    component: MenuPageComponent,
    children: [
      { path: '', component: MenuDefaultPageComponent },
      { path: 'maestro-apartamentos', component: MaestroApartamentosPageComponent },
      { path: 'sincronizador-contactos', component: SincronizadorContactosPageComponent },
      {
        path: 'hoja-estilos',
        component: HojaEstilosPageComponent,
        children: [
          { path: '', redirectTo: 'tipografia', pathMatch: 'full' },
          { path: 'tipografia', component: DsTipografiaComponent },
          { path: 'atomos',     component: DsAtomosComponent     },
          { path: 'moleculas',  component: DsMoleculasComponent  },
          { path: 'organismos', component: DsOrganismosComponent },
        ],
      },
    ],
  },
];
