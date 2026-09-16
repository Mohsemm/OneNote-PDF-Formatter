import os
from context_menu import menus
import fitz  # pip install pymupdf

TARGET_WIDTH = 612   # 8.5in x 72
TARGET_HEIGHT = 792  # 11in x 72
MIN_DIM = 50          # skips tiny images like logos and stickers
PAGE_ASPECT = TARGET_WIDTH / TARGET_HEIGHT  # ~0.773
ASPECT_TOLERANCE = 0.25  # how far the aspect ratio can drift from a page

def get_printout_bbox(page, min_dim=MIN_DIM, verbose=False):
    """bounding box of the printout images on a page, skips small decorations and stray images"""
    candidates = []
    for info in page.get_image_info(xrefs=True):
        b = info['bbox']
        w, h = b[2] - b[0], b[3] - b[1]
        if w <= min_dim or h <= min_dim:
            continue
        aspect = w / h
        candidates.append((b, w, h, aspect))

    if verbose:
        print(f"  page {page.number}: {len(candidates)} image(s) above min_dim")
        for b, w, h, aspect in candidates:
            print(f"    bbox={b} size=({w:.1f},{h:.1f}) aspect={aspect:.3f}")

    if not candidates:
        return None

    # keep only page shaped images so a stray one doesn't skew the box
    filtered = [c for c in candidates if abs(c[3] - PAGE_ASPECT) < ASPECT_TOLERANCE]
    used = filtered if filtered else candidates  # fall back if filter kills everything

    if verbose and len(used) != len(candidates):
        print(f"    -> aspect filter dropped {len(candidates) - len(used)} image(s)")

    x0 = min(b[0] for b, *_ in used)
    y0 = min(b[1] for b, *_ in used)
    x1 = max(b[2] for b, *_ in used)
    y1 = max(b[3] for b, *_ in used)
    rect = fitz.Rect(x0, y0, x1, y1)

    if verbose:
        print(f"    -> final union bbox={rect} aspect={rect.width/rect.height:.3f}")

    return rect

def crop_onenote_pdf(input_path, verbose=True):
    src = fitz.open(input_path)
    out = fitz.open()
    skipped_pages = []
    for page in src:
        rect = get_printout_bbox(page, verbose=verbose)
        if rect is None:
            skipped_pages.append(page.number)
            continue
        new_page = out.new_page(width=TARGET_WIDTH, height=TARGET_HEIGHT)
        new_page.show_pdf_page(new_page.rect, src, page.number, clip=rect)
    if skipped_pages:
        print(f"warning, no printout image found on pages {skipped_pages}, skipped them")
    output_path = f"{os.path.splitext(input_path)[0]}_formatted.pdf"
    out.save(output_path)
    return output_path

def exec_menu_command(file_names, params):
    for file_name in file_names:
        if file_name.endswith('.pdf'):
            print(f'processing {file_name}')
            output_path = crop_onenote_pdf(file_name)
            print(f'saved {output_path}')

if __name__ == '__main__':
    fc = menus.FastCommand('Reformat OneNote PDF', type='FILES', python=exec_menu_command)
    fc.compile()