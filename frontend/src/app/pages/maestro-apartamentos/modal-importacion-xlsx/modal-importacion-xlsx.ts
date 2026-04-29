import { Component, EventEmitter, Input, Output } from '@angular/core';

import { ButtonComponent } from '../../../components/atoms/button/button';
import { AccordionItemComponent } from '../../../components/molecules/accordion-item/accordion-item';
import { ModalComponent } from '../../../components/organisms/modal/modal';
import { ImportacionPreview } from '../../../services/apartamentos.service';

@Component({
  selector: 'app-modal-importacion-xlsx',
  templateUrl: './modal-importacion-xlsx.html',
  styleUrl: './modal-importacion-xlsx.scss',
  standalone: true,
  imports: [ModalComponent, AccordionItemComponent, ButtonComponent],
})
export class ModalImportacionXlsxComponent {
  @Input() preview: ImportacionPreview | null = null;
  @Input() open = false;
  @Input() cargando = false;

  @Output() confirmar = new EventEmitter<void>();
  @Output() cerrar = new EventEmitter<void>();
}
