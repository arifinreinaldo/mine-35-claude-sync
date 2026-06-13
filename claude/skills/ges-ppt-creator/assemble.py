#!/usr/bin/env python3
"""ges-ppt-creator assembler (MVP, dependency-free).

Clones the GES master template and fills client-specific content from an intake
JSON using raw OOXML edits (no python-pptx needed). MVP scope: cover, Our
Understanding, Proposed Business Process, Business Benefits. Other sections
(requirements table, timeline, team, commercials, assumptions) are kept from the
template for now and filled in later iterations.

Usage:  python3 assemble.py intake.json [output.pptx]
"""
import json, sys, re, zipfile, pathlib

SKILL = pathlib.Path(__file__).resolve().parent
TEMPLATE = SKILL / "template" / "ges-proposal.pptx"

# Slide-4 challenge-column headers + body anchors in the marine master template.
MARINE_HEADERS = ["Maintenance Challenges", "Procurement Challenges", "Reporting Challenge"]
BODY_ANCHORS = ["Side Selection", "Purchasing Info Record", "oil consumption"]  # one per challenge column
PROFILE_ANCHOR = "requires an integrated ERP"
MARINE_BENEFITS = [
    "Increased operational efficiency through process automation",
    "Improved data accuracy and transparency",
    "Faster approval cycles with online workflows",
    "Better control over spare parts and inventory",
    "Reduced risk of duplicate purchases and POs",
    "Enhanced maintenance planning and asset reliability",
    "Reduced manual reporting effort and administrative workload",
    "Improved decision-making through real-time dashboards and analytics",
]


def esc(s):
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ---------- slide 1: cover ----------
def fill_cover(x, d):
    c = d["company"]
    x = x.replace("June 2026", esc(c.get("date", "")))  # client name handled by global pass
    # remove the marine hero photo (rId3) -> clean neutral GES background
    for pic in re.findall(r"<p:pic>.*?</p:pic>", x, re.S):
        if 'r:embed="rId3"' in pic:
            x = x.replace(pic, "", 1)
            break
    return x


# ---------- slide 4: Our Understanding ----------
def _replace_body(x, anchor, bullets):
    """Rebuild the paragraphs of the <p:sp> containing `anchor`, reusing its
    first paragraph as the style template and swapping in `bullets`."""
    sp = next((s for s in re.findall(r"<p:sp>.*?</p:sp>", x, re.S) if anchor in s), None)
    if sp is None:
        return x
    m = re.search(r"(<p:txBody>)(.*?)(</p:txBody>)", sp, re.S)
    inner = m.group(2)
    paras = re.findall(r"<a:p>.*?</a:p>", inner, re.S)
    if not paras:
        return x
    prefix = inner[:inner.index("<a:p>")]  # preserve <a:bodyPr> + <a:lstStyle/>
    style = next((p for p in paras if "<a:t>" in p), paras[0])
    new_paras = "".join(
        re.sub(r"<a:t>.*?</a:t>", "<a:t>" + esc(b) + "</a:t>", style, count=1, flags=re.S)
        for b in bullets if b
    )
    new_sp = sp.replace(m.group(0), m.group(1) + prefix + new_paras + m.group(3))
    return x.replace(sp, new_sp, 1)


def fill_understanding(x, d):
    u = d["understanding"]
    ch = u["challenges"]
    # column headers -> client challenge categories
    for i, marine in enumerate(MARINE_HEADERS):
        if i < len(ch):
            x = x.replace(marine, esc(ch[i]["category"]))
    # profile column body
    prof = [u.get("profile", "")]
    if u.get("current_system"):
        prof.append(u["current_system"])
    x = _replace_body(x, PROFILE_ANCHOR, prof)
    # challenge column bodies
    for i, anchor in enumerate(BODY_ANCHORS):
        if i < len(ch):
            x = _replace_body(x, anchor, ch[i]["items"])
    return x


# ---------- slide 8: Proposed Business Process ----------
def fill_process(x, d):
    p = d["process"]
    stages = p["stages"]
    LM, gap = 457200, 280000
    avail = 12192000 - 2 * LM
    n = len(stages)
    cardW = int((avail - (n - 1) * gap) / n)
    xs = [LM + i * (cardW + gap) for i in range(n)]
    cardY, cardH = 1450000, 2900000
    TEAL, TEAL_D, TINT, ORANGE, BAR, DARK = "31859B", "1B5E72", "E8F1F4", "C8732D", "21465E", "333333"

    def title_p(t):
        return ('<a:p><a:pPr algn="ctr"><a:spcAft><a:spcPts val="600"/></a:spcAft></a:pPr>'
                '<a:r><a:rPr lang="en-US" sz="1300" b="1"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                '<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p>' % (TEAL_D, esc(t)))

    def step_p(t):
        return ('<a:p><a:pPr marL="155575" indent="-155575"><a:spcBef><a:spcPts val="400"/></a:spcBef>'
                '<a:buFont typeface="Arial"/><a:buChar char="•"/></a:pPr>'
                '<a:r><a:rPr lang="en-US" sz="1000"><a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
                '<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p>' % (DARK, esc(t)))

    shapes, sid = [], 600
    for st, cx in zip(stages, xs):
        body = title_p(st["title"]) + "".join(step_p(s) for s in st["steps"])
        shapes.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Stage"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 4500"/></a:avLst></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="%s"/></a:solidFill>'
            '<a:ln w="15875"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></p:spPr>'
            '<p:txBody><a:bodyPr anchor="t" lIns="100000" tIns="91440" rIns="91440" bIns="68580" wrap="square"><a:noAutofit/></a:bodyPr>'
            '<a:lstStyle/>%s</p:txBody></p:sp>' % (sid, cx, cardY, cardW, cardH, TINT, TEAL, body))
        sid += 1
    ay, aw, ah = cardY + cardH // 2 - 140000, 240000, 280000
    for i in range(n - 1):
        ax = ((xs[i] + cardW) + xs[i + 1]) // 2 - aw // 2
        shapes.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Arrow"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="%d" y="%d"/><a:ext cx="%d" cy="%d"/></a:xfrm>'
            '<a:prstGeom prst="rightArrow"><a:avLst/></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
            '<p:txBody><a:bodyPr/><a:lstStyle/><a:p><a:endParaRPr lang="en-US"/></a:p></p:txBody></p:sp>'
            % (sid, ax, ay, aw, ah, ORANGE)); sid += 1
    fullW = xs[-1] + cardW - LM
    if p.get("loop_note"):
        shapes.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Loop"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="%d" y="4520000"/><a:ext cx="%d" cy="360000"/></a:xfrm>'
            '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 50000"/></a:avLst></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="F3EBE2"/></a:solidFill><a:ln w="9525"><a:solidFill><a:srgbClr val="%s"/></a:solidFill></a:ln></p:spPr>'
            '<p:txBody><a:bodyPr anchor="ctr" lIns="91440" rIns="91440" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="1000" i="1"><a:solidFill><a:srgbClr val="8A4B16"/></a:solidFill>'
            '<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
            % (sid, LM, fullW, ORANGE, esc(p["loop_note"]))); sid += 1
    if p.get("reporting_note"):
        shapes.append('<p:sp><p:nvSpPr><p:cNvPr id="%d" name="Reporting"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            '<p:spPr><a:xfrm><a:off x="%d" y="5400000"/><a:ext cx="%d" cy="490000"/></a:xfrm>'
            '<a:prstGeom prst="roundRect"><a:avLst><a:gd name="adj" fmla="val 12000"/></a:avLst></a:prstGeom>'
            '<a:solidFill><a:srgbClr val="%s"/></a:solidFill><a:ln><a:noFill/></a:ln></p:spPr>'
            '<p:txBody><a:bodyPr anchor="ctr" lIns="91440" rIns="91440" wrap="square"><a:noAutofit/></a:bodyPr><a:lstStyle/>'
            '<a:p><a:pPr algn="ctr"/><a:r><a:rPr lang="en-US" sz="1050" b="1"><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            '<a:latin typeface="Arial"/><a:cs typeface="Arial"/></a:rPr><a:t>%s</a:t></a:r></a:p></p:txBody></p:sp>'
            % (sid, LM, fullW, BAR, esc(p["reporting_note"])))
    # remove the WIP placeholder shape, inject the diagram
    wip = next((s for s in re.findall(r"<p:sp>.*?</p:sp>", x, re.S) if re.search(r"<a:t>\s*WIP\s*</a:t>", s)), None)
    if wip:
        x = x.replace(wip, "", 1)
    return x.replace("</p:spTree>", "".join(shapes) + "</p:spTree>")


# ---------- slide 9: Business Benefits ----------
def fill_benefits(x, d):
    for i, marine in enumerate(MARINE_BENEFITS):
        new = d["benefits"][i] if i < len(d["benefits"]) else ""
        x = x.replace("<a:t>%s</a:t>" % marine, "<a:t>%s</a:t>" % esc(new))
    return x


# ---------- shared table-cell helper ----------
def _set_row_cells(row, vals):
    """Set the first <a:t> of each cell to its value; blank any extra runs."""
    out = row
    for tc, v in zip(re.findall(r"<a:tc>.*?</a:tc>", row, re.S), vals):
        seen = [False]
        def repl(_m):
            if not seen[0]:
                seen[0] = True
                return "<a:t>" + esc(v) + "</a:t>"
            return "<a:t></a:t>"
        out = out.replace(tc, re.sub(r"<a:t>.*?</a:t>", repl, tc, flags=re.S), 1)
    return out


# ---------- slide 6: Requirements mapping table ----------
def fill_requirements(x, d):
    scope = d.get("scope")
    m = re.search(r"<a:tbl>.*?</a:tbl>", x, re.S)
    if not scope or not m:
        return x
    tbl = m.group(0)
    rows = re.findall(r"<a:tr.*?</a:tr>", tbl, re.S)
    header, tpl = rows[0], rows[2]                  # row 2 is a normal 3-cell data row
    new_tbl = tbl
    for r in rows:
        if r not in (header, tpl):
            new_tbl = new_tbl.replace(r, "", 1)
    built = "".join(
        _set_row_cells(tpl, ["%s — %s" % (s["module"], s["solution"]), s.get("type", ""), s.get("scope_function", "")])
        for s in scope
    )
    return x.replace(tbl, new_tbl.replace(tpl, built, 1))


# ---------- slide 7: Solution landscape (genericize marine labels) ----------
LANDSCAPE_RELABEL = {
    "RMI": "OPERATIONS",
    "Requirement List Transaction": "Operational Transactions",
    "Tugboat Master Data": "Item Master Data",
    "Barge Master Data": "Customer Master Data",
    "Engine Data": "Warehouse & Location",
    "Deck Group": "Item Group",
    "Machine Group": "Price List",
}
def fill_landscape(x, d):
    for old, new in LANDSCAPE_RELABEL.items():
        x = x.replace("<a:t>%s</a:t>" % old, "<a:t>%s</a:t>" % esc(new))
    return x


# ---------- slide 14: Project Methodology timeline (relabel months from start_month) ----------
_MONTHS = ["January", "February", "March", "April", "May", "June",
           "July", "August", "September", "October", "November", "December"]
_TEMPLATE_MONTHS = ["July", "August", "September", "October", "November", "December"]
def fill_timeline(x, d):
    start = (d.get("methodology") or {}).get("start_month")
    if start not in _MONTHS:
        return x
    si = _MONTHS.index(start)
    seq = [_MONTHS[(si + i) % 12] for i in range(len(_TEMPLATE_MONTHS))]
    for i, old in enumerate(_TEMPLATE_MONTHS):       # mark first to avoid chained replaces
        x = x.replace("<a:t>%s</a:t>" % old, "<a:t>@@M%d@@</a:t>" % i, 1)
    for i, new in enumerate(seq):
        x = x.replace("<a:t>@@M%d@@</a:t>" % i, "<a:t>%s</a:t>" % new)
    return x


# ---------- global client-name replacement (runs on every slide) ----------
def replace_client_name(x, d):
    name = d["company"]["name"]
    short = d["company"].get("short_name", name)
    for old in ("PT CONTOH KLIEN", "PT Contoh Klien", "Contoh Klien"):
        x = x.replace(old, esc(name))
    x = x.replace("PT CK", esc(short))
    return x


# ---------- Budgetary Commercials slide (added section) ----------
def fill_commercials(x, d):
    c = d.get("commercials")
    m = re.search(r"<a:tbl>.*?</a:tbl>", x, re.S)
    if not c or not m:  # no-op on the TOC slide (has the title text but no table)
        return x
    tbl = m.group(0)
    tpl = re.findall(r"<a:tr.*?</a:tr>", tbl, re.S)[-1]  # the "—|—|—" template data row
    cur = c.get("currency", "")
    fmt = lambda n: "{:,.0f}".format(n)

    def set_cells(row, vals):
        out = row
        for tc, v in zip(re.findall(r"<a:tc>.*?</a:tc>", row, re.S), vals):
            new_tc = re.sub(r"<a:t>.*?</a:t>", "<a:t>" + esc(v) + "</a:t>", tc, count=1, flags=re.S)
            out = out.replace(tc, new_tc, 1)
        return out

    built, total = "", 0
    for li in c["line_items"]:
        amt = li["qty"] * li["unit_price"]; total += amt
        built += set_cells(tpl, [li["item"], "%s × %s" % (li["qty"], fmt(li["unit_price"])), "%s %s" % (cur, fmt(amt))])
    built += set_cells(tpl, ["TOTAL", "", "%s %s" % (cur, fmt(total))])
    return x.replace(tbl, tbl.replace(tpl, built, 1))


# ---------- Assumptions slide (added section) ----------
def fill_assumptions(x, d):
    if not d.get("assumptions"):
        return x
    return _replace_body(x, "ASSUMPTIONS_PLACEHOLDER", d["assumptions"])


SLIDE_FILLERS = {
    "ppt/slides/slide1.xml": fill_cover,
    "ppt/slides/slide4.xml": fill_understanding,
    "ppt/slides/slide6.xml": fill_requirements,
    "ppt/slides/slide7.xml": fill_landscape,
    "ppt/slides/slide8.xml": fill_process,
    "ppt/slides/slide9.xml": fill_benefits,
    "ppt/slides/slide14.xml": fill_timeline,
}

# Markers found by content scan (slide order is not fixed for added sections).
CONTENT_FILLERS = [("Budgetary Commercials", fill_commercials), ("ASSUMPTIONS_PLACEHOLDER", fill_assumptions)]


def assemble(intake_path, out_path):
    low = intake_path.lower()
    if low.endswith(".xlsx"):
        from ges_xlsx import xlsx_to_intake
        data = xlsx_to_intake(intake_path)
    elif low.endswith(".csv"):
        from ges_csv import csv_to_intake
        data = csv_to_intake(intake_path)
    else:
        data = json.loads(pathlib.Path(intake_path).read_text())
    zin = zipfile.ZipFile(TEMPLATE)
    entries = {n: zin.read(n) for n in zin.namelist()}
    for name, filler in SLIDE_FILLERS.items():
        entries[name] = filler(entries[name].decode("utf-8"), data).encode("utf-8")
    for name in list(entries):
        if re.match(r"ppt/slides/slide\d+\.xml$", name) and name not in SLIDE_FILLERS:
            xml = entries[name].decode("utf-8")
            updated = xml
            for marker, fn in CONTENT_FILLERS:
                if marker in updated:
                    updated = fn(updated, data)
            if updated != xml:
                entries[name] = updated.encode("utf-8")
    # global pass: replace any remaining marine client name on every slide
    for name in list(entries):
        if re.match(r"ppt/slides/slide\d+\.xml$", name):
            entries[name] = replace_client_name(entries[name].decode("utf-8"), data).encode("utf-8")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zout:
        for name, blob in entries.items():
            zout.writestr(name, blob)
    return out_path


def _default_out(intake_path):
    low = intake_path.lower()
    if low.endswith(".xlsx"):
        from ges_xlsx import xlsx_to_intake
        name = xlsx_to_intake(intake_path)["company"].get("name", "Client")
    elif low.endswith(".csv"):
        from ges_csv import csv_to_intake
        name = csv_to_intake(intake_path)["company"].get("name", "Client")
    else:
        name = json.loads(pathlib.Path(intake_path).read_text())["company"]["name"]
    return "Proposal %s v0.1.pptx" % name.replace("/", "-")


if __name__ == "__main__":
    intake = sys.argv[1]
    out = sys.argv[2] if len(sys.argv) > 2 else _default_out(intake)
    print("Wrote:", assemble(intake, out))
