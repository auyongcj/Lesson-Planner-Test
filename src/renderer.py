from __future__ import annotations

from jinja2 import Template
from .schema import ScheduleDoc
import re


_NAME_TOKEN = re.compile(r"^[A-Za-z][A-Za-z'\-]*$")

def _is_name_token(tok: str) -> bool:
    if "(" in tok or ")" in tok:
        return False
    return bool(_NAME_TOKEN.match(tok))


def _format_ic_text(ic: str) -> str:
    """
    Format IC so each token is on a new line, except the final name
    which is kept as 1–2 tokens (e.g., 'Tom Tan').

    Parentheses tokens like '(NPCC)' are never treated as part of the name.
    """
    if not ic:
        return ""

    parts = ic.strip().split()
    if not parts:
        return ""

    # Collect up to 2 name tokens from the end
    name_tokens = []
    i = len(parts) - 1
    while i >= 0 and len(name_tokens) < 2 and _is_name_token(parts[i]):
        name_tokens.append(parts[i])
        i -= 1
    name_tokens.reverse()

    prefix = parts[: i + 1]  # everything before the name
    lines = prefix[:]        # each token becomes its own line

    if name_tokens:
        lines.append(" ".join(name_tokens))

    return "\n".join(lines)

_HTML = Template(
    """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <style>
    body {
      font-family: Arial, Helvetica, sans-serif;
      font-size: 12px;
      color: #111;
      background: #fff;
    }

    .page {
      width: 620px;
      margin: 0 auto;
      padding: 14px 8px;
    }

    .center {
      text-align: center;
    }

    .title {
      font-weight: bold;
      text-decoration: underline;
      margin-bottom: 2px;
    }
vertical-align: top;
    .subtitle {
      margin-top: 2px;
    }

    /* TABLE: match your document style
       - Outer border only
       - Vertical dividers in body
       - One header separator line
       - No horizontal lines between body rows
    */
    td.ic {
    white-space: pre-line;  /* respects \n */
    text-align: center;
    vertical-align: top;
    }

    table {
    width: 100%;
    margin-top: 18px;
    table-layout: fixed;

    /* ONLY vertical outer borders */
    border-left: 2px solid #000;
    border-right: 2px solid #000;

    border-collapse: separate;
    border-spacing: 0;
    }

    th, td {
    white-space: normal;      /* allow wrapping */
    overflow-wrap: normal;    /* do NOT break long words */
    word-break: normal;       /* do NOT break words */
    hyphens: none;            /* no auto-hyphenation */
    vertical-align: top; 
    }

    thead th {
      text-align: center;
      font-weight: bold;

      /* vertical dividers */
      border-right: 1px solid #000;

      /* header separator only */
      border-bottom: 2px solid #000;

      /* no extra top border */
      border-top: 0;
    }

    thead th:last-child {
      border-right: 0; /* outer border handled by table */
    }

    tbody td {
      text-align: center;
      vertical-align: top;

      /* vertical dividers only */
      border-right: 1px solid #000;
      padding-top: 10px;
      padding-bottom: 10px;
      /* ensure no horizontal borders */
      border-top: 0;
      border-bottom: 0;
    }

    tbody td:last-child {
      border-right: 0; /* outer border handled by table */
    }

    td.remarks {
      text-align: center;
      white-space: pre-wrap;
      word-wrap: break-word;
      padding-left: 2px;
      padding-right: 2px;
    }

    /* Column widths tuned closer to your template */
    col.time { width: 13%; }
    col.activity { width: 24%; }
    col.venue { width: 13%; }
    col.ic { width: 18%; }
    col.attire { width: 12%; }
    col.remarks { width: 20%; }

    .notes {
      margin-top: 26px;
    }

    .notes-title {
      font-weight: bold;
    }

    /* Keep the list compact */
    ol {
      margin: 6px 0 0 18px;
      padding: 0;
    }

    .signoff{
    margin-top: 26px;
    display: flex;
    flex-direction: column;
    align-items: flex-end;  /* whole block sits on the right */
    gap: 0;                 /* no vertical gap */
    line-height: 1.1;
    }

    .signoff-row{
    display: grid;
    grid-template-columns: 140px 160px; /* label | value (reserve space) */
    column-gap: 8px;
    justify-content: end;               /* row is right-aligned */
    }

    .signoff-row .label{
    text-align: right;
    }

    .signoff-row .value{
    text-align: left;
    white-space: nowrap;
  </style>
</head>

<body>
  <div class="page">
    <div class="center">
      <div class="title">{{ doc.programme_title }}</div>
      <div class="subtitle"><b>{{ doc.unit_title }}</b></div>
      <div class="subtitle">{{ doc.programme_title }} {{ doc.programme_date_line }}</div>
    </div>

    <table>
      <colgroup>
        <col class="time" />
        <col class="activity" />
        <col class="venue" />
        <col class="ic" />
        <col class="attire" />
        <col class="remarks" />
      </colgroup>

      <thead>
        <tr>
          <th>Time</th>
          <th>Activity</th>
          <th>Venue</th>
          <th>IC</th>
          <th>Attire</th>
          <th>Remarks</th>
        </tr>
      </thead>

      <tbody>
        {% for r in doc.rows %}
        <tr>
          <td>{{ r.time }}</td>
          <td>{{ r.activity }}</td>
          <td>{{ r.venue }}</td>
          <td class="ic">{{ format_ic(r.ic) }}</td>
          <td>{{ r.attire }}</td>
          <td class="remarks">{{ r.remarks }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>

    <div class="notes">
      <div class="notes-title">Notes:</div>
      <ol>
        {% for n in doc.notes %}
          <li>{{ n }}</li>
        {% endfor %}
      </ol>
    </div>

    <div class="signoff">
        <div class="signoff-row">
            <span class="label">Authenticated by:</span>
            <span class="value">{{ (doc.authenticated_by if doc.authenticated_by else '&nbsp;')|safe }}</span>
        </div>
        <div class="signoff-row">
            <span class="label">Vetted by:</span>
            <span class="value">{{ (doc.vetted_by if doc.vetted_by else '&nbsp;')|safe }}</span>
        </div>
        </div>
  </div>
</body>
</html>
"""
)

def render_html(doc: ScheduleDoc) -> str:
    return _HTML.render(doc=doc, format_ic=_format_ic_text)