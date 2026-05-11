import { Injectable, signal } from '@angular/core';

const BREAKPOINT_MD = 768;

@Injectable({ providedIn: 'root' })
export class SidenavService {
  readonly isOpen = signal(typeof window !== 'undefined' ? window.innerWidth >= BREAKPOINT_MD : true);
  readonly isCollapsed = signal(false);

  constructor() {
    if (typeof window === 'undefined') return;
    let prevIsDesktop = window.innerWidth >= BREAKPOINT_MD;
    window.addEventListener('resize', () => {
      const isDesktop = window.innerWidth >= BREAKPOINT_MD;
      if (isDesktop !== prevIsDesktop) {
        this.isOpen.set(isDesktop);
        prevIsDesktop = isDesktop;
      }
    });
  }

  toggle(): void {
    this.isOpen.update(v => !v);
  }

  toggleCollapse(): void {
    this.isCollapsed.update(v => !v);
  }
}
