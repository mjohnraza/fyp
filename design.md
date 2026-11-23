# Design System Specification
## "The Classical Scholar & Instrument" — Editorial Typography & UI Palette

This design system is formulated for the **Agentic Entrepreneur OS** and its **Human Needs & Entrepreneurial Curriculum Module**. It draws inspiration from mid-century academic typography, classical book design, and precise laboratory instruments.

---

## 1. Visual Philosophy
- **Editorial Gravity:** Centered on thought, memory recall, and deliberate decision-making rather than neon gamification or generic SaaS dashboards.
- **Warm Paper Aesthetic:** Uses a cream/parchment background (`#faf6ec`) to alleviate eye strain and evoke deep study.
- **Tactile Precision:** Borders, buttons, sticky timer bars, and flashcard widgets feel like refined physical stationery and scholarly instruments.

---

## 2. Color Palette & Tokens

```css
:root {
  --bg: #faf6ec;           /* Warm paper / parchment background */
  --surface: #fffdf8;      /* Clean card and panel background */
  --surface-alt: #f3ead2;  /* Tinted parchment for sticky controls & badges */
  --rule: rgba(139,101,20,0.24); /* Subtle antique gold rule / divider */
  --ink: #211a0f;          /* Deep carbon-sepia primary text */
  --ink-soft: #786646;     /* Muted walnut secondary text */
  --gold: #93630f;         /* Burnished brass / antique gold accent */
  --gold-bright: #b9860f;  /* Radiant gold for active indicators & numbers */
  --gold-wash: rgba(185,134,15,0.09); /* Golden tint for callouts & answers */
}
```

---

## 3. Typography

- **Display & Headings:** `Fraunces` (`serif`, optical sizing, weights 400..700). Used for page titles, section headings, blockquotes, Roman numerals, and numeric callouts.
- **Body & Controls:** `Inter` (`sans-serif`, weights 400..700). Clean, legible, highly neutral for paragraphs, tables, form inputs, and buttons.
- **Numeric Tabulars:** `font-variant-numeric: tabular-nums` for timers, scorecards, and progress trackers.

---

## 4. Recurring Architectural Components

### 4.1 Ornamental Rule (`.rule-orn`)
A classical horizontal rule bisected by a rotated diamond motif:
```html
<div class="rule-orn"><span></span></div>
```

### 4.2 Roman Numeral Stage / Need Callout (`.need-num`)
Used to number stages, fundamental needs, and pipeline tiers with italicized gold numerals.

### 4.3 Scholar's Blockquote
Centered italic statement bookended by twin 34px gold hair lines.

### 4.4 Tool Panel & Instruments (`.tool-panel`, `.timer`)
Subtle antique rule border, crisp white surface, and high-contrast ink buttons transitioning to antique gold.
