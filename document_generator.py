from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH


def create_mom_document(
    meeting_title,
    participants,
    meeting_date,
    location,
    mom,
    photo_path=None,
    branding_path=None,
    branding_type="Logo"
):
    document = Document()


    # -----------------------------------------------------
    # INSTITUTION BRANDING
    # -----------------------------------------------------

    if branding_path:

        branding_paragraph = document.add_paragraph()

        branding_paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        run = branding_paragraph.add_run()

        if branding_type == "Logo":

            # Small centered logo
            run.add_picture(
                branding_path,
                width=Inches(1.35)
            )

        else:

            # Full-width letterhead / banner
            run.add_picture(
                branding_path,
                width=Inches(6.3)
            )

        # Small spacing after branding
        branding_paragraph.paragraph_format.space_after = (
            Inches(0.08)
        )


    # -----------------------------------------------------
    # TITLE
    # -----------------------------------------------------

    title = document.add_heading(
        "MINUTES OF MEETING",
        level=0
    )

    title.alignment = WD_ALIGN_PARAGRAPH.CENTER


    document.add_paragraph()


    # -----------------------------------------------------
    # MEETING DETAILS
    # -----------------------------------------------------

    document.add_heading(
        "Meeting Details",
        level=1
    )

    table = document.add_table(
        rows=4,
        cols=2
    )

    table.style = "Table Grid"


    details = [
        (
            "Meeting Title",
            meeting_title
            if meeting_title
            else "Not specified"
        ),
        (
            "Date",
            str(meeting_date)
        ),
        (
            "Participants",
            participants
            if participants
            else "Not specified"
        ),
        (
            "Location",
            location
            if location
            else "Not specified"
        ),
    ]


    for i, (label, value) in enumerate(details):

        table.cell(
            i,
            0
        ).text = label

        table.cell(
            i,
            1
        ).text = value


    # -----------------------------------------------------
    # AGENDA
    # -----------------------------------------------------

    document.add_heading(
        "Agenda",
        level=1
    )

    document.add_paragraph(
        mom.get(
            "agenda",
            "Not specified"
        )
    )


    # -----------------------------------------------------
    # DISCUSSION POINTS
    # -----------------------------------------------------

    document.add_heading(
        "Key Discussion Points",
        level=1
    )

    discussion_points = mom.get(
        "discussion_points",
        []
    )


    if discussion_points:

        for point in discussion_points:

            document.add_paragraph(
                point,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No specific discussion points identified."
        )


    # -----------------------------------------------------
    # DECISIONS
    # -----------------------------------------------------

    document.add_heading(
        "Decisions",
        level=1
    )

    decisions = mom.get(
        "decisions",
        []
    )


    if decisions:

        for decision in decisions:

            document.add_paragraph(
                decision,
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No specific decisions identified."
        )


    # -----------------------------------------------------
    # ACTION ITEMS
    # -----------------------------------------------------

    document.add_heading(
        "Action Items",
        level=1
    )

    action_items = mom.get(
        "action_items",
        []
    )


    if action_items:

        for action in action_items:

            responsible = action.get(
                "responsible",
                "Not specified"
            )

            task = action.get(
                "task",
                "Not specified"
            )

            document.add_paragraph(
                f"{responsible}: {task}",
                style="List Bullet"
            )

    else:

        document.add_paragraph(
            "No specific action items identified."
        )


    # -----------------------------------------------------
    # MEETING PHOTOGRAPH
    # -----------------------------------------------------

    if photo_path:

        document.add_heading(
            "Meeting Photograph",
            level=1
        )

        photo_paragraph = document.add_paragraph()

        photo_paragraph.alignment = (
            WD_ALIGN_PARAGRAPH.CENTER
        )

        photo_paragraph.add_run().add_picture(
            photo_path,
            width=Inches(5.5)
        )


    # -----------------------------------------------------
    # FOOTER / GENERATED BY
    # -----------------------------------------------------

    document.add_paragraph()

    footer_text = document.add_paragraph()

    footer_text.alignment = (
        WD_ALIGN_PARAGRAPH.CENTER
    )

    footer_text.add_run(
        "Generated using Faculty MoM Assistant"
    )


    return document