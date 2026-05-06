import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NgIconComponent } from '@ng-icons/core';
import { ButtonComponent } from '../../components/atoms/button/button';
import { PageHeaderComponent } from '../../components/organisms/page-header/page-header';
import { IntegracionesData, PerfilService } from '../../services/perfil.service';
import { AuthService } from '../../services/auth.service';
import { VaultService } from '../../services/vault.service';
import { ApartamentosService } from '../../services/apartamentos.service';

interface Herramienta {
  id: string;
  label: string;
  descripcion: string;
  route: string;
  icon: string;
  contador?: number;
  estado?: 'ok' | 'parcial' | 'sin-conexion';
}

const HERRAMIENTAS: Herramienta[] = [
  {
    id: 'maestro-apartamentos',
    label: 'Maestro de apartamentos',
    descripcion: 'Gestiona el catálogo de apartamentos e importa datos desde XLSX.',
    route: '/maestro-apartamentos',
    icon: 'phosphorBuildings',
  },
  {
    id: 'sincronizador-contactos',
    label: 'Sincronizador de contactos',
    descripcion: 'Sincroniza huéspedes con Google Contacts, formateando nombres y teléfonos.',
    route: '/sincronizador-contactos',
    icon: 'phosphorAddressBook',
  },
  {
    id: 'notificaciones-checkin-tardio',
    label: 'Notificaciones check-in tardío',
    descripcion: 'Envía alertas para reservas con llegada tardía usando plantillas personalizables.',
    route: '/notificaciones-checkin-tardio',
    icon: 'phosphorBellRinging',
  },
  {
    id: 'mapa-calor',
    label: 'Mapa de calor',
    descripcion: 'Visualiza la ocupación mensual en un mapa de calor de check-ins y check-outs.',
    route: '/mapa-calor',
    icon: 'phosphorFireSimple',
  },
  {
    id: 'vault-comunicaciones',
    label: 'Vault de comunicaciones',
    descripcion: 'Biblioteca de plantillas de mensajes con refinado y traducción por IA.',
    route: '/vault-comunicaciones',
    icon: 'phosphorChatText',
  },
];

@Component({
  selector: 'app-menu-default',
  templateUrl: './menu-default.html',
  standalone: true,
  imports: [RouterLink, NgIconComponent, PageHeaderComponent, ButtonComponent],
})
export class MenuDefaultPageComponent implements OnInit {
  private readonly perfilService = inject(PerfilService);
  private readonly authService = inject(AuthService);
  private readonly vaultService = inject(VaultService);

  readonly integraciones = signal<IntegracionesData | null>(null);
  readonly HERRAMIENTAS = HERRAMIENTAS;
  readonly usuario = this.authService.getUser();
  readonly usoIA = signal<{ uso_hoy: number; limite_diario: number } | null>(null);

  readonly sinConexiones = computed(() => {
    const d = this.integraciones();
    return d !== null && !d.pms.configurado && !d.google.configurado && !d.ia.configurado;
  });

  ngOnInit(): void {
    this.perfilService.getIntegraciones().subscribe({
      next: (res) => {
        if (res.ok) {
          this.integraciones.set(res.data);
          if (!res.data.ia.configurado) {
            this.vaultService.getUso().subscribe({
              next: (uso) => {
                if (uso.ok) this.usoIA.set({ uso_hoy: uso.uso_hoy, limite_diario: uso.limite_diario });
              },
            });
          }
        }
      },
    });
  }

  getEstadoHerramienta(id: string): 'ok' | 'parcial' | 'sin-conexion' {
    const d = this.integraciones();
    if (id === 'sincronizador-contactos') {
      return (d?.google.configurado || d?.pms.configurado) ? 'ok' : 'parcial';
    }
    return 'ok';
  }
}
