import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SearchBarComponent } from '../../molecules/search-bar/search-bar';

export interface TablaCrudColumn {
  key: string;
  label: string;
  modifier?: string;
}

@Component({
  selector: 'app-tabla-crud',
  templateUrl: './tabla-crud.html',
  styleUrl: './tabla-crud.scss',
  standalone: true,
  imports: [SearchBarComponent],
})
export class TablaCrudComponent {
  @Input() columns: TablaCrudColumn[] = [];
  @Input() searchPlaceholder = 'Buscar…';
  @Input() searchValue = '';
  @Input() emptyTitle = 'Sin resultados';
  @Input() emptyDescription = '';
  @Input() resultCount = 0;
  @Input() selectedCount = 0;
  @Input() searchLabel = '';
  @Input() cargando = false;

  @Output() searchChange = new EventEmitter<string>();

  onSearchInput(value: string): void {
    this.searchChange.emit(value);
  }
}
