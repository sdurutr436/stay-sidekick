import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SidenavService {
  // En móvil (< 768px) el sidenav empieza cerrado; en desktop abierto
  readonly isOpen = signal(typeof window !== 'undefined' ? window.innerWidth >= 768 : true);
  readonly isCollapsed = signal(false);

  toggle(): void {
    this.isOpen.update(v => !v);
  }

  toggleCollapse(): void {
    this.isCollapsed.update(v => !v);
  }
}
