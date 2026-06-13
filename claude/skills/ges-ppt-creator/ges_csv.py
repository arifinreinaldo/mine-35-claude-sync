#!/usr/bin/env python3
"""CSV <-> intake converter for ges-ppt-creator.

A single, Excel-friendly long-format CSV captures the whole intake. Columns:
    section, field1, field2, field3, field4
Rows whose `section` is empty, starts with '#', or equals 'section' are ignored
(headers / comments). Section meanings:

    company            field1=key (name/industry/size/current_system/date), field2=value
    understanding      field1=key (profile/current_system), field2=value
    challenge          field1=category, field2=item            (one row per item)
    process            field1=stage title, field2=step          (one row per step)
    process_note       field1=key (loop_note/reporting_note), field2=value
    benefit            field1=text
    methodology        field1=key (start_month/months), field2=value
    methodology_stage  field1=stage name
    scope              field1=module, field2=solution, field3=type, field4=scope_function
    commercial_meta    field1=key (currency/terms), field2=value
    commercial         field1=item, field2=qty, field3=unit_price
    assumption         field1=text

Usage:
    python3 ges_csv.py blank                 # print a blank fill-in template
    python3 ges_csv.py fromjson intake.json  # print a (pre-filled) CSV from an intake
    python3 ges_csv.py tojson filled.csv out.json
"""
import sys, json, csv, io


def _num(s):
    s = (s or "").replace(",", "").replace(".", "").replace(" ", "").strip()
    return int(s) if s.lstrip("-").isdigit() else 0


def csv_to_intake(path):
    with open(path, encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.reader(fh))
    intake = {"company": {}, "understanding": {"challenges": []}, "process": {"stages": []},
              "benefits": [], "methodology": {"stages": []}, "scope": [],
              "commercials": {"line_items": []}, "assumptions": []}
    ch_order, ch_map, st_order, st_map = [], {}, [], {}
    for r in rows:
        if not r or not r[0].strip() or r[0].strip().startswith("#") or r[0].strip() == "section":
            continue
        sec = r[0].strip()
        f = [(r[i].strip() if i < len(r) else "") for i in range(1, 5)]
        if sec == "company":
            intake["company"][f[0]] = f[1]
        elif sec == "understanding":
            intake["understanding"][f[0]] = f[1]
        elif sec == "challenge":
            if f[0] not in ch_map:
                ch_map[f[0]] = {"category": f[0], "items": []}; ch_order.append(f[0])
            if f[1]:
                ch_map[f[0]]["items"].append(f[1])
        elif sec == "process":
            if f[0] not in st_map:
                st_map[f[0]] = {"title": f[0], "steps": []}; st_order.append(f[0])
            if f[1]:
                st_map[f[0]]["steps"].append(f[1])
        elif sec == "process_note":
            intake["process"][f[0]] = f[1]
        elif sec == "benefit":
            if f[0]:
                intake["benefits"].append(f[0])
        elif sec == "methodology":
            intake["methodology"][f[0]] = _num(f[1]) if f[0] == "months" else f[1]
        elif sec == "methodology_stage":
            if f[0]:
                intake["methodology"]["stages"].append(f[0])
        elif sec == "scope":
            if f[0]:
                intake["scope"].append({"module": f[0], "solution": f[1], "type": f[2], "scope_function": f[3]})
        elif sec == "commercial_meta":
            intake["commercials"][f[0]] = f[1]
        elif sec == "commercial":
            if f[0]:
                intake["commercials"]["line_items"].append({"item": f[0], "qty": _num(f[1]) or 1, "unit_price": _num(f[2])})
        elif sec == "assumption":
            if f[0]:
                intake["assumptions"].append(f[0])
    intake["understanding"]["challenges"] = [ch_map[c] for c in ch_order]
    intake["process"]["stages"] = [st_map[t] for t in st_order]
    return intake


def intake_to_csv(intake, blank_prices=False):
    out = io.StringIO()
    w = csv.writer(out)
    w.writerow(["section", "field1", "field2", "field3", "field4"])
    cmt = lambda c: w.writerow(["# " + c, "", "", "", ""])
    cmt("COMPANY  (field1=key, field2=value)")
    for k in ("name", "industry", "size", "current_system", "date"):
        w.writerow(["company", k, intake.get("company", {}).get(k, ""), "", ""])
    cmt("UNDERSTANDING")
    u = intake.get("understanding", {})
    w.writerow(["understanding", "profile", u.get("profile", ""), "", ""])
    w.writerow(["understanding", "current_system", u.get("current_system", ""), "", ""])
    cmt("CHALLENGES  (field1=category, field2=item) — one row per item")
    for ch in u.get("challenges", []):
        for it in ch["items"]:
            w.writerow(["challenge", ch["category"], it, "", ""])
    cmt("PROCESS  (field1=stage, field2=step) — one row per step")
    for st in intake.get("process", {}).get("stages", []):
        for step in st["steps"]:
            w.writerow(["process", st["title"], step, "", ""])
    cmt("PROCESS NOTES")
    w.writerow(["process_note", "loop_note", intake.get("process", {}).get("loop_note", ""), "", ""])
    w.writerow(["process_note", "reporting_note", intake.get("process", {}).get("reporting_note", ""), "", ""])
    cmt("BENEFITS  (field1=text)")
    for b in intake.get("benefits", []):
        w.writerow(["benefit", b, "", "", ""])
    cmt("METHODOLOGY")
    m = intake.get("methodology", {})
    w.writerow(["methodology", "start_month", m.get("start_month", ""), "", ""])
    w.writerow(["methodology", "months", m.get("months", ""), "", ""])
    for s in m.get("stages", []):
        w.writerow(["methodology_stage", s, "", "", ""])
    cmt("SCOPE  (field1=module, field2=solution, field3=type [Standard | Enhancement | Standard, Enhancement], field4=scope function)")
    for s in intake.get("scope", []):
        w.writerow(["scope", s["module"], s.get("solution", ""), s.get("type", ""), s.get("scope_function", "")])
    cmt("COMMERCIALS — currency + terms")
    c = intake.get("commercials", {})
    w.writerow(["commercial_meta", "currency", c.get("currency", ""), "", ""])
    w.writerow(["commercial_meta", "terms", c.get("terms", ""), "", ""])
    cmt("COMMERCIAL LINE ITEMS  (field1=item, field2=qty, field3=unit_price)")
    for li in c.get("line_items", []):
        price = "" if (blank_prices or not li.get("unit_price")) else li["unit_price"]
        w.writerow(["commercial", li["item"], li.get("qty", 1), price, ""])
    cmt("ASSUMPTIONS  (field1=text)")
    for a in intake.get("assumptions", []):
        w.writerow(["assumption", a, "", "", ""])
    return out.getvalue()


_BLANK = {
    "company": {k: "" for k in ("name", "industry", "size", "current_system", "date")},
    "understanding": {"profile": "", "current_system": "",
                      "challenges": [{"category": "Challenge Category %d" % i, "items": ["", "", ""]} for i in (1, 2, 3)]},
    "process": {"loop_note": "", "reporting_note": "",
                "stages": [{"title": "%d. Stage" % i, "steps": ["", "", "", ""]} for i in (1, 2, 3, 4)]},
    "benefits": [""] * 8,
    "methodology": {"start_month": "", "months": 6,
                    "stages": ["Impact Analysis", "Functional Design", "Customization", "Implementation", "Training", "Go-live"]},
    "scope": [{"module": "", "solution": "", "type": "", "scope_function": ""} for _ in range(6)],
    "commercials": {"currency": "IDR", "terms": "",
                    "line_items": [{"item": n, "qty": q, "unit_price": 0} for n, q in
                                   (("1C:Drive named-user licenses", 10), ("Implementation services", 1),
                                    ("Custom enhancements", 1), ("Annual support & maintenance (Year 1)", 1))]},
    "assumptions": [""] * 6,
}


def blank_template_csv():
    return intake_to_csv(_BLANK, blank_prices=True)


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "blank"
    if cmd == "blank":
        sys.stdout.write(blank_template_csv())
    elif cmd == "fromjson":
        sys.stdout.write(intake_to_csv(json.load(open(sys.argv[2])), blank_prices="--blank-prices" in sys.argv))
    elif cmd == "tojson":
        json.dump(csv_to_intake(sys.argv[2]), open(sys.argv[3], "w"), indent=2, ensure_ascii=False)
        print("wrote", sys.argv[3])
