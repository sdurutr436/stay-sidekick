import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class SidenavService {
  readonly isOpen = signal(true);
  readonly isCollapsed = signal(false);

  toggle(): void {
    this.isOpen.update(v => !v);
  }

  toggleCollapse(): void {
    this.isCollapsed.update(v => !v);
  }
}
