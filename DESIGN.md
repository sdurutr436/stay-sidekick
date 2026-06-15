---
name: Stay Sidekick
colors:
  surface: '#fef8f4'
  surface-dim: '#ded9d5'
  surface-bright: '#fef8f4'
  surface-container-lowest: '#fdfaf2'
  surface-container-low: '#f8f3ee'
  surface-container: '#f2ede9'
  surface-container-high: '#ede7e3'
  surface-container-highest: '#e7e1dd'
  on-surface: '#1d1b19'
  on-surface-variant: '#4b463d'
  inverse-surface: '#32302d'
  inverse-on-surface: '#f5f0eb'
  outline: '#7d766c'
  outline-variant: '#cec5b9'
  surface-tint: '#9c661c'
  primary: '#9c661c'
  on-primary: '#ffffff'
  primary-container: '#f7e6c4'
  on-primary-container: '#73664b'
  inverse-primary: '#d5c5a4'
  secondary: '#645e51'
  on-secondary: '#ffffff'
  secondary-container: '#e8dece'
  on-secondary-container: '#696255'
  tertiary: '#5b5d6f'
  on-tertiary: '#ffffff'
  tertiary-container: '#e5e6fc'
  on-tertiary-container: '#646679'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#f2e1bf'
  primary-fixed-dim: '#d5c5a4'
  on-primary-fixed: '#231b06'
  on-primary-fixed-variant: '#50462d'
  secondary-fixed: '#ebe1d1'
  secondary-fixed-dim: '#cfc5b6'
  on-secondary-fixed: '#1f1b11'
  on-secondary-fixed-variant: '#4c463a'
  tertiary-fixed: '#e0e1f7'
  tertiary-fixed-dim: '#c4c5da'
  on-tertiary-fixed: '#181b2a'
  on-tertiary-fixed-variant: '#434657'
  background: '#fef8f4'
  on-background: '#1d1b19'
  surface-variant: '#e7e1dd'
  header: '#f3e6c9'
  body-gradient-from: '#f3e6c9'
  body-gradient-to: '#faf6ea'
  footer: '#faf6ea'
  btn-primary: '#9c661c'
  btn-primary-hover: '#cf871f'
typography:
  display-2xl:
    fontFamily: Archivo Narrow
    fontSize: 64px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-xl:
    fontFamily: Archivo Narrow
    fontSize: 48px
    fontWeight: '800'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  display-lg:
    fontFamily: Archivo Narrow
    fontSize: 36px
    fontWeight: '800'
    lineHeight: '1.2'
    letterSpacing: -0.01em
  h1:
    fontFamily: Archivo Narrow
    fontSize: 36px
    fontWeight: '700'
    lineHeight: '1.2'
  h2:
    fontFamily: Archivo Narrow
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.3'
  h3:
    fontFamily: Archivo Narrow
    fontSize: 24px
    fontWeight: '700'
    lineHeight: '1.4'
  h4:
    fontFamily: Archivo Narrow
    fontSize: 20px
    fontWeight: '700'
    lineHeight: '1.4'
  body-xl:
    fontFamily: Archivo Narrow
    fontSize: 18px
    fontWeight: '500'
    lineHeight: '1.6'
  body-md:
    fontFamily: Archivo Narrow
    fontSize: 16px
    fontWeight: '500'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Archivo Narrow
    fontSize: 12px
    fontWeight: '500'
    lineHeight: '1.5'
  caption:
    fontFamily: Archivo Narrow
    fontSize: 12px
    fontWeight: '400'
    lineHeight: '1.4'
  h1-mobile:
    fontFamily: Archivo Narrow
    fontSize: 28px
    fontWeight: '700'
    lineHeight: '1.2'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  2xl: 48px
  3xl: 64px
  gutter: 24px
  margin-mobile: 16px
  margin-desktop: 40px
---

## Brand & Style

The design system is engineered for a professional, utility-first travel and hospitality experience. It prioritizes clarity, efficiency, and a refined functional aesthetic that feels dependable yet premium. 

The style leans into **Modern Corporate Minimalism** with a focus on high-density information architecture. It is built on a **warm amber palette**: the page flows top-to-bottom through a vertical gradient, while a saturated dark amber drives primary actions. The interface should feel "architectural"—defined by precise alignments, generous whitespace within components, and a rigorous adherence to a systematic grid.

## Colors

This design system is **amber-forward and warm**. The chrome is organised as a single vertical flow:

- **Page Gradient:** The header sits on a stable warm amber (`#f3e6c9`). The body background is a vertical gradient that begins at that same stable tone (just under the header) and descends to a fainter, near-white warm tone (`#faf6ea`). The footer and the final CTA's legal note rest on that faint endpoint, so header → body → footer read as one continuous descent.
- **Primary Actions:** Buttons use a **dark amber** fill (`#9c661c`) with white text; on hover they *lighten* (`#cf871f`) rather than darken. In dark mode the amber brightens to a glow with dark text.
- **Accent:** The pale amber (`hsl(47.4419, 64.1791%, 86.8627%)`) remains for focus states, active chips and selection highlights.
- **Surfaces:** Cards, inputs and secondary buttons are **never cold white**. They use warm, low-saturation cream tones (a desaturated amber) so they harmonize with the gradient. A clear tonal hierarchy keeps them legible: cards are the lightest (lift off the canvas), the base/input surface sits one step down, and alt panels/badges are a slightly deeper cream. Warm taupe 1px borders define every surface.
- **Light Mode:** Cards stay the lightest warm tone so they lift cleanly off the gradient; their warm border carries the separation where the gradient is palest.
- **Dark Mode:** Use deep warm charcoal tones; the gradient runs from a warm charcoal header down to a near-obsidian footer. Avoid pure black except at the deepest base.

## Typography

The typography system relies on **Archivo** to convey a utilitarian, modern tone. 

- **Display Scales:** Use 800 weight for high-impact marketing or hero sections. Tighten letter spacing slightly at these sizes.
- **Headings:** Use 700 weight. Ensure clear vertical rhythm by maintaining a 1.4x line-height ratio for smaller headers.
- **Body/Labels:** Set at 500 weight to provide a slightly more "filled" look than standard book weights, enhancing legibility on screens.
- **Captions:** Use 400 weight for metadata, legal text, or secondary annotations.

## Layout & Spacing

This design system uses a **12-column fluid grid** for desktop and a **4-column fluid grid** for mobile.

- **Spacing Rhythm:** Based on a 4px baseline. All padding, margins, and gaps must be multiples of 4.
- **Desktop:** 1200px max-width container, centered. 24px gutters.
- **Mobile:** Full width with 16px side margins.
- **Alignment:** Consistent vertical alignment is critical. Use `spacing-lg` (24px) for standard grouping and `spacing-2xl` (48px) to separate distinct sections of content.

## Elevation & Depth

The design system uses **Tonal Layering** and **Low-Contrast Outlines** rather than heavy shadows to maintain a clean, professional look.

- **Level 0 (Background):** Base page color.
- **Level 1 (Surface):** Subtle shift (e.g., 2% lighter or darker than background) to define cards or sections.
- **Outlines:** Use 1px borders for all interactive elements and containers. In light mode, use a warm taupe (`#b7ab9a`); in dark mode, use a warm charcoal (`#494440`).
- **Focus States:** When an element is focused or active, transition the border color to the Amber accent or use a 2px solid stroke. Shadows should be avoided unless used as a very soft, 10% opacity ambient glow for modals.

## Shapes

The shape language is **Soft** and restrained.

- **Components:** Standard buttons, input fields, and small cards use a 0.25rem (4px) corner radius.
- **Large Containers:** Modals or large feature cards use a 0.5rem (8px) corner radius (`rounded-lg`).
- **Icons:** Use square or slightly rounded icons that match the 4px logic. Avoid circular "pill" shapes unless used for tags or status chips to create visual contrast against the otherwise rectilinear UI.

## Components

- **Buttons:** 
    - *Primary:* Dark amber background (`#9c661c`), white text, 500 weight. No border. **Lightens** on hover (`#cf871f`).
    - *Secondary:* Transparent background, 1px achromatic border, text-primary.
    - *Ghost:* No background or border, text-secondary.
- **Input Fields:** 1px achromatic border, 4px radius. On focus, the border changes to Amber. Placeholder text in `body-sm` 400 weight.
- **Chips:** Small, 0.75rem font size. Use Amber background for "active" or "selected" and a light gray for "default."
- **Cards:** Defined by a 1px border. No shadow. Padding should be a minimum of `spacing-lg` (24px) to ensure a premium feel.
- **Lists:** Use `spacing-md` for vertical gaps between items. Separate items with a 1px horizontal rule using the system border color.
- **Checkboxes/Radios:** Use the Amber accent for the checked state to ensure high visibility against the neutral background.