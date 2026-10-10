# onenote pdf formatter

OneNote leaves a lot of padding around any PDF you insert, and it stays there when you export the page. This crops each page down to just the embedded printout, so you get a clean file with the same page size as the original document.

It adds a right click option called **Reformat OneNote PDF** to any `.pdf` file on Windows, Mac or Linux.

## how it works

When you insert a PDF into OneNote as a printout, OneNote stores it as one or more image objects at a fixed, predictable spot on the page, with whatever else is on that page (typed notes, margins) around it.

Instead of guessing margins or scanning pixel colours to find the content, the script reads the PDF's own metadata to get the exact bounding box of those images on each page. It then crops to that box and rescales the result to a standard page size (8.5" x 11" by default).

This works no matter

- how much handwriting or ink is on the page
- whether the PDF was inserted from Windows, Mac or iPad OneNote
- how much OneNote notes content sits above or around the printout
- whether one OneNote page holds several printout pages, or a printout page gets cut in two by OneNote's page break (each printout page is detected separately and the split ones are stitched back together)

## requirements

- Python 3
- [PyMuPDF](https://pypi.org/project/PyMuPDF/) (`pymupdf`)
- [context_menu](https://pypi.org/project/context-menu/)

## installation

1. Clone or download the repository.

2. Install the requirements and run the program.
```
pip install pymupdf context_menu
python make_context_menu.py
```

Now you can right click any `.pdf` file and pick **Reformat OneNote PDF**.

## usage

1. Export your annotated OneNote page(s) as a PDF (from my testing `Microsoft Print to PDF` gives the best quality).
2. Right click the exported PDF.
3. Pick **Reformat OneNote PDF**.
4. A new file called `<original_name>_formatted.pdf` shows up in the same folder.

You can also select a bunch of PDFs at once and it will do them all.

## uninstalling

Run `remove_context_menu.py` to remove the right click entry.

## configuration

The target page size is set at the top of `make_context_menu.py`.

```python
TARGET_WIDTH = 612   # 8.5in x 72
TARGET_HEIGHT = 792  # 11in x 72
```

Change it if your documents use a different page size (for A4 it's 595 x 842).

`MIN_DIM` is the smallest image size (in points) that counts as part of the printout. It's there to ignore small decorations like OneNote page icons and stickers so they don't end up in the crop.

## credits

Inspired by [Atlinx/OneNote-PDF-Cropper](https://github.com/Atlinx/OneNote-PDF-Cropper), which uses a fixed offset transform calibrated for PDFs inserted from **iPad** OneNote. This one takes a different approach so it works on PDFs inserted from **any platform**, Windows included.
