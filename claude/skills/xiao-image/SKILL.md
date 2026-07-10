---
name: xiao-image
description: Generate Ian-style hand-drawn article illustrations starring Xiaohei (小黑) — a deadpan little black creature doing absurd-but-accurate work. Use when the user asks for "illustrations", "article images", "blog images", "body illustrations", "shot list", "doodle explainers", "hand-drawn diagrams", or visuals for articles, posts, blogs, Notion docs, workflow docs, methodologies, processes, structures, states, metaphors, or opinions. Default style: pure-white hand-drawn sketches, sparse red/orange/blue annotations, clean and minimal but wonderfully weird.
---

# Xiaohei Absurd Article Illustrations

## The pitch

Design and generate 16:9 landscape illustrations for article bodies. The goal is NOT commercial illustration, PPT infographics, or cute cartoons — it's turning an article's key judgment, process, structure, state, or metaphor into one clean, weird, inventive hand-drawn explainer that reads instantly but never smells like a manual.

The house IP is **Xiaohei (小黑)**: solid black body, white dot eyes, thin legs, blank expression — earnestly doing something absurd that somehow holds up. Xiaohei must perform the core action of every image, never stand around as decoration.

## Read these first

Load per task — don't stuff the whole set into context at once:

- `references/style-dna.md`: style DNA, colors, text, hard bans.
- `references/xiaohei-ip.md`: Xiaohei's look, personality, action library, and taboos.
- `references/composition-patterns.md`: structure types, original-metaphor method, anti-copying rules.
- `references/prompt-template.md`: the per-image generation prompt template.
- `references/qa-checklist.md`: post-generation checks and iteration rules.
- `assets/examples/`: rare visual calibration only — never in the default path. Never copy their compositions, props, or labels.

## Workflow

### 1. Digest the article

Read whatever the user gives you — text, link, Notion page, Markdown file, screenshot. Extract:

- The core argument
- Which paragraphs carry a cognitive turn
- What genuinely benefits from a picture
- What should stay as text, no image needed

Don't illustrate evenly. Prioritize "cognitive anchors": the core judgment, two breakpoints, an input→output loop, a fork, a before/after, one-input-many-outputs, a handoff path, common pitfalls, a character's state change.

### 2. Shot list before pixels

If the user only asks "figure out where images should go / how to illustrate this," deliver a shot list first. For each shot:

- Which paragraph it follows
- The image's subject
- The one idea it must land
- Structure type
- What Xiaohei is doing in it
- Suggested props
- Suggested handwritten labels

Default 4–8 shots. Short article: 1–3. Even long pieces rarely deserve more than 9. Enough is enough — don't turn an article into a picture book.

### 3. Generate one at a time

If the user explicitly says "generate / make / output the images," don't stop to ask for confirmation; generate each image individually with the built-in `image_gen`. Never collage multiple shots into one image.

One image = one core structure. Every prompt must include:

- 16:9 landscape article illustration
- Pure white background
- Black hand-drawn line art
- A few red/orange/blue handwritten annotations
- Lots of white space
- Xiaohei as the actor of the core action
- Bans: PPT look, commercial illustration, childish-cute, complex architecture, top-left category title

Never re-carve past examples. Examples only teach line density and how Xiaohei participates — do not reuse existing compositions ("conveyor-belt breakpoints / Xiaohei pulling threads / the content fish / the stamp toolbox / the pitfalls path") unless the user explicitly asks for a remake. Every article gets a freshly invented metaphor: strange, but it holds.

### 4. Check and iterate

After generation, run `references/qa-checklist.md`. Regenerate or spot-edit if:

- Xiaohei is just decoration
- The canvas is crowded
- It reads like a flowchart or PPT slide
- Labels are too many or badly garbled
- A category title ("Common Pitfalls / Workflow / System Architecture") appears top-left
- The style is cute, childish, or stiff
- The background isn't clean white

### 5. Save and deliver

If working inside a workspace, copy final images to:

```text
assets/<article-slug>-illustrations/
```

Named in order:

```text
01-topic-name.png
02-topic-name.png
```

Keep the raw generations; never overwrite existing assets unless the user explicitly asks for replacement.

## Output style

Pre-generation strategy: short and sharp. Post-generation delivery must include:

- How many images were made
- What each one is for
- Where they're saved
- Which shots are rock-solid and which are optional

No essays on style theory — let the images do the talking.
