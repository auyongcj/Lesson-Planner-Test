from __future__ import annotations

from io import BytesIO

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, KeepTogether
)

from .lesson_schema import LessonPlanDoc


# ── Colours ───────────────────────────────────────────────────────────────────
_HEADER_BG = colors.HexColor("#cfcfcf")
_BORDER    = colors.HexColor("#4b4b4b")
_WHITE     = colors.white
_TEXT      = colors.HexColor("#111111")

# ── Page geometry ─────────────────────────────────────────────────────────────
_MARGIN = 1.8 * cm
_PW, _PH = A4
_UW = _PW - 2 * _MARGIN

# ── Paragraph styles ──────────────────────────────────────────────────────────
def _ps(name, font="Helvetica", size=10, align=TA_LEFT, indent=0, space_before=0, space_after=0):
    return ParagraphStyle(
        name,
        fontName=font,
        fontSize=size,
        leading=size + 3,
        textColor=_TEXT,
        alignment=align,
        leftIndent=indent,
        spaceBefore=space_before,
        spaceAfter=space_after,
    )

N           = _ps("N")
NC          = _ps("NC",          align=TA_CENTER)
NR          = _ps("NR",          align=TA_RIGHT)
BR          = _ps("BR",          font="Helvetica-Bold", align=TA_RIGHT)
BL          = _ps("BL",          font="Helvetica-Bold")
BC          = _ps("BC",          font="Helvetica-Bold", align=TA_CENTER)
SEC         = _ps("SEC",         font="Helvetica-Bold", size=10, space_before=6, space_after=1)
BULL        = _ps("BULL",        indent=10)
BULL_INDENT = _ps("BULL_INDENT", indent=22)
AUTH        = _ps("AUTH",        indent=28)


# ── Shared table style commands ───────────────────────────────────────────────
_GRID    = [("GRID",        (0, 0), (-1, -1), 0.8, _BORDER)]
_VALMID  = [("VALIGN",      (0, 0), (-1, -1), "TOP")]
_PAD     = [
    ("TOPPADDING",    (0, 0), (-1, -1), 5),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ("LEFTPADDING",   (0, 0), (-1, -1), 6),
    ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
]
_BGWHITE = [("BACKGROUND",  (0, 0), (-1, -1), _WHITE)]
_BASE    = _GRID + _VALMID + _PAD + _BGWHITE


def _hdr_cmds(row):
    return [
        ("BACKGROUND",    (0, row), (-1, row), _HEADER_BG),
        ("FONTNAME",      (0, row), (-1, row), "Helvetica-Bold"),
        ("ALIGN",         (0, row), (-1, row), "CENTER"),
        ("VALIGN",        (0, row), (-1, row), "MIDDLE"),
        ("TOPPADDING",    (0, row), (-1, row), 4),
        ("BOTTOMPADDING", (0, row), (-1, row), 4),
    ]


# ── Helpers ───────────────────────────────────────────────────────────────────
def _safe(text):
    return (text or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _p(text, style=None):
    return Paragraph(_safe(text) or "&nbsp;", style or N)


def _remarks_to_cell(rb):
    if rb is None:
        return [_p("")]
    result = []
    lead = (rb.lead or "").strip()
    if lead:
        result.append(Paragraph(_safe(lead), N))
    items = getattr(rb, "items", None) or []
    style = getattr(rb, "style", "bullet") or "bullet"
    ROMAN = ["i","ii","iii","iv","v","vi","vii","viii","ix","x",
             "xi","xii","xiii","xiv","xv","xvi","xvii","xviii","xix","xx"]
    for idx, it in enumerate(items):
        text = (getattr(it, "text", "") or "").strip()
        if style == "number":
            prefix = f"{idx + 1}."
        elif style == "roman":
            prefix = f"{ROMAN[idx] if idx < len(ROMAN) else idx + 1}."
        else:
            prefix = "•"
        result.append(Paragraph(f"{prefix} {_safe(text)}", BULL))
        subitems = getattr(it, "subitems", None) or []
        for k, sub in enumerate(subitems):
            s = (sub or "").strip()
            result.append(Paragraph(f"{ROMAN[k] if k < len(ROMAN) else k+1}. {_safe(s)}", BULL_INDENT))
    return result or [_p("")]


def _sum_minutes(rows) -> str:
    total = 0
    for r in rows:
        txt = r.time_minutes or ""
        digits = ""
        for ch in txt:
            if ch.isdigit():
                digits += ch
            elif digits:
                break
        if digits:
            total += int(digits)
    return f"{total} MINUTES" if total else ""


def _bullets(items, fallback="NIL."):
    if not items:
        return [Paragraph(f"• {_safe(fallback)}", BULL)]
    return [Paragraph(f"• {_safe(x)}", BULL) for x in items]


# ── Section builders ──────────────────────────────────────────────────────────
def _build_section4(doc, total_minutes):
    cw = [_UW * 0.22, _UW * 0.58, _UW * 0.20]
    data  = [[_p("Stage", BC), _p("Activity", BC), _p("Time (Minutes)", BC)]]
    extra = list(_hdr_cmds(0))

    for r in doc.lesson_info_rows:
        data.append([_p(r.stage, NC), _p(r.activity, NC), _p(r.time_minutes, NC)])
    if not doc.lesson_info_rows:
        data.append([_p(""), _p(""), _p("")])

    tr = len(data)
    data.append([_p("Total", BR), "", _p(total_minutes, BC)])
    extra += [
        ("SPAN",     (0, tr), (1, tr)),
        ("ALIGN",    (0, tr), (1, tr), "RIGHT"),
        ("FONTNAME", (0, tr), (-1, tr), "Helvetica-Bold"),
    ]

    for label, value in [
        ("Attire",                 doc.attire),
        ("Targeted\nParticipants", doc.targeted_participants),
        ("Location",               doc.location),
    ]:
        row = len(data)
        data.append([_p(label, BC), _p(value, BL), ""])
        extra += [
            ("SPAN",     (1, row), (2, row)),
            ("FONTNAME", (0, row), (-1, row), "Helvetica-Bold"),
            ("ALIGN",    (1, row), (2, row), "LEFT"),
        ]

    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_BASE + extra))
    return t


def _build_section5(doc):
    cw    = [_UW * 0.22, _UW * 0.58, _UW * 0.20]
    data  = [[_p("Logistics", BC), _p("Remarks", BC), _p("Quantity", BC)]]
    extra = list(_hdr_cmds(0))

    for r in doc.logistics_rows:
        data.append([_p(r.logistics, NC), _p(r.remarks, NC), _p(r.quantity, NC)])
    if not doc.logistics_rows:
        data.append([_p(""), _p(""), _p("")])

    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_BASE + extra))
    return t


def _build_section6(doc):
    cw = [_UW * 0.12, _UW * 0.28, _UW * 0.60]
    data = [
        [_p("TRAINING PERSONNEL:", BC), "", _p(doc.training_personnel_line or "", BC)],
        [_p("Stage", BC), _p("Activity", BC), _p("Remarks", BC)],
    ]
    extra = [
        ("SPAN",          (0, 0), (1, 0)),
        ("BACKGROUND",    (0, 0), (-1, 0), _HEADER_BG),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN",         (0, 0), (-1, 0), "CENTER"),
        ("VALIGN",        (0, 0), (-1, 0), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, 0), 4),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 4),
    ] + _hdr_cmds(1)

    for r in doc.method_rows:
        data.append([_p(r.stage, NC), _p(r.activity, NC), _remarks_to_cell(r.remarks)])
    if not doc.method_rows:
        data.append([_p(""), _p(""), _p("")])

    t = Table(data, colWidths=cw, repeatRows=2)
    t.setStyle(TableStyle(_BASE + extra))
    return t


def _build_section7(doc):
    cw    = [_UW * 0.22, _UW * 0.28, _UW * 0.50]
    data  = [[_p("Roles", BC), _p("Name(s) of personnel", BC), _p("Remarks", BC)]]
    extra = list(_hdr_cmds(0))

    for r in doc.personnel_rows:
        data.append([_p(r.role, N), _p(r.names, N), _p(r.remarks, N)])
    if not doc.personnel_rows:
        data.append([_p(""), _p(""), _p("")])

    t = Table(data, colWidths=cw, repeatRows=1)
    t.setStyle(TableStyle(_BASE + extra))
    return t


# ── Main ──────────────────────────────────────────────────────────────────────
def render_lesson_pdf(doc: LessonPlanDoc) -> bytes:
    buf = BytesIO()
    pdf = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=_MARGIN,
        rightMargin=_MARGIN,
        topMargin=_MARGIN,
        bottomMargin=_MARGIN,
    )

    total_minutes = _sum_minutes(doc.lesson_info_rows)
    story = []

    # 1. Lesson Title
    story.append(KeepTogether([
        Paragraph("1. LESSON TITLE", SEC),
        Paragraph(f"• {_safe(doc.lesson_title)}" if doc.lesson_title else "•", BULL),
        Spacer(1, 4),
    ]))

    # 2. Lesson Objectives
    story.append(KeepTogether([
        Paragraph("2. LESSON OBJECTIVES", SEC),
        Paragraph("At the end of the lesson, participants are expected to:", N),
        *_bullets(doc.lesson_objectives, fallback=""),
        Spacer(1, 4),
    ]))

    # 3. Prior Knowledge
    story.append(KeepTogether([
        Paragraph("3. PRIOR KNOWLEDGE", SEC),
        *_bullets(doc.prior_knowledge, fallback="NIL."),
        Spacer(1, 4),
    ]))

    # 4. Lesson Information
    story.append(KeepTogether([
        Paragraph("4. LESSON INFORMATION", SEC),
        _build_section4(doc, total_minutes),
        Spacer(1, 4),
    ]))

    # 5. Equipment & Logistics
    story.append(KeepTogether([
        Paragraph("5. EQUIPMENT & LOGISTICS", SEC),
        _build_section5(doc),
        Spacer(1, 4),
    ]))

    # 6. Method of Instruction
    story.append(KeepTogether([
        Paragraph("6. METHOD OF INSTRUCTION", SEC),
        _build_section6(doc),
        Spacer(1, 4),
    ]))

    # 7. Training Personnel
    story.append(KeepTogether([
        Paragraph("7. TRAINING PERSONNEL", SEC),
        _build_section7(doc),
        Spacer(1, 4),
    ]))

    # 8. Safety Precautions
    story.append(KeepTogether([
        Paragraph("8. SAFETY PRECAUTIONS", SEC),
        *_bullets(doc.safety_precautions, fallback=""),
        Spacer(1, 4),
    ]))

    # 9. Contingency Plans
    story.append(KeepTogether([
        Paragraph("9. CONTINGENCY PLANS", SEC),
        *_bullets(doc.contingency_plans, fallback="NIL."),
        Spacer(1, 4),
    ]))

    # 10. Authentication
    story.append(KeepTogether([
        Paragraph("10. AUTHENTICATION", SEC),
        Paragraph(f"• Prepared by: {_safe(doc.prepared_by)}", AUTH),
        Paragraph(f"• Vetted by: {_safe(doc.vetted_by)}", AUTH),
        Paragraph(f"• Date: {_safe(doc.date_text)}", AUTH),
    ]))

    pdf.build(story)
    return buf.getvalue()