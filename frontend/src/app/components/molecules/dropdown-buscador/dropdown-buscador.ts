import { Component, ElementRef, EventEmitter, HostListener, Input, Output, inject, signal } from '@angular/core';

export interface DropdownOption {
  value: string;
  label: string;
}

@Component({
  selector: 'app-dropdown-buscador',
  templateUrl: './dropdown-buscador.html',
  styleUrl: './dropdown-buscador.scss',
  standalone: true,
})
export class DropdownBuscadorComponent {
  @Input() options: DropdownOption[] = [];
  @Input() placeholder = 'Seleccionar…';
  @Input() searchPlaceholder = 'Buscar…';
  @Input() emptyMessage = 'Sin resultados';

  @Output() optionSelected = new EventEmitter<DropdownOption>();

  private readonly elementRef = inject(ElementRef);

  readonly isOpen = signal(false);
  readonly searchQuery = signal('');
  readonly selectedOption = signal<DropdownOption | null>(null);

  get filteredOptions(): DropdownOption[] {
    const q = this.searchQuery().toLowerCase().trim();
    if (!q) return this.options;
    return this.options.filter(opt => opt.label.toLowerCase().includes(q));
  }

  get triggerLabel(): string {
    return this.selectedOption()?.label ?? this.placeholder;
  }

  toggle(): void {
    this.isOpen.update(v => !v);
    if (!this.isOpen()) this.searchQuery.set('');
  }

  select(option: DropdownOption): void {
    this.selectedOption.set(option);
    this.optionSelected.emit(option);
    this.isOpen.set(false);
    this.searchQuery.set('');
  }

  onSearchInput(event: Event): void {
    this.searchQuery.set((event.target as HTMLInputElement).value);
  }

  @HostListener('document:click', ['$event'])
  onDocumentClick(event: MouseEvent): void {
    if (!this.elementRef.nativeElement.contains(event.target as Node)) {
      this.isOpen.set(false);
      this.searchQuery.set('');
    }
  }
}
