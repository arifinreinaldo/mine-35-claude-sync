---
name: dascom-a4-dot-matrix-escpos
description: Use when building ESC/POS print commands for DASCOM 1145 A4 dot-matrix printer over Bluetooth in a Flutter/Kotlin app — covers coordinate math, layout conventions, pagination, word-wrap, inline group headers, Kotlin data-class pattern, and the MainActivity dispatcher → helper pattern. Transfers across companies/solutions that use the same printer.
---

# DASCOM 1145 A4 Dot-Matrix ESC/POS — Playbook

Printer: **DASCOM 1145** dot matrix, 24cm wide, Bluetooth, 10 CPI monospace fixed-pitch. Protocol: **ESC/POS** via Dascom SDK (wrapped by `EscPosWrapper`).

## Hardware facts (invariant)

- **80 characters per line** at 10 CPI — every layout math assumes this
- **x-unit = 1/60 inch**, **y-unit = 1/180 inch** — `printText(data, x, y)` feeds `y` units vertically **then** prints starting at column `x`
- **6 x-units per character** — so column N of an 80-char line is at `x = N * 6`
- Line spacing constant in code: `LINE_SPACING` (use this, never hardcode y)
- No backspace/overstrike — position additively, left-to-right

## Core formulas

```kotlin
// Center a title of known length on an 80-char line
val titleX = ((80 - titleLen) / 2) * 6
escPos.printText("${boldFont}TITLE${boldOffFont}", titleX, LINE_SPACING * 2)

// Two-column header row: left label/value + right label/value at fixed column 43
val ADDR_LEFT_WIDTH = 43
escPos.printText(
    "Transaction No: $txnNo".padEnd(ADDR_LEFT_WIDTH) + "Doc Date : $docDate",
    0, LINE_SPACING
)
```

Bold ESC codes (define once at top of helper):
```kotlin
private val boldFont = "\u001BE"     // ESC E — bold on
private val boldOffFont = "\u001BF"  // ESC F — bold off
```

## Architecture: thin dispatcher + helper

**Don't stuff print logic into `MainActivity.kt`.** MainActivity parses the method call and delegates to a single helper class (e.g. `FnnPrintHelper`, `ScfPrintHelper`). One file per company/solution's printer suite.

```kotlin
// MainActivity.kt — slim block per command
"DASCOM_FNN_A4_VARIANT" -> {
    val btAddress = call.argument<String>("btAddress") ?: ""
    val headerJson = call.argument<String>("headerJson") ?: ""
    val detailJson = call.argument<String>("detailJson") ?: ""
    FnnPrintHelper(context).printVariant(btAddress, headerJson, detailJson, result)
}
```

Helper exposes one `fun printXxx(btAddress, headerJson, detailJson, result)` per document type. All share a common `connectAndPrint` that handles Bluetooth connect, `EscPosWrapper` construction, error paths (`PrinterConnectionTimeoutException`, generic `Exception`), and `finally { disconnect() }`.

## Data-class pattern (Kotlin + Gson)

Two classes per payload — source with `@SerializedName`, intermediate for print:

```kotlin
// Parsed directly from JSON — mirrors server field names
data class FooHdr(
    @SerializedName("TransactionNo") val transactionNo: String = "",
    @SerializedName("Date")          val date: String = "",
    @SerializedName("Amount")        val amount: Double = 0.0,
)

// Intermediate — all String, used only for rendering
data class FooHeaderPrint(
    val transactionNo: String = "",
    val date: String = "",
    val amount: String = "",
)
```

**Rules learned the hard way:**
- **Don't rename Kotlin variables** just to match JSON keys — keep ergonomic Kotlin names, let `@SerializedName` do the mapping.
- **Labels in the JSON (e.g. `"Datelbl"`) can be parsed but don't have to be used** — hardcoding labels in the layout is fine if the user prefers it, makes layout code readable.
- **Double fields:** use a lenient Gson instance (`safeDoubleGson`) that tolerates nulls/strings, then format with `String.format("%.2f", value)` inside the mapping, not in the layout.

## Detail parsing: word-wrap vs chunked

```kotlin
// Break at whitespace, fall back to hard split for over-long single words.
fun wordWrap(text: String, maxLen: Int): List<String> {
    val words = text.split(" ")
    val lines = mutableListOf<String>()
    var current = StringBuilder()
    for (w in words) {
        if (w.length > maxLen) {                       // single word too long
            if (current.isNotEmpty()) { lines.add(current.toString()); current = StringBuilder() }
            w.chunked(maxLen).forEach { lines.add(it) }
            continue
        }
        val proposed = if (current.isEmpty()) w else "$current $w"
        if (proposed.length > maxLen) { lines.add(current.toString()); current = StringBuilder(w) }
        else current = StringBuilder(proposed)
    }
    if (current.isNotEmpty()) lines.add(current.toString())
    return lines
}
```

- **Use `wordWrap`** for human-readable text: descriptions, customer names, addresses.
- **Use `.chunked(n)`** for ID codes / part numbers — no spaces, breaking anywhere is fine.

## Atomic pagination

Multi-line items must NOT split across pages. Structure: `List<List<String>>` (list of line-groups). Group = one logical item (1-N lines).

```kotlin
val allLineGroups = mutableListOf<List<String>>()
for (dtl in details) {
    val lines = /* build 1..N lines for this detail */
    allLineGroups.add(lines)
}

val pages = mutableListOf<List<String>>()
var currentPage = mutableListOf<String>()
var linesOnPage = 0
for (group in allLineGroups) {
    if (linesOnPage + group.size > itemPerPage && linesOnPage > 0) {
        pages.add(currentPage); currentPage = mutableListOf(); linesOnPage = 0
    }
    currentPage.addAll(group); linesOnPage += group.size
}
if (currentPage.isNotEmpty()) pages.add(currentPage)
val totalPages = pages.size.coerceAtLeast(1)
```

Typical `itemPerPage`: 25–40 depending on header+footer height. Start with 30 and adjust after test print.

## Inline group headers

Detail records where a delimiter field (commonly `hypen`) is empty are **group labels**, not items ("BAD QUANTITY", "GOOD", "EXCHANGE", "RETURN"). Detect and render inline — don't pre-group/sort unless the user asks.

```kotlin
for (dtl in details) {
    if (dtl.hypen.isEmpty()) {
        allLineGroups.add(listOf(dtl.item.padEnd(50)))   // group header line
    } else {
        // normal item line(s)
    }
}
```

## Per-page skeleton

```kotlin
connectAndPrint(btAddress, result, "DASCOM_XXX") { escPos ->
    pages.forEachIndexed { pageIndex, pageLines ->
        // Page header
        escPos.feedLines(3.0)
        escPos.printText("${boldFont}TITLE${boldOffFont}", titleX, LINE_SPACING * 2)
        escPos.printText("".padEnd(ADDR_LEFT_WIDTH) + "Page No :${pageIndex + 1} of $totalPages", 0, LINE_SPACING)
        // ...more header lines...

        // Column header + separator
        escPos.printText(SEPARATOR, 0, LINE_SPACING)
        escPos.printText(colHeader, 0, LINE_SPACING)
        escPos.printText(SEPARATOR, 0, LINE_SPACING / 2)

        // Detail lines
        pageLines.forEach { escPos.printText(it, 0, LINE_SPACING) }

        // Non-last pages: pad blanks to keep footer position stable, print "Continued..."
        if (pageIndex < pages.size - 1) {
            val blanks = itemPerPage - pageLines.size
            if (blanks > 0) escPos.feedLines(blanks.toDouble())
            escPos.printText(SEPARATOR, 0, LINE_SPACING)
            escPos.printText("Continued . . . . . . . . . . . . . .", 0, LINE_SPACING)
        }

        // Last page: footer (totals, signatures, timestamp)
        if (pageIndex == pages.size - 1) {
            escPos.printText(SEPARATOR, 0, LINE_SPACING)
            // signatures, temperature, totals, etc.
            escPos.printText("Print Date/Time : ${formatTimestamp()}".padStart(80), 0, LINE_SPACING)
        }

        escPos.doPrintNewPage()
    }
}
```

## Timestamp footer

Use device local time via `formatTimestamp()` (wraps `SimpleDateFormat`) — **do not** use the server-supplied `printedOn` string; it may drift from the device clock the operator trusts.

## When adding a new command — checklist

1. Create `FooHdr.kt` + `FooDtl.kt` under `domain/<solution>/` — two data classes each (source + `*Print`).
2. Add `fun printFoo(...)` in the solution's `*PrintHelper.kt`.
3. Add the `MainActivity.kt` dispatch block — pass-through only, no logic.
4. Layout pass — column widths sum to 80, separators, title centered, page-number at column 43.
5. Test with ≥3 pages of detail to validate pagination and "Continued" footer.
6. Test a detail with a description long enough to wrap — confirm no word splits.
7. Test with an inline group header if applicable.

## What typically breaks

- **Off-by-one column math** — forgetting `padEnd` trims nothing when string is already ≥ width. Always build a string then verify `line.length == 80` in a debug log before trusting the layout.
- **Wrong `x` base unit** — `x` is in 1/60-inch units, NOT characters. `x = 43` puts you at column ~7, not column 43. Use `x = 43 * 6` or `ADDR_LEFT_WIDTH * 6`.
- **Bold leaking across lines** — always pair `boldFont` with `boldOffFont` in the same `printText` call.
- **Gson NumberFormatException** on Doubles — use a lenient Gson (`safeDoubleGson`) instance for headers with numeric fields.
- **Last page padded with blank lines** — the pad-to-itemPerPage should apply only when `pageIndex < pages.size - 1`.
- **Stale build showing old @SerializedName** — if a field refuses to appear after a rename, do a `flutter clean` + rebuild before debugging the mapping.

## Cross-company reuse

This playbook transfers to any company using the same DASCOM 1145. What changes per company:
- Header/detail field names and JSON keys
- Column header strings and widths
- Title string
- Footer contents (signatures, totals, disclaimers, temperature, etc.)
- `itemPerPage` (tune after first test print)

What stays the same: all the formulas, patterns, and architecture above.
