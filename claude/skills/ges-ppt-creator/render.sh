#!/bin/bash
# Render a pptx to per-slide PNGs via LibreOffice + poppler.
# Usage: render_pptx.sh "/path/file.pptx" [dpi]
set -e
SRC="$1"
DPI="${2:-110}"
OUT=/tmp/render
SOFFICE="/Applications/LibreOffice.app/Contents/MacOS/soffice"
rm -rf "$OUT" && mkdir -p "$OUT"
"$SOFFICE" --headless --convert-to pdf --outdir "$OUT" "$SRC" >/dev/null 2>&1
PDF=$(ls "$OUT"/*.pdf | head -1)
pdftoppm -png -r "$DPI" "$PDF" "$OUT/slide"
echo "Rendered to $OUT:"
ls "$OUT"/slide*.png | sed 's#.*/##'
