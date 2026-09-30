# UI Design Gate (Phase 1a + Phase 3 addendum)

Adapted from oil-oil/oil-ui. Use only for **major UI changes**: a new screen, a redesign, a new
visual direction. Skip for a tweak, a new field, or a config-driven form that syscon already renders.
Taste decisions belong to me. Execution belongs to the AI.

## Phase 1a — Before the spec

1. **Set the tone.** Score five dimensions, each with one line of reasoning. No adjectives like
   "premium" or "clean".
   - energy (calm ↔ urgent)
   - completeness (sketch ↔ finished)
   - density (sparse ↔ packed)
   - weight (light ↔ heavy)
   - formality (playful ↔ strict)
2. **Find an engine per direction.** An engine is a concrete source: a material, a place of use,
   a scenario, a design movement. Derive it from the product content, the audience, and where the
   screen is used. Never from a trend or a style library. Skip the engine when an existing design
   system already fixes the look; then vary layout only.
3. **Draw a skeleton per direction.** A 3–5 box wireframe, before any copy. Skeletons differ
   inside one round. A left/right split appears at most once. One direction must be bold.
4. **Check differentiation.** Any two directions share at most ONE of: skeleton, typeface, color,
   key visual. More than one shared = a recolor, not a direction. Redo it.
5. **Render one comparison page.** One self-contained HTML file with all directions side by side,
   a desktop/mobile toggle, and keyboard navigation. Build it with `impeccable` or `frontend-design`.
   Write to `docs/<feature>-directions.html`.
6. **I choose.** I pick a direction and give feedback. Do not sand the directions into one middle
   option. Do not start Phase 1b before I choose.

The spec then carries: the chosen direction, its tone scores, its skeleton, the type and color
decisions, and the states the screen must show (empty, loading, error, full).
Do not build a new design system for one tweak.

## Phase 3 addendum — Reality check and reduction

Add these to the reviewer brief and to my Phase 4 check.

- **Real render.** Run the screen at real viewport sizes, desktop and mobile, at 100% and 200%
  zoom. A scaled-down preview or added decoration does not count.
- **Reduce.** Delete the text one section at a time. Restore only what breaks comprehension.
  Keep object names, decision reasons, state, and primary actions.
- **Browser checks:** read `document.hidden` first. A hidden tab fakes every motion fault.
