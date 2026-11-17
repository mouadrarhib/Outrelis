# Outrelis authentication design

Visual authority: the user-supplied `../Outrelis-Authentication-Experience/index.html`,
`styles.css`, and local assets. This is a React port of that direction, not a redesign.
Surface mode: Operate (create an account or sign in).

| Token | Value |
|---|---|
| Principal canvas | `#344C40` |
| Foreground | `#FAF8F2` |
| Primary action | `#C43D2B` |
| Supporting foreground | Paper at 86% |
| Dividers | Paper at 24% |
| Field borders | Paper at 58% |
| Quiet brand surface | Paper at 4.5% |
| Display | Instrument Serif, 400, normal/italic |
| Body | DM Sans, 400/500/600 |
| Controls | 52px minimum height, 4px radius |
| Gutters | 80px wide desktop, 56px desktop, 32px tablet, 20px mobile |
| Motion | 180ms feedback; 300ms GSAP view entrance, ease-out |

Preserve the two-column sage composition above 767px. Below that breakpoint,
hide the illustration panel and move the logo above the form. Font files are local
with bundled OFL licenses. Keep SVG geometry and wordmark proportions intact.

Use real labels, keyboard focus, autocomplete, inline validation, loading and
recoverable API errors. Disable submissions while pending. All reduced-motion
views stay fully visible. Match backend password rules; never show simulated
account creation or password-reset success. Do not invent product statistics.

The desktop discovery SVG plays a one-shot GSAP story: pin arrives, a single halo
settles, the dashed route is revealed through an SVG mask, and the saved check
draws in. The sequence lasts about 2.6 seconds and plays once without looping.
Mobile and reduced-motion views keep static art.
