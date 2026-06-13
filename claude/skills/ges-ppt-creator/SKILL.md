---
name: ges-ppt-creator
description: Generate a GES (Global ERP Solution / 1C:Drive) ERP implementation proposal deck (.pptx) tailored to a client company. Use ONLY when the user explicitly asks to "generate a GES ppt", "create a GES proposal", or "make a GES ERP proposal deck". Do NOT load or use during normal coding work.
---

# ges-ppt-creator

Generates a GES-branded 1C:Drive ERP proposal deck for any client industry by cloning the master template and filling client-specific content. Acts as a senior ERP pre-sales consultant.

**Status:** Complete. Tailors every section — cover, Table of Contents (correct page numbers), Our Understanding, Requirements table (from `scope`), Solution landscape, Proposed Business Process, Business Benefits, Project Methodology timeline (months from `start_month`), Roles & Responsibility, Proposed Team, **Budgetary Commercials** (pricing table + auto TOTAL, with section divider), and **Assumptions** (with section divider). A global pass swaps the client name on every slide, so generated decks have **zero marine residue**. 33 slides.

## Operating rule: auto-draft soft, require hard

- **Auto-draft (then let the user edit):** the narrative — customer profile, categorized pain points, business-process stages, benefits, assumptions. Seed from the industry; never present them as final.
- **Require explicit input (never invent):** in-scope modules, timeline dates, team names, and commercials/pricing.

## Procedure

1. **Gather inputs, grouped by section** (one topic at a time):
   - **Basics (ask):** company name, industry, size, current system(s), proposal date.
   - **Understanding (draft → user edits):** a one-paragraph profile + 3 challenge categories with 3 items each, drawn from the industry.
   - **Process flow (draft → user edits):** 3–5 end-to-end stages, each with its steps, plus a loop note and a reporting note.
   - **Benefits (draft → user edits):** 8 benefits, each tied to a stated pain.
   - **Scope (ASK — never invent):** in-scope modules, each with its solution name, `Standard` / `Enhancement` / `Standard, Enhancement` tag, and a one-line scope function. Drives the Requirements table and Solution landscape.
   - **Timeline (ASK):** project `start_month`, duration in months, and stage names. Months are relabeled on the methodology slide from `start_month`.
   - **Commercials (ASK — never invent):** currency + line items (`item`, `qty`, `unit_price`) + payment terms. The deck computes line totals and the grand TOTAL.
   - **Assumptions (draft → user edits):** scope/environment/data/training caveats that protect the proposal.
   - The client name is swapped on every slide automatically (Roles, Team, landscape intro) — no separate step needed.

2. **Write the answers to `intake.json`** following `examples/intake.sample.json`.

3. **Generate the deck:**
   ```bash
   python3 ~/.claude/skills/ges-ppt-creator/assemble.py intake.json "Proposal <Company> v0.1.pptx"
   ```

4. **Preview it** so you and the user can see the result:
   ```bash
   bash ~/.claude/skills/ges-ppt-creator/render.sh "Proposal <Company> v0.1.pptx"
   ```
   Show the rendered slides (cover, Understanding, Process, Benefits). Confirm no leftover marine content.

5. **Polish loop:** edit `intake.json` and re-run until the user is satisfied. The original `v0.4` template is never modified.

## Excel fill-in workflow (when the user asks for a form / Excel / CSV)

When the user asks for a fill-in form ("give me an excel to fill", "generate a form", etc.):

1. **Generate a question-based Excel they can fill:**
   - If you have already drafted content for this client, pre-fill it with **prices left blank**:
     ```bash
     python3 ~/.claude/skills/ges-ppt-creator/ges_xlsx.py fromjson intake.json "<Company> - intake.xlsx" --blank-prices
     ```
   - If starting cold, emit the blank template:
     ```bash
     python3 ~/.claude/skills/ges-ppt-creator/ges_xlsx.py blank "<Company> - intake.xlsx"
     ```
   The sheet has a **Question** column and an **Answer** column (one row per answer; a hidden `Key` column maps them). The user types into the highlighted Answer column.
2. The user fills / edits the answers — especially the commercial **unit prices**, currency, and terms.
3. **Generate the deck straight from the Excel** — `assemble.py` auto-detects `.xlsx`:
   ```bash
   python3 ~/.claude/skills/ges-ppt-creator/assemble.py "<Company> - intake.xlsx" "Proposal <Company> v0.1.pptx"
   ```
4. Render and polish as usual.

(`assemble.py` also accepts `intake.json` and `intake.csv`; `ges_csv.py` is a dependency-free CSV equivalent if a plain-text form is preferred. Prices may use thousands separators — `4.500.000` or `4500000`.)

## Files

- `template/ges-proposal.pptx` — GES master template (33 slides). **Sanitized**: uses a neutral sample client name (`PT Contoh Klien` / `PT CK`) that is swapped to the real client on every run — no real client data is stored in the skill.
- `template/intake-template.xlsx` — blank question-based fill-in form.
- `assemble.py` — assembler; accepts `intake.xlsx`, `intake.csv`, or `intake.json`.
- `ges_xlsx.py` — Excel ↔ intake converter (`blank` / `fromjson` / `tojson`). Requires `openpyxl`.
- `ges_csv.py` — CSV ↔ intake converter (dependency-free fallback).
- `examples/intake.sample.json` — a complete non-marine (manufacturing) example.
- `render.sh` — LibreOffice → per-slide PNG preview (requires LibreOffice + poppler).

- `template/ges-proposal.pptx` — GES master template (keeps branding, dividers, methodology, team, about-us).
- `assemble.py` — dependency-free assembler (raw OOXML; no python-pptx required).
- `examples/intake.sample.json` — a filled non-marine (manufacturing) example.
- `render.sh` — LibreOffice → per-slide PNG preview (requires LibreOffice + poppler).
