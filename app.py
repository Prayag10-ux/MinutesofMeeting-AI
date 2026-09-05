import streamlit as st
import tempfile
import textwrap
import html
from datetime import datetime

from transcription import transcribe_audio
from mom_generator import generate_mom
from document_generator import create_mom_document


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MoM AI — Faculty Meeting Intelligence",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# HELPERS
# ============================================================

def ui_html(content):
    """
    Render custom HTML using Streamlit's native HTML renderer.
    """
    st.html(textwrap.dedent(content).strip())


def esc(value):
    """
    Safely escape text before putting it inside HTML.
    """
    return html.escape(str(value))


# ============================================================
# GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       PROFESSIONAL DARK NAVY THEME
       ======================================================== */

    :root {

        --bg: #0b1220;

        --surface: #111b2d;

        --surface-2: #162238;

        --surface-3: #1b2940;

        --border: #2d3c54;

        --border-light: #40516a;

        --text: #f4f6f8;

        --text-soft: #c3ccd8;

        --muted: #8996a8;

        --accent: #6f9dcc;

        --accent-light: #9dbce0;

        --white: #f4f6f8;

        --black: #0b1220;
    }


    /* ========================================================
       GLOBAL
       ======================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at 15% 0%,
                rgba(111,157,204,0.10),
                transparent 28%
            ),

            radial-gradient(
                circle at 90% 85%,
                rgba(111,157,204,0.06),
                transparent 30%
            ),

            var(--bg);

        color: var(--text);
    }


    .main .block-container {

        max-width: 1380px;

        padding-top: 28px;

        padding-bottom: 80px;
    }


    header {
        visibility: hidden;
    }


    footer {
        visibility: hidden;
    }


    /* ========================================================
       TYPOGRAPHY
       ======================================================== */

    p {
        color: var(--text-soft);
    }


    label {

        color: #d3dbe5 !important;

        font-weight: 650 !important;

        font-size: 12px !important;
    }


    /* ========================================================
       TEXT INPUTS
       ======================================================== */

    .stTextInput input,
    .stTextArea textarea,
    [data-testid="stDateInput"] input {

        background: #0e1828 !important;

        color: var(--text) !important;

        border: 1px solid var(--border-light) !important;

        border-radius: 5px !important;

        box-shadow: none !important;

        min-height: 46px;

        font-size: 14px !important;
    }


    .stTextInput input::placeholder {

        color: #69778a !important;
    }


    .stTextInput input:hover,
    .stTextArea textarea:hover,
    [data-testid="stDateInput"] input:hover {

        border-color: #60738d !important;
    }


    .stTextInput input:focus,
    .stTextArea textarea:focus,
    [data-testid="stDateInput"] input:focus {

        border-color: var(--accent) !important;

        box-shadow:
            0 0 0 1px var(--accent) !important;
    }


    /* ========================================================
       FILE UPLOADER
       ======================================================== */

    [data-testid="stFileUploader"] {

        background: #0e1828 !important;

        border: 1px dashed #52657e !important;

        border-radius: 5px !important;

        padding: 8px !important;
    }


    [data-testid="stFileUploader"] section {

        background: transparent !important;
    }


    [data-testid="stFileUploaderDropzoneInstructions"] {

        color: #9ba8b8 !important;
    }


    /* ========================================================
       AUDIO RECORDER
       ======================================================== */

    [data-testid="stAudioInput"] {

        background: #0e1828 !important;

        border: 1px solid var(--border-light) !important;

        border-radius: 5px !important;

        padding: 12px !important;
    }


    /* ========================================================
       PRIMARY BUTTON
       ======================================================== */

    .stButton > button {

        background: #e7edf4 !important;

        color: #0b1220 !important;

        border: 1px solid #e7edf4 !important;

        border-radius: 5px !important;

        min-height: 50px;

        font-weight: 900 !important;

        letter-spacing: 0.8px;

        box-shadow:
            0 4px 0 #050912 !important;

        transition:
            transform 0.12s ease,
            box-shadow 0.12s ease !important;
    }


    .stButton > button:hover {

        background: #ffffff !important;

        border-color: #ffffff !important;

        transform: translateY(2px);

        box-shadow:
            0 2px 0 #050912 !important;
    }


    /* ========================================================
       DOWNLOAD BUTTON
       ======================================================== */

    .stDownloadButton > button {

        background: #1b2a40 !important;

        color: #eaf0f6 !important;

        border: 1px solid #52657e !important;

        border-radius: 5px !important;

        min-height: 50px;

        font-weight: 900 !important;

        letter-spacing: 0.8px;
    }


    .stDownloadButton > button:hover {

        background: #263a55 !important;

        color: #ffffff !important;

        border-color: var(--accent-light) !important;
    }


    /* ========================================================
       ALERTS
       ======================================================== */

    [data-testid="stAlert"] {

        background: #152238 !important;

        border: 1px solid #354963 !important;

        border-radius: 5px !important;

        color: #d7e0ea !important;
    }


    /* ========================================================
       EXPANDER
       ======================================================== */

    [data-testid="stExpander"] {

        background: #101a2b !important;

        border: 1px solid #34465e !important;

        border-radius: 5px !important;
    }


    [data-testid="stExpander"] summary {

        color: #e1e7ee !important;

        font-weight: 800 !important;
    }


    /* ========================================================
       RADIO
       ======================================================== */

    [data-testid="stRadio"] label {

        color: #cbd5e1 !important;
    }


    /* ========================================================
       DIVIDERS
       ======================================================== */

    hr {

        border-color: #27374d !important;
    }


    /* ========================================================
       RESPONSIVE
       ======================================================== */

    @media (max-width: 900px) {

        .main .block-container {

            padding-left: 18px;

            padding-right: 18px;
        }

    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# TOP NAVIGATION
# ============================================================

ui_html(
    """
    <div style="
        display:flex;
        justify-content:space-between;
        align-items:center;

        padding:8px 0 26px 0;

        border-bottom:1px solid #2d3c54;

        margin-bottom:32px;
    ">

        <div style="
            display:flex;
            align-items:center;
            gap:12px;
        ">

            <div style="
                width:38px;
                height:38px;

                display:flex;
                align-items:center;
                justify-content:center;

                background:#e7edf4;

                color:#0b1220;

                border-radius:5px;

                font-size:19px;

                font-weight:900;
            ">
                ◈
            </div>

            <div>

                <div style="
                    color:#f4f6f8;

                    font-size:14px;

                    font-weight:900;

                    letter-spacing:1.7px;

                    text-transform:uppercase;
                ">
                    MoM AI
                </div>

                <div style="
                    color:#8996a8;

                    font-size:9px;

                    font-weight:700;

                    letter-spacing:1.5px;

                    text-transform:uppercase;

                    margin-top:3px;
                ">
                    Faculty Meeting Intelligence
                </div>

            </div>

        </div>


        <div style="
            border:1px solid #40516a;

            background:#111b2d;

            padding:8px 12px;

            color:#9ba8b8;

            font-size:9px;

            font-weight:800;

            letter-spacing:1.3px;

            text-transform:uppercase;
        ">

            <span style="
                display:inline-block;

                width:7px;
                height:7px;

                background:#8eb0d4;

                margin-right:7px;

                vertical-align:middle;

                border-radius:50%;
            "></span>

            Local AI System

        </div>

    </div>
    """
)


# ============================================================
# HERO
# ============================================================

ui_html(
    """
    <div style="
        position:relative;

        overflow:hidden;

        background:
            linear-gradient(
                135deg,
                #1b2b43 0%,
                #142238 55%,
                #0d1727 100%
            );

        border:1px solid #40516a;

        padding:58px 60px;

        margin-bottom:22px;

        min-height:360px;

        box-sizing:border-box;

        border-radius:5px;
    ">

        <div style="
            position:absolute;

            top:24px;
            right:28px;

            color:#718197;

            font-size:9px;

            font-weight:800;

            letter-spacing:1.5px;
        ">
            WHISPER / GEMMA 3 / OLLAMA
        </div>


        <div style="
            color:#9aa9ba;

            font-size:10px;

            font-weight:900;

            letter-spacing:2.5px;

            text-transform:uppercase;

            margin-bottom:22px;
        ">
            AI Meeting Intelligence
        </div>


        <div style="
            color:#f4f6f8;

            font-size:clamp(48px, 7vw, 88px);

            font-weight:950;

            line-height:0.88;

            letter-spacing:-5px;

            max-width:850px;
        ">
            MINUTES.<br>

            <span style="
                color:#91a4b9;
            ">
                WITHOUT THE WORK.
            </span>
        </div>


        <div style="
            max-width:620px;

            color:#bdc8d5;

            font-size:14px;

            line-height:1.7;

            margin-top:28px;
        ">
            Record the conversation. Let local AI understand it.
            Automatically turn the meeting into structured,
            professional Minutes of Meeting ready for review,
            institutional branding and export.
        </div>


        <div style="
            position:absolute;

            width:210px;
            height:210px;

            right:-85px;
            bottom:-100px;

            border:1px solid #34465e;

            transform:rotate(45deg);
        "></div>

    </div>
    """
)


# ============================================================
# WORKFLOW
# ============================================================

workflow_items = [
    ("01", "RECORD", "Capture the meeting"),
    ("02", "TRANSCRIBE", "Whisper converts speech"),
    ("03", "ANALYSE", "Gemma extracts the MoM"),
    ("04", "EXPORT", "Download the final document"),
]


workflow_html = """
<div style="
    display:grid;

    grid-template-columns:repeat(4,1fr);

    gap:1px;

    background:#34465e;

    border:1px solid #34465e;

    margin-bottom:52px;

    border-radius:5px;

    overflow:hidden;
">
"""


for number, title, description in workflow_items:

    workflow_html += f"""
    <div style="
        background:#111b2d;

        padding:20px 22px;

        min-height:90px;

        box-sizing:border-box;
    ">

        <div style="
            color:#718197;

            font-size:9px;

            font-weight:900;

            letter-spacing:1.5px;

            margin-bottom:14px;
        ">
            {number}
        </div>

        <div style="
            color:#edf1f5;

            font-size:13px;

            font-weight:900;

            letter-spacing:1px;
        ">
            {title}
        </div>

        <div style="
            color:#8996a8;

            font-size:10px;

            margin-top:5px;
        ">
            {description}
        </div>

    </div>
    """


workflow_html += "</div>"

ui_html(workflow_html)


# ============================================================
# SECTION HEADER
# ============================================================

def section_header(number, title):

    ui_html(
        f"""
        <div style="
            display:flex;

            align-items:flex-end;

            gap:15px;

            margin-top:42px;

            margin-bottom:20px;
        ">

            <div style="
                color:#718197;

                font-size:10px;

                font-weight:900;

                letter-spacing:1.5px;

                padding-bottom:4px;
            ">
                {number}
            </div>

            <div style="
                color:#f4f6f8;

                font-size:27px;

                font-weight:900;

                letter-spacing:-1px;

                line-height:1;
            ">
                {esc(title)}
            </div>

            <div style="
                flex:1;

                height:1px;

                background:#2d3c54;

                margin-bottom:5px;
            "></div>

        </div>
        """
    )


# ============================================================
# INFO CARD
# ============================================================

def info_card(kicker, title, description):

    ui_html(
        f"""
        <div style="
            background:#111b2d;

            border:1px solid #34465e;

            padding:23px;

            margin-bottom:14px;

            border-radius:5px;
        ">

            <div style="
                color:#7f8da0;

                font-size:9px;

                font-weight:900;

                letter-spacing:1.7px;

                text-transform:uppercase;

                margin-bottom:9px;
            ">
                {esc(kicker)}
            </div>

            <div style="
                color:#edf1f5;

                font-size:19px;

                font-weight:850;

                letter-spacing:-0.4px;

                margin-bottom:6px;
            ">
                {esc(title)}
            </div>

            <div style="
                color:#9aa7b7;

                font-size:11px;

                line-height:1.6;
            ">
                {esc(description)}
            </div>

        </div>
        """
    )


# ============================================================
# SECTION 01 — MEETING DETAILS
# ============================================================

section_header("01", "Meeting details")


left, right = st.columns(
    2,
    gap="large"
)


with left:

    info_card(
        "Basic information",
        "What is this meeting about?",
        "These details become part of the official meeting record."
    )

    meeting_title = st.text_input(
        "Meeting Title",
        placeholder="AI & ML Department Workshop Planning"
    )

    participants = st.text_input(
        "Participants",
        placeholder="Dr. Thomas, Rahul, Anu"
    )


with right:

    info_card(
        "Meeting context",
        "When and where?",
        "The date and location will be included in the generated MoM."
    )

    meeting_date = st.date_input(
        "Meeting Date",
        value=datetime.now().date()
    )

    location = st.text_input(
        "Meeting Location",
        placeholder="AI & ML Department, Lab 204"
    )


# ============================================================
# SECTION 02 — INSTITUTIONAL BRANDING
# ============================================================

section_header("02", "Institutional identity")


brand_left, brand_right = st.columns(
    [1.15, 0.85],
    gap="large"
)


with brand_left:

    info_card(
        "Optional",
        "Make the document official.",
        "Upload your institution's logo, letterhead or banner. "
        "It will be placed at the top of the generated Word document."
    )

    branding_type = st.radio(
        "Branding format",
        [
            "Logo",
            "Letterhead / Banner"
        ],
        horizontal=True
    )

    branding = st.file_uploader(
        "Upload institution branding",
        type=[
            "png",
            "jpg",
            "jpeg"
        ],
        help="PNG with transparency is recommended for logos."
    )


with brand_right:

    if branding:

        ui_html(
            """
            <div style="
                color:#8996a8;

                font-size:9px;

                font-weight:900;

                letter-spacing:1.7px;

                text-transform:uppercase;

                margin-bottom:10px;
            ">
                Branding preview
            </div>
            """
        )

        st.image(
            branding,
            use_container_width=True
        )

    else:

        info_card(
            "Preview",
            "No branding selected",
            "Your document will use the default MoM layout unless "
            "an institution image is uploaded."
        )


# ============================================================
# SECTION 03 — RECORDING
# ============================================================

section_header("03", "Record the meeting")


record_left, record_right = st.columns(
    [1.25, 0.75],
    gap="large"
)


with record_left:

    info_card(
        "Audio capture",
        "Start the conversation.",
        "Record directly from your browser. The recording is "
        "processed locally using Whisper."
    )

    audio = st.audio_input(
        "Record your meeting"
    )


with record_right:

    info_card(
        "Privacy first",
        "Local AI processing.",
        "Whisper handles transcription and Gemma 3 analyses "
        "the meeting through Ollama on your machine."
    )

    st.info(
        "Make sure all participants are aware that the meeting "
        "is being recorded."
    )


# ============================================================
# SECTION 04 — MEETING EVIDENCE
# ============================================================

section_header("04", "Meeting evidence")


photo_left, photo_right = st.columns(
    [1.2, 0.8],
    gap="large"
)


with photo_left:

    info_card(
        "Meeting record",
        "Add the meeting photograph.",
        "Upload the photograph required for the official meeting "
        "record. It will also be embedded into the final DOCX."
    )

    photo = st.file_uploader(
        "Upload meeting photograph",
        type=[
            "jpg",
            "jpeg",
            "png"
        ]
    )


with photo_right:

    if photo:

        ui_html(
            """
            <div style="
                color:#8996a8;

                font-size:9px;

                font-weight:900;

                letter-spacing:1.7px;

                text-transform:uppercase;

                margin-bottom:10px;
            ">
                Meeting photograph
            </div>
            """
        )

        st.image(
            photo,
            use_container_width=True
        )

    else:

        info_card(
            "Required",
            "Waiting for photograph",
            "Upload the meeting photograph before generating "
            "the final MoM."
        )


# ============================================================
# GENERATION AREA
# ============================================================

if audio:

    st.markdown(
        "<div style='height:12px'></div>",
        unsafe_allow_html=True
    )


    if photo:

        ui_html(
            """
            <div style="
                background:#1a304b;

                color:#cfe0f2;

                border:1px solid #4d6b8d;

                padding:14px 17px;

                font-size:9px;

                font-weight:900;

                letter-spacing:1.4px;

                text-transform:uppercase;

                margin-bottom:18px;

                border-radius:5px;
            ">
                ● Meeting recording ready for AI analysis
            </div>
            """
        )

    else:

        st.warning(
            "Upload the meeting photograph before generating the MoM."
        )


    st.audio(audio)


    st.markdown(
        "<div style='height:14px'></div>",
        unsafe_allow_html=True
    )


    generate_button = st.button(
        "GENERATE MINUTES OF MEETING  →",
        type="primary",
        use_container_width=True
    )


    if generate_button:

        # ====================================================
        # VALIDATION
        # ====================================================

        if not meeting_title.strip():

            st.warning(
                "Please enter a meeting title."
            )

            st.stop()


        if not participants.strip():

            st.warning(
                "Please enter the participant names."
            )

            st.stop()


        if not location.strip():

            st.warning(
                "Please enter the meeting location."
            )

            st.stop()


        if not photo:

            st.warning(
                "Please upload the meeting photograph."
            )

            st.stop()


        # ====================================================
        # TEMP AUDIO
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            temp_audio.write(
                audio.getvalue()
            )

            audio_path = temp_audio.name


        # ====================================================
        # PROCESSING
        # ====================================================

        section_header(
            "AI",
            "Processing meeting"
        )


        # ====================================================
        # TRANSCRIPTION
        # ====================================================

        with st.spinner(
            "Whisper is transcribing the meeting..."
        ):

            try:

                transcript = transcribe_audio(
                    audio_path
                )

            except Exception as e:

                st.error(
                    f"Transcription failed: {e}"
                )

                st.stop()


        if not transcript.strip():

            st.error(
                "No speech could be detected in the recording."
            )

            st.stop()


        st.success(
            "Transcription complete."
        )


        # ====================================================
        # TRANSCRIPT
        # ====================================================

        with st.expander(
            "VIEW RAW TRANSCRIPT",
            expanded=False
        ):

            st.text_area(
                "Transcript",
                transcript,
                height=300
            )


        # ====================================================
        # GEMMA
        # ====================================================

        with st.spinner(
            "Gemma 3 is analysing the conversation..."
        ):

            try:

                mom = generate_mom(
                    transcript,
                    participants
                )

            except Exception as e:

                st.error(
                    f"AI MoM generation failed: {e}"
                )

                st.info(
                    "Make sure Ollama is running and "
                    "Gemma 3 4B is installed."
                )

                st.stop()


        st.success(
            "Minutes generated successfully."
        )


        # ====================================================
        # RESULTS
        # ====================================================

        section_header(
            "05",
            "Generated minutes"
        )


        # ====================================================
        # META INFORMATION
        # ====================================================

        meta_data = [
            ("Meeting", meeting_title),
            ("Date", meeting_date),
            ("Participants", participants),
            ("Location", location),
        ]


        meta_html = """
        <div style="
            display:grid;

            grid-template-columns:repeat(4,1fr);

            gap:1px;

            background:#34465e;

            border:1px solid #34465e;

            margin-bottom:22px;

            border-radius:5px;

            overflow:hidden;
        ">
        """


        for label, value in meta_data:

            meta_html += f"""
            <div style="
                background:#111b2d;

                padding:17px 19px;

                min-height:72px;
            ">

                <div style="
                    color:#718197;

                    font-size:8px;

                    font-weight:900;

                    letter-spacing:1.5px;

                    text-transform:uppercase;

                    margin-bottom:7px;
                ">
                    {esc(label)}
                </div>

                <div style="
                    color:#e4e9ee;

                    font-size:12px;

                    font-weight:700;

                    line-height:1.4;
                ">
                    {esc(value)}
                </div>

            </div>
            """


        meta_html += "</div>"


        ui_html(meta_html)


        # ====================================================
        # AGENDA
        # ====================================================

        agenda = mom.get(
            "agenda",
            "Not specified"
        )


        ui_html(
            f"""
            <div style="
                background:#111b2d;

                border:1px solid #34465e;

                padding:23px;

                margin-bottom:18px;

                border-radius:5px;
            ">

                <div style="
                    display:flex;

                    justify-content:space-between;

                    border-bottom:1px solid #2d3c54;

                    padding-bottom:12px;

                    margin-bottom:15px;
                ">

                    <div style="
                        color:#8996a8;

                        font-size:9px;

                        font-weight:900;

                        letter-spacing:1.7px;

                        text-transform:uppercase;
                    ">
                        Agenda
                    </div>

                    <div style="
                        color:#65758a;

                        font-size:9px;

                        font-weight:900;
                    ">
                        01
                    </div>

                </div>

                <div style="
                    color:#d6dee7;

                    font-size:14px;

                    line-height:1.7;
                ">
                    {esc(agenda)}
                </div>

            </div>
            """
        )


        # ====================================================
        # DISCUSSION + DECISIONS
        # ====================================================

        discussion_points = mom.get(
            "discussion_points",
            []
        )

        decisions = mom.get(
            "decisions",
            []
        )


        discussion_col, decision_col = st.columns(
            2,
            gap="large"
        )


        # ====================================================
        # DISCUSSION
        # ====================================================

        with discussion_col:

            ui_html(
                """
                <div style="
                    background:#111b2d;

                    border:1px solid #34465e;

                    padding:23px;

                    margin-bottom:18px;

                    border-radius:5px;
                ">

                    <div style="
                        display:flex;

                        justify-content:space-between;

                        border-bottom:1px solid #2d3c54;

                        padding-bottom:12px;

                        margin-bottom:15px;
                    ">

                        <div style="
                            color:#8996a8;

                            font-size:9px;

                            font-weight:900;

                            letter-spacing:1.7px;

                            text-transform:uppercase;
                        ">
                            Key Discussion Points
                        </div>

                        <div style="
                            color:#65758a;

                            font-size:9px;

                            font-weight:900;
                        ">
                            02
                        </div>

                    </div>
                """
            )


            if discussion_points:

                for point in discussion_points:

                    ui_html(
                        f"""
                        <div style="
                            background:#192941;

                            border-left:3px solid #6f9dcc;

                            padding:12px 14px;

                            margin-bottom:8px;

                            color:#d2dbe5;

                            font-size:12px;

                            line-height:1.55;

                            border-radius:2px;
                        ">
                            {esc(point)}
                        </div>
                        """
                    )

            else:

                st.write(
                    "No specific discussion points identified."
                )


            ui_html(
                """
                </div>
                """
            )


        # ====================================================
        # DECISIONS
        # ====================================================

        with decision_col:

            ui_html(
                """
                <div style="
                    background:#111b2d;

                    border:1px solid #34465e;

                    padding:23px;

                    margin-bottom:18px;

                    border-radius:5px;
                ">

                    <div style="
                        display:flex;

                        justify-content:space-between;

                        border-bottom:1px solid #2d3c54;

                        padding-bottom:12px;

                        margin-bottom:15px;
                    ">

                        <div style="
                            color:#8996a8;

                            font-size:9px;

                            font-weight:900;

                            letter-spacing:1.7px;

                            text-transform:uppercase;
                        ">
                            Decisions
                        </div>

                        <div style="
                            color:#65758a;

                            font-size:9px;

                            font-weight:900;
                        ">
                            03
                        </div>

                    </div>
                """
            )


            if decisions:

                for decision in decisions:

                    ui_html(
                        f"""
                        <div style="
                            background:#192941;

                            border-left:3px solid #9dbce0;

                            padding:12px 14px;

                            margin-bottom:8px;

                            color:#d2dbe5;

                            font-size:12px;

                            line-height:1.55;

                            border-radius:2px;
                        ">
                            {esc(decision)}
                        </div>
                        """
                    )

            else:

                st.write(
                    "No specific decisions identified."
                )


            ui_html(
                """
                </div>
                """
            )


        # ====================================================
        # ACTION ITEMS
        # ====================================================

        action_items = mom.get(
            "action_items",
            []
        )


        ui_html(
            """
            <div style="
                background:#111b2d;

                border:1px solid #34465e;

                padding:23px;

                margin-bottom:18px;

                border-radius:5px;
            ">

                <div style="
                    display:flex;

                    justify-content:space-between;

                    border-bottom:1px solid #2d3c54;

                    padding-bottom:12px;

                    margin-bottom:15px;
                ">

                    <div style="
                        color:#8996a8;

                        font-size:9px;

                        font-weight:900;

                        letter-spacing:1.7px;

                        text-transform:uppercase;
                    ">
                        Action Items
                    </div>

                    <div style="
                        color:#65758a;

                        font-size:9px;

                        font-weight:900;
                    ">
                        04
                    </div>

                </div>
            """
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


                ui_html(
                    f"""
                    <div style="
                        display:grid;

                        grid-template-columns:150px 1fr;

                        border:1px solid #34465e;

                        background:#0e1828;

                        margin-bottom:8px;

                        border-radius:3px;

                        overflow:hidden;
                    ">

                        <div style="
                            padding:15px;

                            border-right:1px solid #34465e;

                            color:#9db0c5;

                            font-size:8px;

                            font-weight:900;

                            letter-spacing:1.2px;

                            text-transform:uppercase;
                        ">
                            {esc(responsible)}
                        </div>

                        <div style="
                            padding:15px;

                            color:#e0e6ec;

                            font-size:12px;

                            font-weight:650;

                            line-height:1.55;
                        ">
                            {esc(task)}
                        </div>

                    </div>
                    """
                )

        else:

            st.write(
                "No specific action items identified."
            )


        ui_html(
            """
            </div>
            """
        )


        # ====================================================
        # MEETING EVIDENCE
        # ====================================================

        section_header(
            "06",
            "Meeting evidence"
        )


        evidence_left, evidence_right = st.columns(
            [1.2, 0.8],
            gap="large"
        )


        with evidence_left:

            ui_html(
                """
                <div style="
                    color:#8996a8;

                    font-size:9px;

                    font-weight:900;

                    letter-spacing:1.7px;

                    text-transform:uppercase;

                    margin-bottom:10px;
                ">
                    Meeting photograph
                </div>
                """
            )

            st.image(
                photo,
                use_container_width=True
            )


        with evidence_right:

            info_card(
                "Document verification",
                "Evidence attached.",
                "The meeting photograph will be embedded into the "
                "final Word document together with the generated "
                "Minutes of Meeting."
            )


        # ====================================================
        # TEMP PHOTO
        # ====================================================

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".jpg"
        ) as temp_photo:

            temp_photo.write(
                photo.getvalue()
            )

            photo_path = temp_photo.name


        # ====================================================
        # TEMP BRANDING
        # ====================================================

        branding_path = None


        if branding:

            if branding.type == "image/png":

                branding_extension = ".png"

            else:

                branding_extension = ".jpg"


            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=branding_extension
            ) as temp_branding:

                temp_branding.write(
                    branding.getvalue()
                )

                branding_path = temp_branding.name


        # ====================================================
        # EXPORT
        # ====================================================

        section_header(
            "07",
            "Export document"
        )


        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".docx"
        ) as temp_docx:

            try:

                document = create_mom_document(
                    meeting_title=meeting_title,
                    participants=participants,
                    meeting_date=meeting_date,
                    location=location,
                    mom=mom,
                    photo_path=photo_path,
                    branding_path=branding_path,
                    branding_type=branding_type
                )

                document.save(
                    temp_docx.name
                )

            except Exception as e:

                st.error(
                    f"Could not create DOCX: {e}"
                )

                st.stop()


            with open(
                temp_docx.name,
                "rb"
            ) as file:

                docx_data = file.read()


        info_card(
            "Final document",
            "Your Minutes are ready.",
            "The final Word document contains the meeting details, "
            "AI-generated minutes, action items, institutional "
            "branding and meeting photograph."
        )


        st.markdown(
            "<div style='height:8px'></div>",
            unsafe_allow_html=True
        )


        st.download_button(
            label="DOWNLOAD MINUTES OF MEETING  ↓",
            data=docx_data,
            file_name="Faculty_MoM.docx",
            mime=(
                "application/vnd.openxmlformats-officedocument."
                "wordprocessingml.document"
            ),
            use_container_width=True
        )


        ui_html(
            """
            <div style="
                background:#1a304b;

                color:#cfe0f2;

                border:1px solid #4d6b8d;

                padding:14px 17px;

                font-size:9px;

                font-weight:900;

                letter-spacing:1.4px;

                text-transform:uppercase;

                margin-top:18px;

                border-radius:5px;
            ">
                ✓ Document generated successfully
            </div>
            """
        )


# ============================================================
# FOOTER
# ============================================================

ui_html(
    """
    <div style="
        border-top:1px solid #2d3c54;

        margin-top:65px;

        padding-top:17px;

        display:flex;

        justify-content:space-between;

        color:#68778b;

        font-size:8px;

        font-weight:800;

        letter-spacing:1.4px;

        text-transform:uppercase;
    ">

        <span>
            MOM AI / FACULTY MEETING INTELLIGENCE
        </span>

        <span>
            WHISPER · GEMMA 3 · OLLAMA
        </span>

    </div>
    """
)