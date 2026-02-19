from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as components

from src.schema import ScheduleDoc, ScheduleRow
from src.renderer import render_html

from datetime import date
from src.lesson_schema import LessonPlanDoc, LessonInfoRow, LogisticsRow, MethodRow, PersonnelRow, RemarkItem, RemarksBlock
from src.lesson_renderer import render_lesson_html
from datetime import date
from io import BytesIO
from src.render_lesson_pdf import render_lesson_pdf

st.set_page_config(page_title="Training Programme Builder", layout="wide")
st.markdown("""
<style>
/* Allow sticky to work inside streamlit columns */
[data-testid="stHorizontalBlock"] {
    align-items: flex-start !important;
}

[data-testid="stHorizontalBlock"] > [data-testid="stColumn"]:nth-child(2) {
    position: sticky;
    top: 3.5rem;
    max-height: calc(100vh - 4rem);
    overflow-y: auto;
}

/* Keep your existing preview-sticky class too */
.preview-sticky {
    position: sticky;
    top: 1rem;
    align-self: flex-start;
}
</style>
""", unsafe_allow_html=True)


def _init_state():
    if "doc" not in st.session_state:
        st.session_state.doc = ScheduleDoc(
            unit_title="(S2 SQUAD)",
            programme_title="Training Programme",
            programme_date_line="",  # will be set by date selector below
            rows=[
                ScheduleRow(
                    time="",                      # empty
                    activity="Administrative Matters",
                    venue="",                     # empty
                    ic="",                        # empty
                    attire="",                    # empty
                    remarks=""                    # empty
                )
            ],
            notes=[],  # start empty
            authenticated_by="",
            vetted_by="",
        )

    # store selected date once (only on first run)
    if "programme_date" not in st.session_state:
        st.session_state.programme_date = date.today()

def _init_lesson_state():
    if "lesson" not in st.session_state:
        st.session_state.lesson = LessonPlanDoc(
        lesson_title="",
        lesson_objectives=[],
        prior_knowledge=[],
        lesson_info_rows=[LessonInfoRow(stage="1", activity="", time_minutes="")],
        attire="",
        targeted_participants="",
        location="",
        logistics_rows=[],
        training_personnel_line="",
        method_rows=[MethodRow(stage="1", activity="")],
        personnel_rows=[],
        safety_precautions=[],
        contingency_plans=[],
        prepared_by="",
        vetted_by="",
        date_text="",
        )


def _move_row(idx: int, direction: int):
    doc: ScheduleDoc = st.session_state.doc
    new_idx = idx + direction
    if 0 <= idx < len(doc.rows) and 0 <= new_idx < len(doc.rows):
        doc.rows[idx], doc.rows[new_idx] = doc.rows[new_idx], doc.rows[idx]


def _delete_row(idx: int):
    doc: ScheduleDoc = st.session_state.doc
    if 0 <= idx < len(doc.rows):
        doc.rows.pop(idx)


_init_state()
doc: ScheduleDoc = st.session_state.doc

st.title("Training Programme Builder")

tab1, tab2 = st.tabs(["📅 Training Programme", "📘 Lesson Plan"])

with tab1:
    left, right = st.columns([0.48, 0.52], gap="large")

    with left:
        st.subheader("Document fields")

        doc.unit_title = st.text_input("Unit line", value=doc.unit_title)
        doc.programme_title = st.text_input("Programme title", value=doc.programme_title)
        selected = st.date_input(
        "Programme date",
        value=st.session_state.programme_date
        )
        st.session_state.programme_date = selected

        # Format like your sample: "for 20th February 2026, Friday"
        def _ordinal(n: int) -> str:
            if 11 <= (n % 100) <= 13:
                return f"{n}th"
            return f"{n}{ {1:'st',2:'nd',3:'rd'}.get(n % 10, 'th') }"

        doc.programme_date_line = f"for {_ordinal(selected.day)} {selected.strftime('%B %Y')}, {selected.strftime('%A')}"

        st.divider()
        st.subheader("Schedule rows")

        if st.button("➕ Add row"):
            doc.rows.append(ScheduleRow())
            st.rerun()

        for i, r in enumerate(doc.rows):
            row_key = f"row_{r.id}"  # stable per-row key prefix

            with st.expander(
                f"Row {i+1}: {r.time or '(no time)'} | {r.activity or '(no activity)'}",
                expanded=False
            ):
                c1, c2 = st.columns(2)
                with c1:
                    r.time = st.text_input("Time", value=r.time, key=f"{row_key}_time")
                    r.activity = st.text_input("Activity", value=r.activity, key=f"{row_key}_activity")
                    r.venue = st.text_input("Venue", value=r.venue, key=f"{row_key}_venue")
                with c2:
                    r.ic = st.text_input("IC", value=r.ic, key=f"{row_key}_ic")
                    r.attire = st.text_input("Attire", value=r.attire, key=f"{row_key}_attire")
                    r.remarks = st.text_area("Remarks", value=r.remarks, key=f"{row_key}_remarks", height=100)

                b1, b2, b3 = st.columns([1, 1, 2])
                with b1:
                    if st.button("⬆️ Move up", key=f"up_{i}"):
                        _move_row(i, -1)
                        st.rerun()
                with b2:
                    if st.button("⬇️ Move down", key=f"down_{i}"):
                        _move_row(i, 1)
                        st.rerun()
                with b3:
                    if st.button("🗑️ Delete row", key=f"del_{i}"):
                        _delete_row(i)
                        st.rerun()

        st.divider()
        st.subheader("Notes")

        notes_text = st.text_area(
            "One note per line",
            value="\n".join(doc.notes),
            height=120
        )
        doc.notes = [line.strip() for line in notes_text.splitlines() if line.strip()]

        st.divider()
        st.subheader("Sign-off")
        doc.authenticated_by = st.text_input("Authenticated by", value=doc.authenticated_by, key="tp_authenticated_by")
        doc.vetted_by = st.text_input("Vetted by", value=doc.vetted_by, key="tp_vetted_by")
        st.divider()

        st.subheader("Export")

        
                

    with right:
        st.subheader("Live preview")
        html = render_html(doc)
        components.html(html, height=900, scrolling=True)



with tab2:
    _init_lesson_state()
    lesson: LessonPlanDoc = st.session_state.lesson
    for mr in lesson.method_rows:
        if isinstance(mr.remarks, str):
            mr.remarks = RemarksBlock(lead=mr.remarks)
        elif mr.remarks is None:
            mr.remarks = RemarksBlock()
    left2, right2 = st.columns([0.48, 0.52], gap="large")

    with left2:
        st.subheader("Lesson Plan fields")

        with st.container():
            st.markdown("**1. LESSON TITLE**")
            lesson.lesson_title = st.text_input("Lesson Title", value=lesson.lesson_title, key="lp_title")

            st.markdown("**2. LESSON OBJECTIVES**")
            st.caption("At the end of the lesson, participants are expected to:")

            
            obj_text = st.text_area(
                "Objectives (one per line)",
                value="\n".join(lesson.lesson_objectives),
                height=90,
                key="lp_obj_textarea_unique_1",
            )
            lesson.lesson_objectives = [x.strip() for x in obj_text.splitlines() if x.strip()]

            st.markdown("**3. PRIOR KNOWLEDGE**")

           

            pk_text = st.text_area(
                "Prior Knowledge (one per line)",
                value="\n".join(lesson.prior_knowledge),
                height=70,
                key="lp_pk_textarea_unique_1",
            )
            lesson.prior_knowledge = [x.strip() for x in pk_text.splitlines() if x.strip()]


            st.divider()
            st.subheader("4. Lesson Information")

            if st.button("➕ Add Lesson Info Row"):
                lesson.lesson_info_rows.append(LessonInfoRow(stage=str(len(lesson.lesson_info_rows)+1)))

            for i, r in enumerate(lesson.lesson_info_rows):
                with st.expander(f"Lesson Info Row {i+1}", expanded=(i == 0)):
                    r.stage = st.text_input("Stage", r.stage, key=f"li_stage_{i}")
                    r.activity = st.text_input("Activity", r.activity, key=f"li_act_{i}")
                    r.time_minutes = st.text_input("Time (Minutes)", r.time_minutes, key=f"li_time_{i}")

            lesson.attire = st.text_input("Attire", value=lesson.attire, key="lp_attire")
            lesson.targeted_participants = st.text_input("Targeted Participants", value=lesson.targeted_participants, key="lp_targets")
            lesson.location = st.text_input("Location", value=lesson.location, key="lp_location")

            st.divider()
            st.subheader("5. Equipment & Logistics")

            if st.button("➕ Add Logistics Row"):
                lesson.logistics_rows.append(LogisticsRow())

            for i, r in enumerate(lesson.logistics_rows):
                with st.expander(f"Logistics Row {i+1}", expanded=False):
                    r.logistics = st.text_input("Logistics", r.logistics, key=f"log_item_{i}")
                    r.quantity = st.text_input("Quantity", r.quantity, key=f"log_qty_{i}")
                    r.remarks = st.text_area("Remarks", r.remarks, key=f"log_rem_{i}", height=80)

            st.divider()
            st.subheader("6. Method of Instruction")

            lesson.training_personnel_line = st.text_input("Training personnel line", value=lesson.training_personnel_line)

            if st.button("➕ Add Method Row"):
                lesson.method_rows.append(MethodRow(stage=str(len(lesson.method_rows)+1)))

            for i, r in enumerate(lesson.method_rows):
                with st.expander(f"Method Row {i+1}", expanded=(i == 0)):
                    r.stage = st.text_input("Stage", r.stage, key=f"m_stage_{i}")
                    r.activity = st.text_input("Activity", r.activity, key=f"m_act_{i}")
                    st.markdown("**Remarks**")
                    r.remarks.lead = st.text_input(
                        "Lead line (optional)",
                        value=r.remarks.lead,
                        key=f"m_lead_{i}",
                    )

                    style_options = ["bullet", "number", "roman"]
                    r.remarks.style = st.selectbox(
                        "List style",
                        style_options,
                        index=style_options.index(r.remarks.style),
                        key=f"m_style_{i}",
                    )

                    if st.button("➕ Add point", key=f"m_add_point_{i}"):
                        r.remarks.items.append(RemarkItem())
                        st.rerun()

                    for j, item in enumerate(r.remarks.items):
                        cols = st.columns([0.92, 0.08])
                        with cols[0]:
                            item.text = st.text_input("Point", value=item.text, key=f"m_point_{i}_{j}")
                        with cols[1]:
                            if st.button("✖", key=f"m_del_point_{i}_{j}"):
                                r.remarks.items.pop(j)
                                st.rerun()

                        with st.expander("Sub-points (optional)", expanded=False):
                            if st.button("➕ Add sub-point", key=f"m_add_sub_{i}_{j}"):
                                item.subitems.append("")
                                st.rerun()

                            for k in range(len(item.subitems)):
                                item.subitems[k] = st.text_input(
                                    f"Sub-point {k+1}",
                                    value=item.subitems[k],
                                    key=f"m_sub_{i}_{j}_{k}",
                                )

            st.divider()
            st.subheader("7. Training Personnel")

            if st.button("➕ Add Personnel Row"):
                lesson.personnel_rows.append(PersonnelRow())

            for i, r in enumerate(lesson.personnel_rows):
                with st.expander(f"Personnel Row {i+1}", expanded=False):
                    r.role = st.text_input("Role", r.role, key=f"p_role_{i}")
                    r.names = st.text_input("Name(s)", r.names, key=f"p_names_{i}")
                    r.remarks = st.text_area("Remarks", r.remarks, key=f"p_rem_{i}", height=90)

            st.divider()
            st.subheader("8–10")

            sp_text = st.text_area("Safety Precautions (one per line)", value="\n".join(lesson.safety_precautions), height=80)
            lesson.safety_precautions = [x.strip() for x in sp_text.splitlines() if x.strip()]

            cp_text = st.text_area("Contingency Plans (one per line)", value="\n".join(lesson.contingency_plans), height=70)
            lesson.contingency_plans = [x.strip() for x in cp_text.splitlines() if x.strip()]

            lesson.prepared_by = st.text_input("Prepared by", value=lesson.prepared_by, key="lp_prepared_by")
            lesson.vetted_by = st.text_input("Vetted by", value=lesson.vetted_by, key="lp_vetted_by")
            lesson.date_text = st.text_input("Date", value=lesson.date_text, key="lp_date")

    with right2:


        st.subheader("Export")

        if st.button("📄 Generate PDF", key="lp_gen_pdf"):
            st.session_state["lesson_pdf_bytes"] = render_lesson_pdf(lesson)

        if "lesson_pdf_bytes" in st.session_state:
            st.download_button(
                label="⬇️ Save lesson_plan.pdf",
                data=st.session_state["lesson_pdf_bytes"],
                file_name="lesson_plan.pdf",
                mime="application/pdf",
                key="lp_save_pdf",
            )



            
        lesson_html = render_lesson_html(lesson)
        components.html(lesson_html, height=900, scrolling=True)

        