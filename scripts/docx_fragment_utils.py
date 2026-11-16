"""
docx_fragment_utils.py

Shared low-level helpers for "fragment cloning" DOCX generation.

Core idea: instead of manually rebuilding paragraph/run formatting from
scratch (which loses template-specific XML like right-tab stops, bottom
borders on headings, numPr bullets, and hyperlinks), we deep-copy a real
paragraph element from the template ("shape") and only swap out the text
in its runs. This guarantees generated content is pixel-identical in
formatting to the template it came from.
"""

from copy import deepcopy
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from docx.opc.constants import RELATIONSHIP_TYPE as RT


def get_pPr(p_element):
    """Get the <w:pPr> element of a paragraph element, or None."""
    return p_element.find(qn('w:pPr'))


def get_first_run_element(p_element):
    """Get the first <w:r> direct child of a paragraph element (ignoring hyperlinks)."""
    return p_element.find(qn('w:r'))


def clone_paragraph_shape(template_para):
    """Deep-copy a paragraph's XML element (detached, not attached to any document)."""
    return deepcopy(template_para._element)


def add_shaped_paragraph(doc, shape_element):
    """
    Add a new empty paragraph to `doc` (correctly positioned before sectPr
    via python-docx's own add_paragraph), then copy the shape's <w:pPr>
    (spacing, borders, tab stops, alignment, style) onto it.

    Returns the python-docx Paragraph object.
    """
    new_para = doc.add_paragraph()

    shape_pPr = get_pPr(shape_element)
    existing_pPr = new_para._p.find(qn('w:pPr'))
    if existing_pPr is not None:
        new_para._p.remove(existing_pPr)
    if shape_pPr is not None:
        new_para._p.insert(0, deepcopy(shape_pPr))

    return new_para


def get_run_mold(shape_element, run_index=0):
    """
    Get a deep-copied <w:r> element from a shape to use as a formatting
    "mold" for constructing new runs (preserves rFonts/sz/color/etc).

    run_index selects which run in the shape to use as the mold (e.g. a
    job-line shape has run 0 = bold company/location, run 1 = italic title,
    run 2 = plain tabbed date).
    """
    runs = shape_element.findall(qn('w:r'))
    if run_index >= len(runs):
        run_index = 0
    if not runs:
        return None
    return deepcopy(runs[run_index])


def _set_toggle_prop(rpr, tag, enabled):
    """Add or remove a boolean toggle property (e.g. <w:b/>, <w:i/>) on rPr."""
    existing = rpr.find(qn(tag))
    if enabled and existing is None:
        el = OxmlElement(tag)
        rpr.append(el)
    elif not enabled and existing is not None:
        rpr.remove(existing)


def append_run(paragraph, run_mold, text, bold=None, italic=None):
    """
    Append a new run to `paragraph`, cloned from `run_mold` (preserving
    font/size/color), with `text` and optional bold/italic overrides.

    bold/italic: True to force on, False to force off, None to leave as
    the mold already has it.
    """
    run_elm = deepcopy(run_mold)

    rpr = run_elm.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        run_elm.insert(0, rpr)

    if bold is not None:
        _set_toggle_prop(rpr, 'w:b', bold)
        _set_toggle_prop(rpr, 'w:bCs', bold)
    if italic is not None:
        _set_toggle_prop(rpr, 'w:i', italic)
        _set_toggle_prop(rpr, 'w:iCs', italic)

    t = run_elm.find(qn('w:t'))
    if t is None:
        t = OxmlElement('w:t')
        run_elm.append(t)
    t.text = text
    t.set(qn('xml:space'), 'preserve')

    # Drop any stray <w:tab/> already in the mold; callers add tabs explicitly
    for tab in run_elm.findall(qn('w:tab')):
        run_elm.remove(tab)

    paragraph._p.append(run_elm)
    return run_elm


def append_tab_run(paragraph, run_mold, text_after_tab, bold=None, italic=None):
    """Append a run that starts with a literal tab character, then text."""
    run_elm = deepcopy(run_mold)

    rpr = run_elm.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        run_elm.insert(0, rpr)

    if bold is not None:
        _set_toggle_prop(rpr, 'w:b', bold)
        _set_toggle_prop(rpr, 'w:bCs', bold)
    if italic is not None:
        _set_toggle_prop(rpr, 'w:i', italic)
        _set_toggle_prop(rpr, 'w:iCs', italic)

    # Remove existing <w:t> / <w:tab> in mold, rebuild content: tab then text
    for t in run_elm.findall(qn('w:t')):
        run_elm.remove(t)
    for tab in run_elm.findall(qn('w:tab')):
        run_elm.remove(tab)

    tab_el = OxmlElement('w:tab')
    run_elm.append(tab_el)

    t = OxmlElement('w:t')
    t.text = text_after_tab
    t.set(qn('xml:space'), 'preserve')
    run_elm.append(t)

    paragraph._p.append(run_elm)
    return run_elm


def add_hyperlink_run(doc, paragraph, run_mold, text, url, color="0563C1", underline=True):
    """
    Append a real <w:hyperlink> run to `paragraph`, using `run_mold` for
    base font formatting, colored/underlined like a standard hyperlink.
    """
    part = doc.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)

    hyperlink = OxmlElement('w:hyperlink')
    hyperlink.set(qn('r:id'), r_id)

    run_elm = deepcopy(run_mold)
    rpr = run_elm.find(qn('w:rPr'))
    if rpr is None:
        rpr = OxmlElement('w:rPr')
        run_elm.insert(0, rpr)

    # Clear bold/italic inherited from mold (hyperlinks in this template are plain+colored)
    _set_toggle_prop(rpr, 'w:b', False)
    _set_toggle_prop(rpr, 'w:i', False)

    color_el = rpr.find(qn('w:color'))
    if color_el is None:
        color_el = OxmlElement('w:color')
        rpr.append(color_el)
    color_el.set(qn('w:val'), color)

    if underline:
        u_el = rpr.find(qn('w:u'))
        if u_el is None:
            u_el = OxmlElement('w:u')
            rpr.append(u_el)
        u_el.set(qn('w:val'), 'single')

    t = run_elm.find(qn('w:t'))
    if t is None:
        t = OxmlElement('w:t')
        run_elm.append(t)
    t.text = text
    t.set(qn('xml:space'), 'preserve')

    hyperlink.append(run_elm)
    paragraph._p.append(hyperlink)
    return hyperlink


def set_single_run_text(paragraph, text):
    """
    Replace the text of a paragraph that has exactly one (or more) runs,
    collapsing to a single run with the given text while preserving the
    first run's formatting. Used for in-place edits of static paragraphs
    (e.g. the date line) where we don't want to touch anything else.
    """
    runs = paragraph._p.findall(qn('w:r'))
    if not runs:
        return
    first = runs[0]
    t = first.find(qn('w:t'))
    if t is None:
        t = OxmlElement('w:t')
        first.append(t)
    t.text = text
    t.set(qn('xml:space'), 'preserve')
    # Remove any additional runs so text isn't duplicated/appended
    for extra in runs[1:]:
        paragraph._p.remove(extra)


def parse_inline_markdown(text):
    """
    Parse simple inline **bold** / *italic* markdown into a list of
    (text, bold, italic) segments. Non-greedy, no nesting support beyond
    one level (sufficient for resume/cover-letter bullet content).
    """
    segments = []
    current = ""
    bold = False
    italic = False
    i = 0
    while i < len(text):
        if i < len(text) - 1 and text[i:i + 2] == '**':
            if current:
                segments.append((current, bold, italic))
                current = ""
            bold = not bold
            i += 2
        elif text[i] == '*' and (i == 0 or text[i - 1] != '*') and (i == len(text) - 1 or text[i + 1] != '*'):
            if current:
                segments.append((current, bold, italic))
                current = ""
            italic = not italic
            i += 1
        else:
            current += text[i]
            i += 1
    if current:
        segments.append((current, bold, italic))
    return segments
