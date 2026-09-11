# OneNote PDF Formatter (Metadata-Based)

Crops PDFs exported from OneNote down to just the embedded printout content, removing the page padding/whitespace OneNote adds by default around inserted PDFs, so you get a clean file matching the original document's page size.

Adds a right-click context menu option (**Reformat OneNote PDF**) for any `.pdf` file on Windows, Mac, or Linux.

## How it works

When you insert a PDF into OneNote as a printout, OneNote embeds it as one or more image objects on the page at a fixed, predictable location, surrounded by whatever native OneNote content (typed notes, page margins) happens to be on that page.

Instead of guessing margins or scanning pixel colors to find the content, this script reads the PDF's own internal metadata to find the exact bounding box of those embedded images on each page, then crops to that box and rescales the result to a standard page size (default: 8.5" x 11").

This means it works reliably regardless of:
- How much handwritten annotation or ink is on the page
- Whether the PDF was inserted from Windows, Mac, or iPad OneNote
- How much OneNote notes content sits above/around the printout

## Requirements

- Python 3
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`pymupdf`)
- [context_menu](https://pypi.org/project/context-menu/)

## Installation


1. Clone/download the repository

2. Download requirement(s) and run the program:
```
pip install pymupdf context_menu
python make_context_menu.py
```

You should now be able to right-click any `.pdf` file and select **Reformat OneNote PDF**.

## Usage

1. Export your annotated OneNote page(s) as PDF (from my testing, `Microsoft Print to PDF` gives the best quality).
2. Right-click the exported PDF file.
3. Select **Reformat OneNote PDF**.
4. A new file, `<original_name>_formatted.pdf`, appears in the same folder.

You can also select multiple PDF files at once to batch-process them.

## Uninstalling

Run `remove_context_menu.py` to remove the right-click menu entry.

## Configuration

Target page size is set at the top of `make_context_menu.py`:

```python
TARGET_WIDTH = 612   # 8.5in x 72
TARGET_HEIGHT = 792  # 11in x 72
```

Adjust if your original documents use a different page size (e.g. A4: 595 x 842).

`MIN_DIM` controls the minimum image size (in points) considered part of the printout, used to filter out small decorative images (like OneNote page icons/stickers) that shouldn't be included in the crop.

## Credits

Inspired by [Atlinx/OneNote-PDF-Cropper](https://github.com/Atlinx/OneNote-PDF-Cropper) which uses a fixed-offset transform calibrated for PDFs inserted via **iPad**
 OneNote. This project takes a different approach that allows it to work on  PDFs inserted from **any platform**, including Windows.