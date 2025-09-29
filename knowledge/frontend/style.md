# Frontend Style

The project’s frontend uses **TailwindCSS**, **shadcn/ui**, and **Framer Motion**.  
Goal: a clean, consistent, and delightful UI.

---

## Principles
- **Clarity**: simple layouts, readable typography.  
- **Consistency**: shared design tokens, reusable components.  
- **Delight**: subtle animations to guide user focus.  
- **Responsiveness**: mobile-first, flexible grids.  

---

## TailwindCSS
- Utility-first classes for layout, spacing, typography.  
- Base styling for custom components.  
- Design tokens defined in `tailwind.config.js`.  

---

## shadcn/ui
- Provides accessible, production-ready components (Button, Dialog, Input, Select, etc.).  
- Used as the **UI kit foundation**, styled via Tailwind.  
- Extendable for project-specific components.  
- Ensures consistent design language across forms, modals, and tables.  

---

## Framer Motion
- Page transitions, modals, progress bars, and charts.  
- Animations short and smooth (<250ms).  
- Motion supports UX flow, never distracts.  

---

## Components
- **Core**: Button, Input, Modal, Drawer, Table, Card, Progress.  
- **Layout**: Sidebar, Topbar, Page container.  
- **Charts**: Donut, Line, Bar (animated on load).  
- **Forms**: built on shadcn/ui inputs + Tailwind utility classes.  

---

# Summary
**Tailwind** handles base styling,  
**shadcn/ui** supplies accessible UI primitives,  
**Framer Motion** adds subtle delight.  
The result: a clear, consistent, responsive design system.
