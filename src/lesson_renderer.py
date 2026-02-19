from __future__ import annotations

from jinja2 import Template
from .lesson_schema import LessonPlanDoc


def remarks_block_to_html(rb) -> str:
    """
    Convert RemarksBlock into HTML lists (safe, controlled formatting).
    """
    if rb is None:
        return ""

    parts: list[str] = []

    lead = (rb.lead or "").strip()
    if lead:
        parts.append(f"<div>{lead}</div>")

    items = getattr(rb, "items", None) or []
    style = getattr(rb, "style", "bullet") or "bullet"

    if not items:
        return "".join(parts)

    if style == "number":
        parts.append("<ol>")
    elif style == "roman":
        parts.append("<ol type='i'>")
    else:
        parts.append("<ul>")

    for it in items:
        text = (getattr(it, "text", "") or "").strip()
        parts.append(f"<li>{text if text else '&nbsp;'}</li>")

        subitems = getattr(it, "subitems", None) or []
        if subitems:
            parts.append("<ol type='i'>")
            for sub in subitems:
                s = (sub or "").strip()
                parts.append(f"<li>{s if s else '&nbsp;'}</li>")
            parts.append("</ol>")

    parts.append("</ol>" if style in ("number", "roman") else "</ul>")
    return "".join(parts)

_HTML = Template(
    r"""
<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<style>
@media print {
@page {
    margin: 1cm;
  }
  thead th, .kv .k {
    background: #cfcfcf !important;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }
}
  body{
    font-family: Arial, Helvetica, sans-serif;
    font-size: 12px;
    color:#111;
    background:#fff;
  }

  .page{
    width: 640px;
    margin: 0 auto;
    padding: 18px 18px 10px;
  }

  .sec-title{
    font-weight: 700;
    margin: 10px 0 2px;
  }
  .sec-title:first-child{ margin-top: 0; }

  ul{
    margin: 2px 0 8px 28px;
    padding: 0;
  }
  li{ margin: 2px 0; }

  /* Tables */
  table{
    width: 100%;
    border-collapse: collapse;
    table-layout: fixed;
    margin-top: 6px;
  }

  th, td{
    border: 1.4px solid #4b4b4b;
    padding: 0;                 /* IMPORTANT: padding goes to .cell */
    vertical-align: middle;
    background: #fff;
  }

  /* Header grey like the sample */
  thead th{
    background: #cfcfcf !important;
    font-weight: 700;
    text-align: center;
    vertical-align: middle;
    padding: 6px 8px;
  }

  /* Cell wrapper controls baseline row height consistently */
  .cell{
    padding: 7px 8px;           /* baseline spacing (Attire-like) */
    min-height: 32px;           /* baseline row height */
    box-sizing: border-box;

    /* wrap by whole words */
    white-space: normal;
    overflow-wrap: normal;
    word-break: normal;
    hyphens: none;
  }

  /* Alignment helpers */
  .c-center{ text-align: center; }
  .c-left{ text-align: left; }
  .c-right{ text-align: right; }

  /* Stage cell: centered vertically + horizontally */
  .stage-cell{
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 32px;           /* keep baseline */
    padding: 7px 8px;
    box-sizing: border-box;
  }

  /* 4. LESSON INFORMATION ratios */
  .t-lesson-info col.stage { width: 18%; }
  .t-lesson-info col.activity { width: 62%; }
  .t-lesson-info col.time { width: 20%; }

  .total-cell{
    font-weight: 700;
  }
  .total-row .cell{
    min-height: 28px;           /* total row slightly tighter like Word */
    padding-top: 6px;
    padding-bottom: 6px;
  }

  /* Attire/Targeted/Location block (values are bold in your sample) */
  .kv{
    margin-top: 0;
  }
  .kv .k{
    width: 22%;
    font-weight: 700;
    text-align: center;
    vertical-align: middle;
  }
  .kv .v{
    width: 78%;
    font-weight: 700;
  }

  /* 5. Equipment & Logistics ratios */
  .t-logistics col.log { width: 22%; }
  .t-logistics col.rem { width: 58%; }
  .t-logistics col.qty { width: 20%; }

  /* 6. Method of instruction top bar row */
  .method-top th{
    background: #cfcfcf !important;
    font-weight: 700;
    text-align: center;
    vertical-align: middle;
    padding: 7px 8px;
  }

  .t-method col.stage { width: 12%; }
  .t-method col.activity { width: 28%; }
  .t-method col.remarks { width: 60%; }

  .method-remarks{
    white-space: pre-line; /* keep user bullets/newlines */
  }
  
  .method-remarks ul,
    .method-remarks ol{
    margin: 4px 0 0 18px;
    padding: 0;
    }
    .method-remarks li{
    margin: 2px 0;
  }

  /* 7. Training personnel ratios */
  .t-personnel col.role { width: 22%; }
  .t-personnel col.names { width: 28%; }
  .t-personnel col.rem { width: 50%; }

  .auth ul{ margin-left: 44px; }
   @media print {
   @page {
    margin: 1cm;
  }
    thead th {
      background: #cfcfcf !important;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }
  }
</style>
</head>

<body>
<div class="page">

  <div class="sec-title">1. LESSON TITLE</div>
  <ul>
    {% if doc.lesson_title %}
      <li>{{ doc.lesson_title }}</li>
    {% else %}
      <li>&nbsp;</li>
    {% endif %}
  </ul>

  <div class="sec-title">2. LESSON OBJECTIVES</div>
  <div>At the end of the lesson, participants are expected to:</div>
  <ul>
    {% for x in doc.lesson_objectives %}
      <li>{{ x }}</li>
    {% endfor %}
    {% if doc.lesson_objectives|length == 0 %}
      <li>&nbsp;</li>
    {% endif %}
  </ul>

  <div class="sec-title">3. PRIOR KNOWLEDGE</div>
  <ul>
    {% for x in doc.prior_knowledge %}
      <li>{{ x }}</li>
    {% endfor %}
    {% if doc.prior_knowledge|length == 0 %}
      <li>NIL.</li>
    {% endif %}
  </ul>

  <div class="sec-title">4. LESSON INFORMATION</div>

  <table class="t-lesson-info">
    <colgroup>
      <col class="stage" />
      <col class="activity" />
      <col class="time" />
    </colgroup>
    <thead>
      <tr>
        <th>Stage</th>
        <th>Activity</th>
        <th>Time (Minutes)</th>
      </tr>
    </thead>
    <tbody>
      {% for r in doc.lesson_info_rows %}
      <tr>
        <td><div class="stage-cell">{{ r.stage }}</div></td>
        <td><div class="cell c-center">{{ r.activity }}</div></td>
        <td><div class="cell c-center">{{ r.time_minutes }}</div></td>
      </tr>
      {% endfor %}
      {% if doc.lesson_info_rows|length == 0 %}
      <tr>
        <td><div class="stage-cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
      </tr>
      {% endif %}

      <tr class="total-row">
        <td colspan="2"><div class="cell c-right total-cell">Total</div></td>
        <td><div class="cell c-center total-cell">{{ total_minutes }}</div></td>
      </tr>
    </tbody>
  </table>

  <table class="kv">
    <tbody>
      <tr>
        <td class="k"><div class="cell c-center">Attire</div></td>
        <td class="v"><div class="cell">{{ doc.attire }}</div></td>
      </tr>
      <tr>
        <td class="k"><div class="cell c-center">Targeted<br/>Participants</div></td>
        <td class="v"><div class="cell">{{ doc.targeted_participants }}</div></td>
      </tr>
      <tr>
        <td class="k"><div class="cell c-center">Location</div></td>
        <td class="v"><div class="cell">{{ doc.location }}</div></td>
      </tr>
    </tbody>
  </table>

  <div class="sec-title">5. EQUIPMENT &amp; LOGISTICS</div>

  <table class="t-logistics">
    <colgroup>
      <col class="log" />
      <col class="rem" />
      <col class="qty" />
    </colgroup>
    <thead>
      <tr>
        <th>Logistics</th>
        <th>Remarks</th>
        <th>Quantity</th>
      </tr>
    </thead>
    <tbody>
      {% for r in doc.logistics_rows %}
      <tr>
        <td><div class="cell c-center">{{ r.logistics }}</div></td>
        <td><div class="cell c-center">{{ r.remarks }}</div></td>
        <td><div class="cell c-center">{{ r.quantity }}</div></td>
      </tr>
      {% endfor %}
      {% if doc.logistics_rows|length == 0 %}
      <tr>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
      </tr>
      {% endif %}
    </tbody>
  </table>

  <div class="sec-title">6. METHOD OF INSTRUCTION</div>

  <table class="t-method">
    <colgroup>
        <col class="stage" />
        <col class="activity" />
        <col class="remarks" />
    </colgroup>

    <thead>
        <tr class="method-top">
            <th colspan="2">TRAINING PERSONNEL:</th>
            <th>{{ doc.training_personnel_line }}</th>
        </tr>

        <tr>
        <th>Stage</th>
        <th>Activity</th>
        <th>Remarks</th>
        </tr>
    </thead>

    <tbody>
        {% for r in doc.method_rows %}
        <tr>
        <td><div class="stage-cell">{{ r.stage }}</div></td>
        <td><div class="cell c-center">{{ r.activity }}</div></td>
        <td><div class="cell c-left method-remarks">{{ remarks_html(r.remarks) | safe }}</div></td>
        </tr>
        {% endfor %}
        {% if doc.method_rows|length == 0 %}
        <tr>
        <td><div class="stage-cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
        </tr>
        {% endif %}
    </tbody>
  </table>


  <div class="sec-title">7. TRAINING PERSONNEL</div>

  <table class="t-personnel">
    <colgroup>
      <col class="role" />
      <col class="names" />
      <col class="rem" />
    </colgroup>
    <thead>
      <tr>
        <th>Roles</th>
        <th>Name(s) of personnel</th>
        <th>Remarks</th>
      </tr>
    </thead>
    <tbody>
      {% for r in doc.personnel_rows %}
      <tr>
        <td><div class="cell c-left">{{ r.role }}</div></td>
        <td><div class="cell c-left">{{ r.names }}</div></td>
        <td><div class="cell c-left">{{ r.remarks }}</div></td>
      </tr>
      {% endfor %}
      {% if doc.personnel_rows|length == 0 %}
      <tr>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
        <td><div class="cell">&nbsp;</div></td>
      </tr>
      {% endif %}
    </tbody>
  </table>

  <div class="sec-title">8. SAFETY PRECAUTIONS</div>
  <ul>
    {% for x in doc.safety_precautions %}
      <li>{{ x }}</li>
    {% endfor %}
    {% if doc.safety_precautions|length == 0 %}
      <li>&nbsp;</li>
    {% endif %}
  </ul>

  <div class="sec-title">9. CONTINGENCY PLANS</div>
  <ul>
    {% for x in doc.contingency_plans %}
      <li>{{ x }}</li>
    {% endfor %}
    {% if doc.contingency_plans|length == 0 %}
      <li>NIL.</li>
    {% endif %}
  </ul>

  <div class="sec-title">10. AUTHENTICATION</div>
  <div class="auth">
    <ul>
      <li>Prepared by: {{ doc.prepared_by }}</li>
      <li>Vetted by: {{ doc.vetted_by }}</li>
      <li>Date: {{ doc.date_text }}</li>
    </ul>
  </div>

</div>
</body>
</html>
"""
)

def _sum_minutes(rows) -> str:
    total = 0
    for r in rows:
        txt = (r.time_minutes or "")
        digits = ""
        for ch in txt:
            if ch.isdigit():
                digits += ch
            elif digits:
                break
        if digits:
            total += int(digits)
    return f"{total} MINUTES" if total else ""


def render_lesson_html(doc: LessonPlanDoc) -> str:
    return _HTML.render(
        doc=doc,
        total_minutes=_sum_minutes(doc.lesson_info_rows),
        remarks_html=remarks_block_to_html,
    )