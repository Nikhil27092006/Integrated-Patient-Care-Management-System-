import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db
import plotly.graph_objects as go
from datetime import date, time, timedelta
from pages.shared_styles import (inject_css, sidebar_header, page_header,
                                  stat_cards, status_badge, PLOTLY_LAYOUT, sidebar_footer)
import ai_care

def _weekly_calendar(appts: list, week_start: date):
    """Render a 6-day (Mon-Sat) calendar card."""
    week_days = [week_start + timedelta(days=i) for i in range(6)]
    today     = date.today()
    cal = {str(d): [] for d in week_days}
    for a in appts:
        ds = str(a["scheduled_date"])
        if ds in cal:
            cal[ds].append(a)

    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    cols = st.columns(6)
    for i, (d, col) in enumerate(zip(week_days, cols)):
        is_today     = (d == today)
        header_color = "#0ea5e9" if is_today else "#6b7280"
        border       = "rgba(14,165,233,0.6)" if is_today else "rgba(14,165,233,0.12)"
        bg           = "rgba(14,165,233,0.07)" if is_today else "rgba(10,22,40,0.5)"

        events_html = ""
        for a in cal[str(d)]:
            s_color = {"confirmed":"#14b8a6","pending":"#f59e0b",
                       "completed":"#10b981","cancelled":"#ef4444"}.get(
                           a.get("status","pending"), "#9ca3af")
            events_html += f"""
            <div class="cal-event" style="border-left-color: {s_color};">
                <b>{str(a['start_time'])[:5]}</b><br>
                {a['patient_name']}<br>
                <span style="opacity:0.7">{a.get('reason','') or ''}</span>
            </div>"""

        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {border};border-radius:14px;
                        padding:0.7rem 0.6rem;min-height:140px;">
                <div style="font-size:0.7rem;font-weight:700;color:{header_color};
                            text-transform:uppercase;margin-bottom:3px;">{day_names[i]}</div>
                <div style="font-size:0.9rem;font-weight:600;color:#e2e8f0;margin-bottom:8px;">
                    {d.strftime('%d')} <span style="font-size:0.65rem;color:#9ca3af;">{d.strftime('%b')}</span>
                </div>
                {events_html if events_html else '<div style="font-size:0.68rem;color:#374151;margin-top:4px;">—</div>'}
            </div>
            """, unsafe_allow_html=True)


def render():
    inject_css()
    user = st.session_state.user_data
    sidebar_header("Doctor", user["name"])

    PAGES = {
        "Dashboard":     "home",
        "Appointments":  "appointments",
        "My Patients":   "patients",
        "Health Records": "records",
        "Prescribe":     "prescribe",
        "💊 Medicines":  "medicines",
        "🤖 AI Care":    "ai_care",
        "My Profile":    "profile",
    }
    if "doctor_page" not in st.session_state:
        st.session_state.doctor_page = "home"

    with st.sidebar:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── Live notification badge: pending appointments ──────────────
        doc_profile_pre = db.fetch_doctor_by_user_id(user["id"])
        doc_id_pre = doc_profile_pre["id"] if doc_profile_pre else None
        if doc_id_pre:
            pending_appts = [a for a in db.fetch_appointments(doctor_id=doc_id_pre)
                             if (a["status"] or "pending") == "pending"]
            if pending_appts:
                st.markdown(f"""
                <div class="notification-toast" style="color: #f59e0b; border-color: rgba(245,158,11,0.35);
                            background: linear-gradient(135deg, rgba(245,158,11,0.15), rgba(251,191,36,0.1));">
                    🔔 {len(pending_appts)} new appointment request(s) awaiting confirmation
                </div>
                """, unsafe_allow_html=True)

        for label, key in PAGES.items():
            is_active = (st.session_state.doctor_page == key)
            kind = "primary" if is_active else "secondary"
            if st.button(label, key=f"dnav_{key}", use_container_width=True, type=kind):
                st.session_state.doctor_page = key
                st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)
        if st.button("↩  Log out", key="doc_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        sidebar_footer()

    doc_profile = db.fetch_doctor_by_user_id(user["id"])
    doctor_id   = doc_profile["id"] if doc_profile else None
    page        = st.session_state.doctor_page

    # ════════════════════════════════════════════════════════════════════
    # HOME / DOCTOR PORTAL
    # ════════════════════════════════════════════════════════════════════
    if page == "home":
        specialty = doc_profile["specialty_name"] if doc_profile and doc_profile.get("specialty_name") else "General Practitioner"
        exp       = doc_profile["experience_years"] if doc_profile else 0

        # Animated medical header
        st.markdown("""
        <div style="display: flex; align-items: center; justify-content: center; gap: 20px; margin-bottom: 10px; flex-wrap: wrap;">
            <span class="stethoscope-icon" style="font-size: 2rem;">🩺</span>
            <span class="heart-pulse" style="font-size: 2rem;"></span>
            <span class="medical-cross" style="font-size: 1.8rem;">➕</span>
            <span class="dna-animation" style="font-size: 1.5rem;">
                <span></span><span></span><span></span><span></span><span></span>
            </span>
            <span class="hospital-glow" style="font-size: 1.8rem;">🏥</span>
        </div>
        """, unsafe_allow_html=True)

        page_header(f"Dr. {user['name']}", f"{specialty}  ·  {exp} yrs experience")

        all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []
        upcoming  = [a for a in all_appts if str(a["scheduled_date"]) >= str(date.today())]
        completed = [a for a in all_appts if a["status"] == "completed"]
        pending   = [a for a in all_appts if (a["status"] or "pending") == "pending"]
        patients  = {a["patient_id"] for a in all_appts}

        stat_cards([
            ("A", "Total Appointments", str(len(all_appts))),
            ("U", "Upcoming",           str(len(upcoming))),
            ("C", "Completed",          str(len(completed))),
            ("P", "Unique Patients",    str(len(patients))),
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Pending confirmation requests (NEW) ────────────────────────
        if pending:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(245,158,11,0.12), rgba(251,191,36,0.08));
                        border: 1px solid rgba(245,158,11,0.3);
                        border-radius: 14px; padding: 1rem 1.4rem; margin-bottom: 1.2rem;
                        box-shadow: 0 4px 16px rgba(245,158,11,0.15);">
                <div style="font-weight:700;color:#f59e0b; font-size: 0.95rem; display: flex; align-items: center; gap: 8px;">
                    🔔 Appointment Requests Awaiting Confirmation
                </div>
            </div>
            """, unsafe_allow_html=True)
            for a in pending:
                col_l, col_c, col_r = st.columns([4, 1, 1])
                with col_l:
                    # Show patient ID and contact info for better interconnection
                    patient_email = a.get('patient_email', '')
                    patient_phone = a.get('patient_phone', '')
                    contact_info = f"📧 {patient_email}" if patient_email else ""
                    if patient_phone:
                        contact_info += f" | 📞 {patient_phone}"
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(10,22,40,0.7), rgba(15,30,60,0.6));
                                border: 1px solid rgba(245,158,11,0.25);
                                border-radius: 12px; padding: 0.8rem 1.1rem;
                                box-shadow: 0 4px 12px rgba(0,0,0,0.2);">
                        <div style="display: flex; align-items: center; gap: 8px; flex-wrap: wrap;">
                            <span style="font-weight:700;color:#e2e8f0;">👤 {a['patient_name']}</span>
                            <span style="color:#0ea5e9;font-size:0.78rem;">(ID: #{a['patient_id']})</span>
                            <span style="color:#9ca3af;font-size:0.85rem; margin-left: 8px;">
                                📅 {a['scheduled_date']} @ {str(a['start_time'])[:5]}
                            </span>
                        </div>
                        <div style="color:#9ca3af;font-size:0.82rem; margin-top: 4px;">{a['reason'] or ''}</div>
                        {f'<div style="color:#14b8a6;font-size:0.78rem; margin-top: 4px;">{contact_info}</div>' if contact_info else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    if st.button("✅ Confirm", key=f"conf_{a['id']}", type="primary", use_container_width=True):
                        db.update_appointment_status(a["id"], "confirmed")
                        st.success("Confirmed!"); st.rerun()
                with col_r:
                    if st.button("❌ Decline", key=f"decl_{a['id']}", use_container_width=True):
                        db.update_appointment_status(a["id"], "cancelled")
                        st.warning("Declined!"); st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="content-card-title">📋 Today\'s Schedule</div>',
                    unsafe_allow_html=True)
        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        today_appts = db.fetch_appointments(doctor_id=doctor_id, date_filter=date.today()) if doctor_id else []
        # Sort by time
        today_appts = sorted(today_appts, key=lambda a: str(a["start_time"]))

        if today_appts:
            for a in today_appts:
                status = a["status"] or "pending"
                badge  = status_badge(status)
                col_l, col_c, col_r = st.columns([4, 1, 1])
                with col_l:
                    st.markdown(f"""
                    <div class="content-card" style="padding:1rem 1.3rem;margin-bottom:8px;">
                        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;">
                            <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
                                <span style="font-weight:700;color:#e2e8f0;">👤 {a['patient_name']}</span>
                                <span style="color:#0ea5e9;font-size:0.78rem;">(ID: #{a['patient_id']})</span>
                                <span style="color:#9ca3af;font-size:0.85rem; margin-left: 8px;">
                                    🕐 {str(a['start_time'])[:5]}
                                </span>
                                <span style="color:#9ca3af;font-size:0.82rem; margin-left: 6px;">
                                    {a['reason'] or ''}
                                </span>
                            </div>
                            <div>{badge}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_c:
                    if status in ["pending", "confirmed", "booked"]:
                        if st.button("✅ Done", key=f"cmp_{a['id']}", type="primary", use_container_width=True):
                            db.update_appointment_status(a["id"], "completed")
                            st.rerun()
                with col_r:
                    if status in ["pending", "confirmed", "booked"]:
                        if st.button("❌ Cancel", key=f"doc_cancel_{a['id']}", use_container_width=True):
                            db.update_appointment_status(a["id"], "cancelled")
                            st.rerun()
        else:
            st.markdown("""
            <div class="content-card" style="text-align:center;color:#6b7280;padding:2.5rem;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">🎉</div>
                <div style="font-size: 1rem;">No appointments scheduled for today</div>
            </div>
            """, unsafe_allow_html=True)

    # ════════════════════════════════════════════════════════════════════
    # APPOINTMENTS — Weekly Calendar + List View
    # ════════════════════════════════════════════════════════════════════
    elif page == "appointments":
        page_header("Appointments", "Manage your full schedule")

        all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []

        # Status filter
        status_options = ["All", "pending", "confirmed", "completed", "cancelled"]
        col_sf, col_df = st.columns(2)
        status_filter = col_sf.selectbox("Filter by Status", status_options, key="doc_sf")
        date_filter_a = col_df.date_input("Filter by Date (optional)", value=None, key="doc_df_top")

        filtered_appts = db.fetch_appointments(
            doctor_id=doctor_id,
            date_filter=date_filter_a if date_filter_a else None
        ) if doctor_id else []
        if status_filter != "All":
            filtered_appts = [a for a in filtered_appts if (a["status"] or "pending") == status_filter]

        tab_cal, tab_list = st.tabs(["📆 Weekly Calendar", "📋 List & Actions"])

        with tab_cal:
            if "cal_week_offset" not in st.session_state:
                st.session_state.cal_week_offset = 0

            today      = date.today()
            week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.cal_week_offset)
            week_end   = week_start + timedelta(days=5)

            nav_l, nav_title, nav_r = st.columns([1, 3, 1])
            with nav_l:
                if st.button("◀ Prev", key="doc_prev_wk", type="primary"):
                    st.session_state.cal_week_offset -= 1; st.rerun()
            with nav_title:
                st.markdown(f"""
                <div style="text-align:center;font-weight:700;color:#0ea5e9;padding:0.6rem 0;
                            font-size:1.05rem; font-family: 'Space Grotesk', sans-serif;">
                    {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}
                </div>""", unsafe_allow_html=True)
            with nav_r:
                if st.button("Next ▶", key="doc_next_wk", type="primary"):
                    st.session_state.cal_week_offset += 1; st.rerun()

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _weekly_calendar(all_appts, week_start)

        with tab_list:
            if filtered_appts:
                for a in filtered_appts:
                    status = a["status"] or "pending"
                    badge  = status_badge(status)
                    patient_email = a.get('patient_email', '')
                    patient_phone = a.get('patient_phone', '')
                    with st.expander(
                        f"#{a['id']}  {a['patient_name']}  ·  {a['scheduled_date']}  {str(a['start_time'])[:5]}  [{status.upper()}]"
                    ):
                        c1, c2 = st.columns(2)
                        c1.markdown(f"**Patient:** {a['patient_name']} (ID: #{a['patient_id']})")
                        if patient_email:
                            c1.markdown(f"**Email:** {patient_email}")
                        if patient_phone:
                            c1.markdown(f"**Phone:** {patient_phone}")
                        c1.markdown(f"**Reason:** {a['reason'] or '—'}")
                        c1.markdown(f"**Date:** {a['scheduled_date']} @ {str(a['start_time'])[:5]}–{str(a['end_time'])[:5]}")
                        c2.markdown(f"**Status:** {badge}", unsafe_allow_html=True)

                        # Action buttons
                        btn_cols = st.columns(4)
                        if status == "pending":
                            if btn_cols[0].button("✅ Confirm", key=f"lconf_{a['id']}", type="primary"):
                                db.update_appointment_status(a["id"], "confirmed"); st.rerun()
                            if btn_cols[1].button("❌ Decline", key=f"ldecl_{a['id']}"):
                                db.update_appointment_status(a["id"], "cancelled"); st.rerun()
                        elif status == "confirmed":
                            if btn_cols[0].button("✅ Complete", key=f"lcomp_{a['id']}", type="primary"):
                                db.update_appointment_status(a["id"], "completed"); st.rerun()
                            if btn_cols[1].button("❌ Cancel", key=f"lcanc_{a['id']}"):
                                db.update_appointment_status(a["id"], "cancelled"); st.rerun()
                        elif status in ["completed", "cancelled"]:
                            c2.markdown("*No further actions available.*")
            else:
                st.info("No appointments found with the selected filters.")

    # ════════════════════════════════════════════════════════════════════
    # MY PATIENTS — with full health record expand
    # ════════════════════════════════════════════════════════════════════
    elif page == "patients":
        page_header("My Patients", "All patients who have booked with you")

        all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []
        seen = {}
        for a in all_appts:
            pid = a["patient_id"]
            if pid not in seen:
                seen[pid] = {"name": a["patient_name"], "appts": [], "email": a.get("patient_email", ""), "phone": a.get("patient_phone", "")}
            seen[pid]["appts"].append(a)

        if seen:
            search_pat = st.text_input("🔍 Search patient…", placeholder="Name", key="pat_search")
            filtered_patients = {
                pid: info for pid, info in seen.items()
                if not search_pat or search_pat.lower() in info["name"].lower()
            }

            for pid, info in filtered_patients.items():
                pname      = info["name"]
                pemail     = info.get("email", "")
                pphone     = info.get("phone", "")
                appt_list  = info["appts"]
                records    = db.fetch_health_records(patient_id=pid)
                upcoming_p = [a for a in appt_list if str(a["scheduled_date"]) >= str(date.today())]
                last_appt  = sorted(appt_list, key=lambda a: str(a["scheduled_date"]), reverse=True)

                with st.expander(f"👤 {pname} (ID: #{pid})  ·  {len(appt_list)} appointment(s)  ·  {len(records)} record(s)"):
                    col_info, col_rec = st.columns([1, 2])

                    with col_info:
                        contact_info = ""
                        if pemail:
                            contact_info += f"<b style='color:#e2e8f0;'>Email:</b> {pemail}<br>"
                        if pphone:
                            contact_info += f"<b style='color:#e2e8f0;'>Phone:</b> {pphone}<br>"
                        st.markdown(f"""
                        <div style="font-size:0.85rem;color:#9ca3af;line-height:2;">
                            {contact_info}
                            <b style="color:#e2e8f0;">Total Appointments:</b> {len(appt_list)}<br>
                            <b style="color:#e2e8f0;">Upcoming:</b> {len(upcoming_p)}<br>
                            <b style="color:#e2e8f0;">Health Records:</b> {len(records)}<br>
                            {f'<b style="color:#e2e8f0;">Last Visit:</b> {str(last_appt[0]["scheduled_date"])}<br>' if last_appt else ''}
                        </div>
                        """, unsafe_allow_html=True)

                        # Upcoming appointments for this patient
                        if upcoming_p:
                            st.markdown("**Upcoming Appointments:**")
                            for ua in upcoming_p[:3]:
                                badge = status_badge(ua["status"] or "pending")
                                st.markdown(
                                    f"📅 {ua['scheduled_date']} @ {str(ua['start_time'])[:5]} "
                                    f"— {badge}", unsafe_allow_html=True)

                    with col_rec:
                        if records:
                            st.markdown("**📋 Health Records:**")
                            for r in records[:5]:
                                st.markdown(f"""
                                <div style="background: linear-gradient(135deg, rgba(10,22,40,0.65), rgba(15,30,60,0.55));
                                            border: 1px solid rgba(14,165,233,0.15);
                                            border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 8px;
                                            font-size: 0.82rem; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">
                                    <b style="color:#0ea5e9;">{str(r['recorded_at'])[:10]}</b>
                                    {"  ·  Dx: " + (r['diagnosis'] or '') if r['diagnosis'] else ''}
                                    <br>
                                    <span style="color:#9ca3af;">
                                        ❤️ {r['heart_rate'] or '—'} bpm &nbsp;|&nbsp;
                                        🩸 {r['blood_pressure'] or '—'} &nbsp;|&nbsp;
                                        💨 SpO₂ {r['pulse_oximetry'] or '—'}%
                                    </span>
                                    {f'<br><span style="color:#6b7280;">{r["notes"]}</span>' if r['notes'] else ''}
                                </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.info("No health records for this patient yet.")

                        # Quick-add record button
                        if st.button(f"➕ Add Record for {pname}", key=f"add_rec_{pid}"):
                            st.session_state.doctor_page = "records"
                            st.session_state["prefill_patient"] = pid
                            st.rerun()
        else:
            st.info("No patients yet.")

    # ════════════════════════════════════════════════════════════════════
    # HEALTH RECORDS
    # ════════════════════════════════════════════════════════════════════
    elif page == "records":
        page_header("Health Records", "Add and view patient records")

        tab_add, tab_view = st.tabs(["➕ Add Record", "📂 View Records"])

        with tab_add:
            all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []
            patients  = {a["patient_id"]: a["patient_name"] for a in all_appts}

            with st.form("add_hr_form"):
                if patients:
                    # Support pre-fill from "My Patients" quick-add
                    prefill = st.session_state.pop("prefill_patient", None)
                    pat_keys = list(patients.keys())
                    default_idx = pat_keys.index(prefill) if prefill and prefill in pat_keys else 0
                    pat_id = st.selectbox("Select Patient",
                                          options=pat_keys,
                                          index=default_idx,
                                          format_func=lambda x: patients[x])
                else:
                    st.warning("No patients available. Patients must book an appointment first.")
                    pat_id = None

                c1, c2, c3 = st.columns(3)
                hr   = c1.number_input("Heart Rate (bpm)", 0, 250, 72)
                bp   = c2.text_input("Blood Pressure", placeholder="120/80")
                spo2 = c3.number_input("SpO₂ (%)", 0, 100, 98)

                c4, c5, c6 = st.columns(3)
                trop = c4.number_input("Troponin (ng/mL)", 0.0, 100.0, 0.0, format="%.3f")
                ef   = c5.number_input("Ejection Fraction (%)", 0, 100, 60)
                co   = c6.number_input("Cardiac Output (L/min)", 0.0, 20.0, 5.0, step=0.1)

                ecg   = st.text_input("ECG Note", placeholder="Normal sinus rhythm")
                diag  = st.text_input("Diagnosis", placeholder="Primary diagnosis")
                notes = st.text_area("Clinical Notes", placeholder="Additional notes…")

                if st.form_submit_button("💾 Save Record", type="primary"):
                    if pat_id and doctor_id:
                        ok, msg = db.add_health_record(
                            pat_id, doctor_id, hr, bp, trop, ef, co, spo2, ecg, diag, notes)
                        if ok:
                            st.success(f"✅ {msg} — Patient will see this in their Health Dashboard.")
                        else:
                            st.error(msg)
                    else:
                        st.warning("Select a patient first.")

        with tab_view:
            col_f1, col_f2 = st.columns(2)
            all_patient_ids = list({a["patient_id"]: a["patient_name"]
                                    for a in (db.fetch_appointments(doctor_id=doctor_id) if doctor_id else [])}.items())
            view_pat = col_f1.selectbox("Filter by Patient",
                                        ["All"] + [f"{pid}:{nm}" for pid, nm in all_patient_ids],
                                        format_func=lambda x: "All Patients" if x == "All" else x.split(":")[1],
                                        key="doc_rec_filter")
            filter_pid = None if view_pat == "All" else int(view_pat.split(":")[0])

            records = db.fetch_health_records(
                doctor_id=doctor_id,
                patient_id=filter_pid
            ) if doctor_id else []

            if records:
                for r in records[:30]:
                    with st.expander(
                        f"👤 {r['patient_name']}  ·  {str(r['recorded_at'])[:16]}  ·  Dx: {r['diagnosis'] or 'N/A'}"
                    ):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("❤️ HR",   f"{r['heart_rate'] or '—'} bpm")
                        c2.metric("🩸 BP",   r["blood_pressure"] or "—")
                        c3.metric("💨 SpO₂", f"{r['pulse_oximetry'] or '—'}%")
                        c4.metric("🫀 EF",   f"{r['ejection_fraction'] or '—'}%")
                        if r["ecg_note"]:  st.markdown(f"**ECG:** {r['ecg_note']}")
                        if r["diagnosis"]: st.markdown(f"**Diagnosis:** {r['diagnosis']}")
                        if r["notes"]:     st.markdown(f"📝 {r['notes']}")
            else:
                st.info("No health records found.")

    # ════════════════════════════════════════════════════════════════════
    # PRESCRIBE MEDICINES
    # ════════════════════════════════════════════════════════════════════
    elif page == "prescribe":
        page_header("💊 Prescribe Medicines", "Create prescriptions for your patients")

        # Load medicines
        medicines = db.fetch_all_medicines()
        if not medicines:
            st.warning("No medicines available. Please ask admin to add medicines.")
        else:
            # Get patients who have appointments with this doctor
            all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []
            patient_ids = list(set([a["patient_id"] for a in all_appts]))

            if not patient_ids:
                st.info("No patients have booked appointments with you yet.")
            else:
                # Get patient details
                patients = {}
                for pid in patient_ids:
                    p = db.get_user_profile(pid)
                    if p:
                        patients[pid] = p["full_name"]

                st.markdown("### Create New Prescription")
                with st.form("prescribe_form"):
                    col1, col2 = st.columns(2)

                    selected_patient = col1.selectbox("Select Patient", list(patients.keys()),
                                                      format_func=lambda x: patients[x])

                    med_names = {m["id"]: f"{m['name']} ({m['dosage']})" for m in medicines}
                    selected_medicine = col2.selectbox("Select Medicine", list(med_names.keys()),
                                                       format_func=lambda x: med_names[x])

                    col3, col4 = st.columns(2)
                    dosage = col3.text_input("Dosage Instructions", placeholder="e.g. 1 tablet")
                    frequency = col4.text_input("Frequency", placeholder="e.g. Twice daily")

                    col5, col6 = st.columns(2)
                    duration = col5.text_input("Duration", placeholder="e.g. 7 days")
                    quantity = col6.number_input("Quantity", min_value=1, value=30, step=1)

                    notes = st.text_area("Additional Notes", placeholder="Any special instructions...")

                    if st.form_submit_button("➕ Create Prescription", type="primary"):
                        if not selected_patient or not selected_medicine:
                            st.error("Please select patient and medicine!")
                        else:
                            success, msg = db.create_prescription(
                                selected_patient, doctor_id, selected_medicine,
                                dosage, frequency, duration, quantity, notes
                            )
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown("---")
                st.markdown("### 📋 My Prescriptions")

                my_prescriptions = db.fetch_prescriptions(doctor_id=doctor_id)
                if my_prescriptions:
                    for pres in my_prescriptions:
                        status_color = {"active": "#14b8a6", "completed": "#10b981", "cancelled": "#ef4444"}.get(pres["status"], "#9ca3af")
                        st.markdown(f"""
                        <div style="background: rgba(17,24,39,0.5); border: 1px solid rgba(14,165,233,0.2);
                                    border-radius: 12px; padding: 1rem; margin: 0.5rem 0;">
                            <div style="display: flex; justify-content: space-between;">
                                <div>
                                    <b style="color:#0ea5e9;">{pres['medicine_name']}</b>
                                    <span style="color:#9ca3af; margin-left: 8px;">({pres['medicine_dosage']})</span>
                                </div>
                                <div style="color: {status_color}; font-weight: bold;">{pres['status'].upper()}</div>
                            </div>
                            <div style="font-size: 0.85rem; color:#9ca3af; margin-top: 5px;">
                                👤 Patient: {pres['patient_name']} | 💊 Qty: {pres['quantity']}
                            </div>
                            <div style="font-size: 0.85rem; color:#9ca3af;">
                                📝 {pres['dosageInstructions']} - {pres['frequency']} - {pres['duration']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.info("No prescriptions created yet.")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: MEDICINES
    # ════════════════════════════════════════════════════════════════════
    elif page == "medicines":
        page_header("💊 Medicines", "Browse pharmacy inventory (Read-only)")

        medicines = db.fetch_all_medicines()

        # Search and filter
        col_search1, col_search2 = st.columns([2, 1])
        with col_search1:
            search_term = st.text_input("🔍 Search medicines", placeholder="Search by name...")
        with col_search2:
            category_filter = st.selectbox("Category", ["All"] + list(set(m.get("category", "General") for m in medicines)))

        # Filter medicines
        filtered_meds = medicines
        if search_term:
            filtered_meds = [m for m in filtered_meds if search_term.lower() in m.get("name", "").lower()]
        if category_filter != "All":
            filtered_meds = [m for m in filtered_meds if m.get("category") == category_filter]

        st.info("👨‍⚕️ Doctors can only view medicines. Contact admin to add/edit medicines.")

        if not filtered_meds:
            st.warning("No medicines found.")
        else:
            st.markdown(f"### 📋 Medicines List ({len(filtered_meds)} found)")

            # Grid layout with proper image display - 3 columns
            cols_per_row = 3
            for row_start in range(0, len(filtered_meds), cols_per_row):
                cols = st.columns(cols_per_row)
                row_meds = filtered_meds[row_start:row_start + cols_per_row]

                for col_idx, m in enumerate(row_meds):
                    with cols[col_idx]:
                        with st.container():
                            stock = m.get("stock_quantity", 0)
                            stock_color = "#22c55e" if stock > 50 else "#f59e0b" if stock > 10 else "#ef4444"
                            stock_text = "In Stock" if stock > 10 else "Low Stock" if stock > 0 else "Out of Stock"
                            stock_icon = "✅" if stock > 10 else "⚠️" if stock > 0 else "❌"

                            # Get image - use st.image for proper display
                            img_url = m.get("image_url", "")

                            # Check if image exists using absolute path
                            img_exists = False
                            if img_url:
                                # Try different path formats
                                possible_paths = [
                                    img_url,
                                    os.path.join(os.path.dirname(__file__), "..", img_url),
                                    os.path.join(os.getcwd(), img_url),
                                ]
                                for path in possible_paths:
                                    if os.path.exists(path):
                                        img_exists = True
                                        img_display_path = path
                                        break

                            if img_exists:
                                try:
                                    st.image(img_display_path, width=100, use_container_width=False)
                                except:
                                    st.markdown('<div style="width:100%;height:100px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin-bottom:10px;">💊</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div style="width:100%;height:100px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin-bottom:10px;">💊</div>', unsafe_allow_html=True)

                            # Medicine details
                            st.markdown(f"**{m.get('name', 'Unknown')}**")
                            st.markdown(f"<span style='color:#6b7280;font-size:0.85rem;'>📦 {m.get('category', 'General')}</span>", unsafe_allow_html=True)
                            st.markdown(f"<span style='color:#0ea5e9;font-size:1rem;font-weight:bold;'>💰 ₹{m.get('unit_price', 0)}</span>", unsafe_allow_html=True)

                            if stock > 10:
                                st.success(f"{stock_icon} In Stock")
                            elif stock > 0:
                                st.warning(f"{stock_icon} Low Stock")
                            else:
                                st.error(f"{stock_icon} Out of Stock")

                            if m.get('composition'):
                                st.caption(f"Composition: {m.get('composition', '')[:35]}...")
                            if m.get('dosage'):
                                st.caption(f"Dosage: {m.get('dosage', '')}")
                            if m.get('manufacturer'):
                                st.caption(f"Manufacturer: {m.get('manufacturer', '')}")

                            st.markdown("---")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: AI CARE
    # ════════════════════════════════════════════════════════════════════
    elif page == "ai_care":
        ai_care.render_ai_care_tab(user)

    # ════════════════════════════════════════════════════════════════════
    # MY PROFILE
    # ════════════════════════════════════════════════════════════════════
    elif page == "profile":
        page_header("My Profile", "Update your personal and professional details")

        profile     = db.get_user_profile(user["id"])
        specialties = db.fetch_all_specialties()
        sp_map      = {s["name"]: s["id"] for s in specialties}
        sp_names    = list(sp_map.keys())
        specialty   = doc_profile["specialty_name"] if doc_profile and doc_profile.get("specialty_name") else "—"

        col_l, col_r = st.columns([1, 2])
        with col_l:
            # Appointment stats
            all_appts = db.fetch_appointments(doctor_id=doctor_id) if doctor_id else []
            completed_c = sum(1 for a in all_appts if a["status"] == "completed")
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, rgba(10,22,40,0.8), rgba(15,30,60,0.7));
                        border: 1px solid rgba(14,165,233,0.2);
                        border-radius: 18px; padding: 2rem; text-align: center;
                        box-shadow: 0 8px 24px rgba(0,0,0,0.3);">
                <div style="font-size: 4rem; margin-bottom: 0.6rem; animation: float-icon 3s ease-in-out infinite;">🩺</div>
                <div style="font-size: 1.15rem; font-weight: 700; color: #ffffff;">Dr. {profile['full_name'] if profile else user['name']}</div>
                <div style="color: #0ea5e9; font-size: 0.88rem; margin-top: 5px; font-weight: 600;">{specialty}</div>
                <div style="color: #9ca3af; font-size: 0.8rem; margin-top: 4px;">{profile['email'] if profile else ''}</div>
                <div style="margin-top: 1.2rem; display: flex; justify-content: space-around;">
                    <div style="text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 800; color: #0ea5e9;">{len(all_appts)}</div>
                        <div style="font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Appointments</div>
                    </div>
                    <div style="text-align: center;">
                        <div style="font-size: 1.4rem; font-weight: 800; color: #10b981;">{completed_c}</div>
                        <div style="font-size: 0.7rem; color: #6b7280; text-transform: uppercase; letter-spacing: 0.05em;">Completed</div>
                    </div>
                </div>
                <div style="margin-top: 1.2rem; display: flex; align-items: center; justify-content: center; gap: 8px;">
                    <span style="width: 8px; height: 8px; border-radius: 50%; background: #10b981;
                                 box-shadow: 0 0 8px #10b981; display: inline-block; animation: pulse-dot 2s infinite;"></span>
                    <span style="font-size: 0.75rem; color: #10b981; font-weight: 700; letter-spacing: 0.05em;">ACTIVE</span>
                </div>
            </div>
            <style>
            @keyframes pulse-dot {{
                0%, 100% {{ transform: scale(1); opacity: 1; }}
                50% {{ transform: scale(1.3); opacity: 0.6; }}
            }}
            </style>
            """, unsafe_allow_html=True)

        with col_r:
            tab_p, tab_pro = st.tabs(["👤 Personal Info", "🏥 Professional Info"])
            with tab_p:
                with st.form("doc_personal"):
                    name  = st.text_input("Full Name",    value=profile["full_name"] if profile else "")
                    phone = st.text_input("Phone",        value=str(profile["phone"] or "") if profile else "")
                    genders = ["", "Male", "Female", "Other"]
                    g_idx = genders.index(profile["gender"] or "") if profile and profile.get("gender") in genders else 0
                    gender = st.selectbox("Gender", genders, index=g_idx)
                    if st.form_submit_button("Save Personal Info", type="primary"):
                        db.update_user_profile(user["id"], name, gender or None,
                                               profile["dob"] if profile else None, phone or None)
                        st.session_state.user_data["name"] = name
                        st.success("Saved!")

            with tab_pro:
                with st.form("doc_professional"):
                    bio = st.text_area("Bio / About",
                                       value=doc_profile["bio"] or "" if doc_profile else "")
                    exp = st.number_input("Years of Experience", 0, 60,
                                          value=doc_profile["experience_years"] or 0 if doc_profile else 0)
                    fee = st.number_input("Consultation Fee (₹)", 0.0, 10000.0,
                                          value=float(doc_profile["consultation_fee"] or 0) if doc_profile else 0.0)
                    sp_cur = doc_profile.get("specialty_name") if doc_profile else None
                    sp_idx = sp_names.index(sp_cur) if sp_cur and sp_cur in sp_names else 0
                    sp_sel = st.selectbox("Specialty", sp_names, index=sp_idx) if sp_names else None
                    if st.form_submit_button("Save Professional Info", type="primary"):
                        sp_id = sp_map.get(sp_sel) if sp_sel else None
                        db.update_doctor_profile(user["id"], bio, int(exp), float(fee), sp_id)
                        st.success("Professional info updated! Patients will see your updated profile.")