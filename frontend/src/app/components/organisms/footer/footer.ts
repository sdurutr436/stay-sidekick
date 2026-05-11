import { ChangeDetectionStrategy, Component } from '@angular/core';

@Component({
  selector: 'app-footer',
  templateUrl: './footer.html',
  styleUrl: './footer.scss',
  standalone: true,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FooterComponent {
  protected readonly year = new Date().getFullYear();

  protected readonly footerNav = [
    {
      label: 'Producto',
      links: [
        { text: 'Funcionalidades', href: '#' },
        { text: 'Precios', href: '/precios' },
      ],
    },
    {
      label: 'Legal',
      links: [
        { text: 'Política de privacidad', href: '/legal/privacidad' },
        { text: 'Términos de uso', href: '/legal/terminos' },
        { text: 'Política de cookies', href: '/legal/cookies' },
      ],
    },
    {
      label: 'Empresa',
      links: [
        { text: 'Sobre nosotros', href: '/empresa/sobre-nosotros' },
        { text: 'Contacto', href: '/empresa/contacto' },
      ],
    },
  ] as const;

  protected readonly social = [
    {
      label: 'Perfil de GitHub de Sergio Durán Utrera',
      href: 'https://github.com/sdurutr436',
      text: 'GitHub',
    },
    {
      label: 'Perfil de LinkedIn de Sergio Durán Utrera',
      href: 'https://www.linkedin.com/in/sergio-dur%C3%A1n-utrera/',
      text: 'LinkedIn',
    },
  ] as const;
}
