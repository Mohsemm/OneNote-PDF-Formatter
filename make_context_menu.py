import os
from context_menu import menus
import fitz  # pip install pymupdf

TARGET_WIDTH = 612   # 8.5in x 72
TARGET_HEIGHT = 792  # 11in x 72
MIN_DIM = 50          # ignore tiny decoration images (logos, stickers)
PAGE_ASPECT = TARGET_WIDTH / TARGET_HEIGHT  # ~0.773
PAGE_ASPECT_TOLERANCE = 0.03  # a strip within this of PAGE_ASPECT is one whole printout page
TILE_GAP = 3          # max vertical gap (pt) between tiles of the same printout page
EDGE_SLACK = 3        # how close (pt) a strip must be to the page edge to count as cut off

def get_printout_strips(page, min_dim=MIN_DIM, verbose=False):
    """Group the embedded OneNote 'printout' tiles on this page into strips.

    OneNote stores each inserted PDF page as several horizontal image tiles
    stacked on top of each other. A strip is a run of tiles that touch
    vertically, so one strip = one printout page (or the part of it that
    fits on this OneNote page, if OneNote's page break cut it in two)."""
    tiles = []
    for info in page.get_image_info(xrefs=True):
        b = fitz.Rect(info['bbox'])
        if b.width <= min_dim or b.height <= min_dim:
            continue
        tiles.append(b)

    if verbose:
        print(f"  page {page.number}: {len(tiles)} tile(s) above min_dim")

    tiles.sort(key=lambda r: (r.y0, r.x0))
    strips = []
    for t in tiles:
        last = strips[-1] if strips else None
        same_column = last is not None and abs(t.x0 - last.x0) < TILE_GAP and abs(t.x1 - last.x1) < TILE_GAP
        if same_column and t.y0 - last.y1 <= TILE_GAP:
            strips[-1] = last | t  # extend the current strip downwards
        elif last is not None and last.contains(t):
            continue  # duplicate tile left over from a manual move
        else:
            strips.append(fitz.Rect(t))

    if verbose:
        for s in strips:
            print(f"    strip={s} aspect={s.width/s.height:.3f}")
    return strips

def is_whole_page(rect):
    return abs(rect.width / rect.height - PAGE_ASPECT) < PAGE_ASPECT_TOLERANCE

def collect_printouts(src, verbose=False):
    """Return one list of (page_number, clip) pieces per printout page.

    A printout cut by a OneNote page break shows up as a strip touching the
    bottom of one page followed by a strip touching the top of the next;
    those two pieces are stitched back into a single printout."""
    strips_per_page = [get_printout_strips(page, verbose=verbose) for page in src]
    # OneNote's printable margin: the highest any printout starts on any page.
    margin = min((s.y0 for strips in strips_per_page for s in strips), default=0)

    printouts = []
    pending = None  # pieces of a printout that ran off the bottom of the previous page
    for page, strips in zip(src, strips_per_page):
        for i, s in enumerate(strips):
            starts_at_top = s.y0 <= margin + EDGE_SLACK
            if pending is not None and i == 0 and starts_at_top and not is_whole_page(s):
                # OneNote repeats a band of the printout at the top of the next
                # page after a page break. Trim it so the stitched printout has
                # the height of a real page instead of showing that band twice.
                prev = pending[-1][1]
                overlap = (prev.height + s.height) - s.width / PAGE_ASPECT
                if 0 < overlap < s.height:
                    s = fitz.Rect(s.x0, s.y0 + overlap, s.x1, s.y1)
                pending.append((page.number, s))
                printouts.append(pending)
                pending = None
                continue
            if pending is not None:
                printouts.append(pending)  # nothing continued it, keep what we have
                pending = None
            runs_off_bottom = s.y1 >= page.rect.height - margin - EDGE_SLACK
            if i == len(strips) - 1 and not is_whole_page(s) and runs_off_bottom:
                pending = [(page.number, s)]
            else:
                printouts.append([(page.number, s)])
    if pending is not None:
        printouts.append(pending)
    return printouts

def crop_onenote_pdf(input_path, verbose=True):
    src = fitz.open(input_path)
    out = fitz.open()
    printouts = collect_printouts(src, verbose=verbose)
    pages_with_printouts = {pn for pieces in printouts for pn, _ in pieces}
    skipped_pages = [p.number for p in src if p.number not in pages_with_printouts]
    for pieces in printouts:
        width = max(clip.width for _, clip in pieces)
        height = sum(clip.height for _, clip in pieces)
        # Scale to fit the target page without stretching, centred horizontally.
        scale = min(TARGET_WIDTH / width, TARGET_HEIGHT / height)
        x0 = (TARGET_WIDTH - width * scale) / 2
        y = 0
        new_page = out.new_page(width=TARGET_WIDTH, height=TARGET_HEIGHT)
        for page_number, clip in pieces:
            target = fitz.Rect(x0, y, x0 + clip.width * scale, y + clip.height * scale)
            new_page.show_pdf_page(target, src, page_number, clip=clip)
            y += clip.height * scale
        if verbose and len(pieces) > 1:
            print(f"  stitched printout from pages {[pn for pn, _ in pieces]}")
    if skipped_pages:
        print(f"WARNING: no printout image found on pages {skipped_pages} — these were skipped entirely")
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
