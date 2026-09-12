from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_shading(cell, fill):
    """Set background colour of a table cell."""
    tc_pr = cell._tc.get_or_add_tcPr()

    shd = tc_pr.find(qn("w:shd"))

    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)

    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=80, start=80, bottom=80, end=80):
    """Set cell margins."""
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()

    tc_mar = tc_pr.first_child_found_in("w:tcMar")

    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)

    for margin, value in [
        ("top", top),
        ("start", start),
        ("bottom", bottom),
        ("end", end),
    ]:
        node = tc_mar.find(qn(f"w:{margin}"))

        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)

        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_cell_text(
    cell,
    text,
    bold=False,
    italic=False,
    size=10,
    alignment=WD_ALIGN_PARAGRAPH.LEFT
):
    """Clear a cell and add formatted text."""
    cell.text = ""

    paragraph = cell.paragraphs[0]
    paragraph.alignment = alignment

    run = paragraph.add_run(str(text))
    run.bold = bold
    run.italic = italic
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)

    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    set_cell_margins(cell)


def set_column_width(cell, width_inches):
    """Set cell width."""
    cell.width = Inches(width_inches)

    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))

    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)

    tc_w.set(qn("w:w"), str(int(width_inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def set_table_borders(table, color="000000", size="8"):
    """Set visible borders around a table."""
    tbl = table._tbl
    tbl_pr = tbl.tblPr

    borders = tbl_pr.first_child_found_in("w:tblBorders")

    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)

    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))

        if element is None:
            element = OxmlElement(tag)
            borders.append(element)

        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_repeat_table_header(row):
    """Repeat table header on additional pages if necessary."""
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def create_mom_document(
    meeting_title,
    participants,
    meeting_date,
    location,
    mom,
    photo_path=None,
    branding_path=None,
    branding_type=None
):
    """
    Generate the Minutes of Meeting document.

    branding_path and branding_type are intentionally ignored.
    The uploaded template is used only for formatting/layout,
    not for copying institutional branding or logos.
    """

    document = Document()

    # ---------------------------------------------------------
    # PAGE SETUP
    # ---------------------------------------------------------

    section = document.sections[0]

    section.top_margin = Inches(0.45)
    section.bottom_margin = Inches(0.45)
    section.left_margin = Inches(0.55)
    section.right_margin = Inches(0.55)

    section.header_distance = Inches(0.2)
    section.footer_distance = Inches(0.2)

    # Default font
    styles = document.styles

    styles["Normal"].font.name = "Times New Roman"
    styles["Normal"].font.size = Pt(10)

    # ---------------------------------------------------------
    # TOP HEADER
    # ---------------------------------------------------------

    header_table = document.add_table(rows=2, cols=1)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    header_table.autofit = False

    set_table_borders(header_table, size="8")

    # Reference number
    cell = header_table.cell(0, 0)
    set_cell_text(
        cell,
        "AISAT/Form/QPM15/F2",
        bold=False,
        size=9,
        alignment=WD_ALIGN_PARAGRAPH.CENTER
    )

    # Meeting Minutes title
    cell = header_table.cell(1, 0)
    set_cell_text(
        cell,
        "Meeting Minutes",
        bold=True,
        size=12,
        alignment=WD_ALIGN_PARAGRAPH.CENTER
    )

    for row in header_table.rows:
        for cell in row.cells:
            set_column_width(cell, 7.2)

    document.add_paragraph().paragraph_format.space_after = Pt(3)

    # ---------------------------------------------------------
    # MEETING DETAILS
    # ---------------------------------------------------------

    details_table = document.add_table(rows=5, cols=4)
    details_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    details_table.autofit = False

    set_table_borders(details_table, size="8")

    details = [
        (
            "Type",
            "Meeting",
            "Meeting No",
            "Not specified"
        ),
        (
            "Date",
            str(meeting_date) if meeting_date else "Not specified",
            "Venue",
            location if location else "Not specified"
        ),
        (
            "Time",
            "Not specified",
            "Mode",
            "Not specified"
        ),
        (
            "Attendees",
            participants if participants else "Not specified",
            "",
            ""
        ),
        (
            "Absentees",
            "Not specified",
            "",
            ""
        ),
    ]

    for row_index, row_data in enumerate(details):

        if row_index < 3:

            for col_index, value in enumerate(row_data):
                cell = details_table.cell(row_index, col_index)

                is_label = col_index in (0, 2)

                set_cell_text(
                    cell,
                    value,
                    bold=is_label,
                    size=9
                )

        else:

            label = row_data[0]
            value = row_data[1]

            details_table.cell(row_index, 0).merge(
                details_table.cell(row_index, 0)
            )

            merged_value_cell = details_table.cell(row_index, 1).merge(
                details_table.cell(row_index, 3)
            )

            set_cell_text(
                details_table.cell(row_index, 0),
                label,
                bold=True,
                size=9
            )

            set_cell_text(
                merged_value_cell,
                value,
                size=9
            )

    # Column widths
    widths = [1.0, 3.2, 1.25, 1.75]

    for row in details_table.rows:
        for i, width in enumerate(widths):
            if i < len(row.cells):
                set_column_width(row.cells[i], width)

    document.add_paragraph().paragraph_format.space_after = Pt(3)

    # ---------------------------------------------------------
    # MAIN MINUTES TABLE
    # ---------------------------------------------------------

    discussion_points = mom.get("discussion_points", [])
    decisions = mom.get("decisions", [])
    action_items = mom.get("action_items", [])
    agenda = mom.get("agenda", "Not specified")

    # Build rows dynamically while preserving all existing content.
    rows = []

    # Agenda
    rows.append(
        (
            "",
            "Agenda",
            agenda if agenda else "Not specified",
            True,
            False
        )
    )

    # Discussion points
    for point in discussion_points:
        rows.append(
            (
                "",
                "Discussion",
                point,
                False,
                False
            )
        )

    # Decisions
    for decision in decisions:
        rows.append(
            (
                "",
                "Decision",
                decision,
                False,
                False
            )
        )

    # Action items
    for action in action_items:
        responsible = action.get(
            "responsible",
            "Not specified"
        )

        task = action.get(
            "task",
            "Not specified"
        )

        action_text = f"{task} — Responsibility: {responsible}"

        rows.append(
            (
                "",
                "Action Item",
                action_text,
                False,
                False
            )
        )

    # If nothing was generated, keep a useful row.
    if len(rows) == 0:
        rows.append(
            (
                "",
                "Agenda",
                "Not specified",
                True,
                False
            )
        )

    main_table = document.add_table(
        rows=len(rows) + 1,
        cols=3
    )

    main_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    main_table.autofit = False

    set_table_borders(main_table, size="8")

    # Header
    headers = [
        "Sl.\nNo",
        "Agenda Item",
        "Discussions and Decisions"
    ]

    for i, header in enumerate(headers):
        cell = main_table.cell(0, i)

        set_cell_text(
            cell,
            header,
            bold=True,
            size=9,
            alignment=(
                WD_ALIGN_PARAGRAPH.CENTER
                if i == 0
                else WD_ALIGN_PARAGRAPH.LEFT
            )
        )

        set_cell_shading(cell, "C6D9EA")

    set_repeat_table_header(main_table.rows[0])

    # Content rows
    for index, row_data in enumerate(rows, start=1):

        _, agenda_item, content, is_agenda, _ = row_data

        set_cell_text(
            main_table.cell(index, 0),
            str(index),
            bold=False,
            size=9,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )

        set_cell_text(
            main_table.cell(index, 1),
            agenda_item,
            bold=is_agenda or agenda_item in (
                "Decision",
                "Action Item"
            ),
            size=9
        )

        set_cell_text(
            main_table.cell(index, 2),
            content,
            size=9
        )

    # Column widths approximately matching the reference.
    for row in main_table.rows:
        set_column_width(row.cells[0], 0.4)
        set_column_width(row.cells[1], 2.0)
        set_column_width(row.cells[2], 4.8)

    document.add_paragraph().paragraph_format.space_after = Pt(3)

    # ---------------------------------------------------------
    # MEETING PHOTOGRAPH
    # ---------------------------------------------------------

    photo_row_table = document.add_table(rows=1, cols=3)
    photo_row_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    photo_row_table.autofit = False

    set_table_borders(photo_row_table, size="8")

    set_cell_text(
        photo_row_table.cell(0, 0),
        str(len(rows) + 1),
        size=9,
        alignment=WD_ALIGN_PARAGRAPH.CENTER
    )

    set_cell_text(
        photo_row_table.cell(0, 1),
        "Photo of the meeting",
        bold=True,
        size=9
    )

    photo_cell = photo_row_table.cell(0, 2)

    if photo_path:

        photo_cell.text = ""

        paragraph = photo_cell.paragraphs[0]
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        run = paragraph.add_run()

        try:
            run.add_picture(
                photo_path,
                width=Inches(3.0)
            )
        except Exception:
            set_cell_text(
                photo_cell,
                "Geotagged Photo",
                italic=True,
                size=9
            )

    else:
        set_cell_text(
            photo_cell,
            "Geotagged Photo",
            italic=True,
            size=9
        )

    for row in photo_row_table.rows:
        set_column_width(row.cells[0], 0.4)
        set_column_width(row.cells[1], 2.0)
        set_column_width(row.cells[2], 4.8)

    document.add_paragraph().paragraph_format.space_after = Pt(3)

    # ---------------------------------------------------------
    # ACTION TAKEN REPORT
    # ---------------------------------------------------------

    atr_table = document.add_table(rows=2, cols=4)
    atr_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    atr_table.autofit = False

    set_table_borders(atr_table, size="8")

    # Title row
    title_cell = atr_table.cell(0, 0)

    for i in range(1, 4):
        title_cell = title_cell.merge(
            atr_table.cell(0, i)
        )

    set_cell_text(
        title_cell,
        "Action Taken Report",
        bold=True,
        size=10,
        alignment=WD_ALIGN_PARAGRAPH.CENTER
    )

    set_cell_shading(title_cell, "FFFFFF")

    # Header row
    atr_headers = [
        "Reference",
        "Action Item",
        "Status",
        "Responsibility"
    ]

    for i, header in enumerate(atr_headers):

        cell = atr_table.cell(1, i)

        set_cell_text(
            cell,
            header,
            bold=True,
            size=9,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )

        set_cell_shading(cell, "C6D9EA")

    # Add action rows
    for action in action_items:

        row = atr_table.add_row()

        responsible = action.get(
            "responsible",
            "Not specified"
        )

        task = action.get(
            "task",
            "Not specified"
        )

        set_cell_text(
            row.cells[0],
            "MeetingNo.ItemSl.No",
            italic=True,
            size=8
        )

        set_cell_text(
            row.cells[1],
            task,
            size=8
        )

        set_cell_text(
            row.cells[2],
            "Not specified",
            size=8
        )

        set_cell_text(
            row.cells[3],
            responsible,
            size=8
        )

    # If there are no action items, provide one empty row.
    if not action_items:

        row = atr_table.add_row()

        set_cell_text(
            row.cells[0],
            "MeetingNo.ItemSl.No",
            italic=True,
            size=8
        )

        set_cell_text(
            row.cells[1],
            "No specific action items identified.",
            size=8
        )

        set_cell_text(
            row.cells[2],
            "Not specified",
            size=8
        )

        set_cell_text(
            row.cells[3],
            "Not specified",
            size=8
        )

    for row in atr_table.rows:
        set_column_width(row.cells[0], 1.3)
        set_column_width(row.cells[1], 3.6)
        set_column_width(row.cells[2], 0.8)
        set_column_width(row.cells[3], 1.5)

    document.add_paragraph().paragraph_format.space_after = Pt(5)

    # ---------------------------------------------------------
    # SIGNATURES
    # ---------------------------------------------------------

    signature_table = document.add_table(rows=2, cols=3)
    signature_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    signature_table.autofit = False

    # Remove visible borders from signature table.
    tbl = signature_table._tbl
    tbl_pr = tbl.tblPr

    borders = tbl_pr.first_child_found_in("w:tblBorders")

    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)

    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):

        element = OxmlElement(f"w:{edge}")
        element.set(qn("w:val"), "nil")

        borders.append(element)

    for i in range(3):

        set_cell_text(
            signature_table.cell(0, i),
            "Name and Signature",
            size=9,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )

        set_cell_text(
            signature_table.cell(1, i),
            ["Secretary", "Coordinator", "Chairman"][i],
            size=9,
            alignment=WD_ALIGN_PARAGRAPH.CENTER
        )

        set_column_width(
            signature_table.cell(0, i),
            2.4
        )

    # ---------------------------------------------------------
    # FOOTER / PAGE NUMBER
    # ---------------------------------------------------------

    footer = section.footer

    paragraph = footer.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT

    run = paragraph.add_run("Page ")

    run.font.name = "Times New Roman"
    run.font.size = Pt(8)

    # PAGE field
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")

    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "PAGE"

    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")

    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)

    run = paragraph.add_run("/")

    run.font.name = "Times New Roman"
    run.font.size = Pt(8)

    # NUMPAGES field
    run = paragraph.add_run()

    run.font.name = "Times New Roman"
    run.font.size = Pt(8)

    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")

    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = "NUMPAGES"

    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")

    run._r.append(fld_char1)
    run._r.append(instr_text)
    run._r.append(fld_char2)

    return document