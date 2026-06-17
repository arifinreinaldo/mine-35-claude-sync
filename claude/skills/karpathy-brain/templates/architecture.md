# Architecture — {{PROJECT_NAME}}

> System shape from the seed pass. One level deep; details go in `areas/`.
> Stack: {{STACK}}

## Entry points
- {{ENTRYPOINTS}}

## Shape (top-level)
_(seed: top-level dirs and what each owns)_

## Primary data flow
_(seed: request/event → handling → state → output, one paragraph)_

## Room shape (template for `areas/<feature>.md`)
- **Purpose** — what this area does.
- **Key files** — code paths (mirror into [[code_map]]).
- **State** — where state lives / who owns truth.
- **Edges** — what breaks if changed; timing/ordering notes.
