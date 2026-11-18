# Outrelis authentication design

Visual authority: the implemented React authentication interface and its local
assets. Preserve this direction while extending the authenticated product.
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

Inline success and error feedback uses the source-owned beUI Animated Alert,
adapted to the existing 4px controls and sage/paper/tomato palette. Error copy
names the failed action and gives a recovery step; backend error codes drive the
message while internal server details remain hidden.

The desktop discovery SVG plays a one-shot GSAP story: pin arrives, a single halo
settles, the dashed route is revealed through an SVG mask, and the saved check
draws in. The sequence lasts about 2.6 seconds and plays once without looping.
Mobile and reduced-motion views keep static art.

The authenticated starting-path stage leaves the split authentication frame and
uses a single centered decision surface. Two beUI radio rows share one bordered
list rather than separate cards. The page keeps the established palette, type,
focus treatment and 52px primary action, with the logo and sign-out action in a
quiet product header.
