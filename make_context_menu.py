import os
from context_menu import menus
import fitz  # pip install pymupdf

TARGET_WIDTH = 612   # 8.5in x 72
TARGET_HEIGHT = 792  # 11in x 72
MIN_DIM = 50          # ignore tiny decoration images (logos, stickers)

def get_printout_bbox(page, min_dim=MIN_DIM):
    """Find the bounding box of the embedded OneNote 'printout' image(s)
    on this page, ignoring small decorative images."""
    boxes = []
    for info in page.get_image_info(xrefs=True):
        b = info['bbox']
        w, h = b[2] - b[0], b[3] - b[1]
        if w > min_dim and h > min_dim:
            boxes.append(b)
    if not boxes:
        return None
    x0 = min(b[0] for b in boxes)
    y0 = min(b[1] for b in boxes)
    x1 = max(b[2] for b in boxes)
    y1 = max(b[3] for b in boxes)
    return fitz.Rect(x0, y0, x1, y1)

def crop_onenote_pdf(input_path):
    src = fitz.open(input_path)
    out = fitz.open()
    for page in src:
        rect = get_printout_bbox(page)
        if rect is None:
            continue
        new_page = out.new_page(width=TARGET_WIDTH, height=TARGET_HEIGHT)
        new_page.show_pdf_page(new_page.rect, src, page.number, clip=rect)
    output_path = f"{os.path.splitext(input_path)[0]}_formatted.pdf"
    out.save(output_path)
    return output_path

def exec_menu_command(file_names, params):
    for file_name in file_names:
        if file_name.endswith('.pdf'):
            print(f'Processing: {file_name}')
            output_path = crop_onenote_pdf(file_name)
            print(f'Saved: {output_path}')

if __name__ == '__main__':
    fc = menus.FastCommand('Reformat OneNote PDF', type='FILES', python=exec_menu_command)
    fc.compile()