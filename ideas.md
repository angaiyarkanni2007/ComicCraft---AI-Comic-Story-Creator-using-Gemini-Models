# ComicCraft Design Brief

## Direction: Ink & Signal

ComicCraft is a creative instrument, not a generic dashboard. The visual language combines the warmth of a printed comic zine with the precision of a modern studio tool: paper-like surfaces, ink outlines, electric accent colors, and deliberately editorial composition.

- **Design movement:** contemporary editorial comic-book interface with tactile print cues.
- **Core principles:** make the blank page feel inviting; keep the prompt-to-panel journey obvious; let generated art be the hero; use UI chrome as a supportive studio rail.
- **Color philosophy:** warm bone `#F8F1E7` for the canvas, ink `#17151F` for high-contrast text, electric violet `#7657FF` for creative actions, coral `#FF6F61` for energy and highlight, citrus `#FFC857` for metadata and sparks, and muted sage `#B7C9B1` for positive progress states.
- **Layout paradigm:** split-screen editor on desktop (story brief rail + live comic canvas), single-column flow on mobile. Panels use thick ink borders, offset shadows, and varied but controlled card rhythm.
- **Signature elements:** halftone sunburst background, sticker-like model badges, chunky step numerals, small uppercase labels, hand-cut corner shapes, and a violet comet/speech-bubble logo.
- **Interaction philosophy:** clear stages, immediate feedback, forgiving defaults, and visible model provenance. Inputs should feel like a creative prompt sheet; generation states should feel like a page being inked.
- **Animation:** short, purposeful transitions only: progress steps light in sequence; panel cards rise into place with a slight stagger; respect reduced-motion preferences.
- **Typography system:** `Space Grotesk` for display and UI labels, `DM Sans` for body copy, with `Bricolage Grotesque` as an accent for pull quotes and dialogue. Use CSS fallbacks so the app remains offline-friendly.
- **Brand essence:** a small studio partner that turns a spark into a story.
- **Brand voice:** encouraging, specific, a little playful, never childish; prefer “shape the scene” over “submit.”
- **Wordmark/logo:** ComicCraft wordmark paired with a filled violet comet cutting through a coral speech bubble; the negative space suggests both a panel gutter and a spark of an idea.
- **Signature brand color:** electric violet `#7657FF`.

## Planned placements

1. Generated project logo in the header, favicon, and managed project metadata.
2. Small halftone/ink motifs in the hero and form rail, built with CSS rather than extra image assets.
3. Generated panel artwork is runtime content; no generic stock imagery is used.
