import streamlit as st
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import db
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import date, timedelta
from pages.shared_styles import (inject_css, sidebar_header, page_header,
                                  stat_cards, status_badge, PLOTLY_LAYOUT, sidebar_footer, medical_banner)
import ai_care

def render():
    inject_css()
    user = st.session_state.user_data

    # ── Sidebar ──────────────────────────────────────────────────────────
    sidebar_header("Admin", user["name"])

    # Sidebar pages
    PAGES = {
        "🛡️  Admin Console":    "console",
        "👨‍⚕️  Manage Doctors":  "manage_doctors",
        "👥  Patients":          "patients",
        "➕  Doctors":           "doctors",
        "📅  Appointments":      "appointments",
        "💊  Medicines":        "medicines",
        "📦  Orders":           "orders",
        "🤖  AI Care":           "ai_care",
    }
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = "console"

    with st.sidebar:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
        for label, key in PAGES.items():
            is_active = (st.session_state.admin_page == key)
            kind = "primary" if is_active else "secondary"
            if st.button(label, key=f"anav_{key}", use_container_width=True, type=kind):
                st.session_state.admin_page = key
                st.rerun()

        st.markdown("<hr style='border-color:rgba(255,255,255,0.1);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)
        if st.button("↩  Log out", key="admin_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        sidebar_footer()

    page = st.session_state.admin_page

    # ════════════════════════════════════════════════════════════════════
    # ADMIN CONSOLE — sub-tabs: Analytics | Create doctor | Availability
    #                           | Specialties | Records | All appointments
    # ════════════════════════════════════════════════════════════════════
    if page == "console":
        medical_banner("Admin")

        page_header("Admin Console", "Full oversight of IPCMS")

        counts       = db.fetch_user_counts()
        all_appts    = db.fetch_appointments()
        upcoming_cnt = sum(1 for a in all_appts if str(a["scheduled_date"]) >= str(date.today()))

        stat_cards([
            ("🧑‍⚕️", "Patients",      str(counts.get("Patient", 0))),
            ("➕",   "Doctors",       str(counts.get("Doctor", 0))),
            ("📅",   "Appointments",  str(len(all_appts))),
            ("💧",   "Upcoming",      str(upcoming_cnt)),
        ])

        st.markdown("<br>", unsafe_allow_html=True)

        # Sub-tabs
        (tab_analytics, tab_create, tab_avail,
         tab_specialties, tab_records, tab_allappts, tab_medicines, tab_debug) = st.tabs([
            "Analytics", "Create Doctor", "Availability",
            "Specialties", "Records", "Appointments", "Medicines", "Debug"
        ])

        # ── Analytics ────────────────────────────────────────────────
        with tab_analytics:
            col_chart1, col_chart2 = st.columns([3, 2])

            with col_chart1:
                days = [(date.today() - timedelta(days=i)) for i in range(6, -1, -1)]
                counts_per_day = []
                for d in days:
                    day_appts = db.fetch_appointments(date_filter=d)
                    counts_per_day.append(len(day_appts))

                fig_bar = go.Figure(go.Bar(
                    x=[d.strftime("%b %d\n%Y") for d in days],
                    y=counts_per_day,
                    marker=dict(
                        color="#0ea5e9",
                        line=dict(width=0)
                    )
                ))
                fig_bar.update_layout(
                    **PLOTLY_LAYOUT,
                    title=dict(text="Appointments per day", font=dict(color="#ffffff", size=13)),
                    height=280,
                    showlegend=False,
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_chart2:
                status_counts = {}
                for a in all_appts:
                    s = (a["status"] or "booked").lower()
                    status_counts[s] = status_counts.get(s, 0) + 1

                if status_counts:
                    fig_donut = go.Figure(go.Pie(
                        labels=list(status_counts.keys()),
                        values=list(status_counts.values()),
                        hole=0.55,
                        marker=dict(
                            colors=["#0ea5e9", "#14b8a6", "#8b5cf6", "#ef4444"],
                            line=dict(color="#030712", width=2)
                        )
                    ))
                    fig_donut.update_layout(
                        **PLOTLY_LAYOUT,
                        title=dict(text="By status", font=dict(color="#ffffff", size=13)),
                        height=280,
                        legend=dict(font=dict(color="#9ca3af", size=10)),
                    )
                else:
                    fig_donut = go.Figure()
                    fig_donut.update_layout(**PLOTLY_LAYOUT, height=280)
                    fig_donut.add_annotation(text="No data", x=0.5, y=0.5,
                                             font=dict(color="#6b7280", size=14), showarrow=False)
                st.plotly_chart(fig_donut, use_container_width=True)

            # Appointments by specialty
            st.markdown('<div class="content-card-title">📊 Appointments by specialty</div>',
                        unsafe_allow_html=True)
            doctors  = db.fetch_all_doctors()
            spec_map = {d["id"]: d["specialty"] or "General" for d in doctors}
            spec_counts = {}
            for a in all_appts:
                sp = spec_map.get(a["doctor_id"], "General")
                spec_counts[sp] = spec_counts.get(sp, 0) + 1

            if spec_counts:
                fig_sp = go.Figure(go.Bar(
                    y=list(spec_counts.keys()),
                    x=list(spec_counts.values()),
                    orientation="h",
                    marker=dict(color="#14b8a6", line=dict(width=0))
                ))
                fig_sp.update_layout(**PLOTLY_LAYOUT, height=220, showlegend=False)
                st.plotly_chart(fig_sp, use_container_width=True)
            else:
                st.info("No appointment data by specialty yet.")

        # ── Create doctor ─────────────────────────────────────────────
        with tab_create:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(14,165,233,0.1), rgba(20,184,166,0.08));
                        border: 1px solid rgba(14,165,233,0.2);
                        border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1.4rem;
                        font-size: 0.9rem; color: #9ca3af;">
                <div style="font-weight: 700; color: #0ea5e9; margin-bottom: 5px;">👨‍⚕️ Create Doctor Login</div>
                Create a login for a new doctor. Only admins can perform this action.
            </div>
            """, unsafe_allow_html=True)

            specialties = db.fetch_all_specialties()
            sp_names    = [s["name"] for s in specialties]

            with st.form("create_doc_form"):
                c1, c2 = st.columns(2)
                doc_name  = c1.text_input("Full name")
                doc_pass  = c2.text_input("Temporary password", type="password")
                doc_email = c1.text_input("Email")
                doc_exp   = c2.number_input("Experience (years)", min_value=0, max_value=60, value=5)
                doc_sp    = c1.selectbox("Specialty", sp_names if sp_names else ["General Medicine"])
                doc_fee   = c2.number_input("Consultation fee", min_value=0, max_value=10000, value=100)
                doc_bio   = st.text_area("Short bio", placeholder="Brief description of expertise…")

                if st.form_submit_button("Create doctor account", type="primary"):
                    if not doc_name or not doc_email or not doc_pass:
                        st.warning("Name, email and password are required.")
                    else:
                        import auth as auth_mod
                        ok, msg = auth_mod.register_user(doc_email, doc_pass, doc_name, "Doctor")
                        if ok:
                            # Get the new user ID and create doctor profile
                            new_user = auth_mod.get_user_by_email(doc_email)
                            if new_user:
                                sp_map = {s["name"]: s["id"] for s in specialties}
                                sp_id  = sp_map.get(doc_sp)
                                db.update_doctor_profile(new_user["id"], doc_bio, int(doc_exp), float(doc_fee), sp_id)
                            st.success(f"✅ Doctor account created for {doc_name}!")
                            st.rerun()
                        else:
                            st.error(msg)

        # ── Availability ──────────────────────────────────────────────
        with tab_avail:
            st.markdown('<div class="content-card-title">🕐 Doctor Availability</div>',
                        unsafe_allow_html=True)
            doctors = db.fetch_all_doctors()
            if doctors:
                for doc in doctors:
                    appts_today = db.fetch_appointments(doctor_id=doc["id"], date_filter=date.today())
                    status_txt = f"📅 {len(appts_today)} appointment(s) today"
                    st.markdown(f"""
                    <div style="background: #ffffff;
                                border: 1.5px solid #e2e8f0;
                                border-radius: 12px; padding: 0.9rem 1.2rem; margin-bottom: 0.7rem;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.04); display: flex;
                                align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-weight: 700; color: #0f172a; font-size: 0.95rem;">Dr. {doc['full_name']}</span>
                            <span style="font-size: 0.8rem; color: #0369a1; margin-left: 8px; font-weight:600;">
                                {doc['specialty'] if doc.get('specialty') else 'General'}
                            </span>
                        </div>
                        <div style="font-size: 0.82rem; color: #059669; font-weight: 600;">{status_txt}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No doctors registered yet.")

        # ── Specialties ───────────────────────────────────────────────
        with tab_specialties:
            specialties = db.fetch_all_specialties()
            sp_icons_map = {
                "Cardiology": "🫀", "Neurology": "🧠", "Pediatrics": "👶",
                "Orthopedics": "🦴", "General Medicine": "⚕️", "Dermatology": "🩹",
                "Pulmonology": "🫁", "Psychiatry": "🧘", "Ophthalmology": "👁️",
                "Oncology": "🎗️", "Gastroenterology": "🫃", "Nephrology": "🫘",
                "Urology": "🔬", "Endocrinology": "⚗️", "Gynecology": "🌸"
            }

            if specialties:
                for s in specialties:
                    icon = s.get("icon") or sp_icons_map.get(s["name"], "🏥")
                    desc = s.get("description") or ""
                    st.markdown(f"""
                    <div style="display:flex;align-items:center;gap:0.8rem;padding:0.7rem 0;
                                border-bottom:1px solid rgba(14,165,233,0.1);">
                        <span style="font-size:1.4rem;">{icon}</span>
                        <span>
                            <b style="color:#ffffff;">{s['name']}</b>
                            {f'<span style="color:#6b7280; margin-left: 8px;">— {desc}</span>' if desc else ''}
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("No specialties added yet.")

            st.markdown("<br>", unsafe_allow_html=True)
            with st.form("add_sp_form"):
                c1, c2, c3 = st.columns([2, 3, 1])
                sp_name = c1.text_input("Name", placeholder="e.g. Cardiology")
                sp_desc = c2.text_input("Description", placeholder="Brief description")
                sp_icon = c3.text_input("Icon", placeholder="🫀", value="🏥")
                if st.form_submit_button("Add specialty", type="primary"):
                    if sp_name:
                        ok, msg = db.add_specialty(sp_name, sp_desc, sp_icon)
                        st.success(msg) if ok else st.error(msg)
                        if ok: st.rerun()
                    else:
                        st.warning("Name is required.")

        # ── Records ───────────────────────────────────────────────────
        with tab_records:
            st.markdown('<div class="content-card-title">📋 All Health Records</div>',
                        unsafe_allow_html=True)
            records = db.fetch_health_records()
            if records:
                for r in records[:30]:
                    with st.expander(
                        f"👤 {r['patient_name']}  ·  Dr. {r['doctor_name'] or 'N/A'}  ·  {str(r['recorded_at'])[:16]}"
                    ):
                        c1, c2, c3, c4 = st.columns(4)
                        c1.metric("❤️ HR",   f"{r['heart_rate'] or '—'} bpm")
                        c2.metric("🩸 BP",   r["blood_pressure"] or "—")
                        c3.metric("💨 SpO₂", f"{r['pulse_oximetry'] or '—'}%")
                        c4.metric("🫀 EF",   f"{r['ejection_fraction'] or '—'}%")
                        if r["diagnosis"]: st.markdown(f"**Diagnosis:** {r['diagnosis']}")
                        if r["notes"]:     st.markdown(f"📝 {r['notes']}")
            else:
                st.info("No health records available.")

        # ── All appointments ──────────────────────────────────────────
        with tab_allappts:
            col_f1, col_f2 = st.columns(2)
            date_filter   = col_f1.date_input("Filter by Date", value=None, key="af_date_console")
            status_filter = col_f2.selectbox("Filter by Status",
                                              ["All", "pending", "confirmed", "completed", "cancelled"],
                                              key="af_status_console")

            appts = db.fetch_appointments(date_filter=date_filter if date_filter else None)
            if status_filter != "All":
                appts = [a for a in appts if (a["status"] or "pending") == status_filter]

            if appts:
                rows = []
                for a in appts:
                    rows.append({
                        "#":        a["id"],
                        "Patient":  f"{a['patient_name']} (ID: #{a['patient_id']})",
                        "Doctor":   f"Dr. {a['doctor_name']} (ID: #{a['doctor_id']})",
                        "Date":     str(a["scheduled_date"]),
                        "Time":     str(a["start_time"]),
                        "Status":   (a["status"] or "pending").title(),
                        "Reason":   a["reason"] or "—",
                    })
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True, hide_index=True)

                st.markdown("<br>**Update Appointment Status**", unsafe_allow_html=True)
                for a in appts[:10]:
                    status = a["status"] or "pending"
                    badge  = status_badge(status)
                    with st.expander(
                        f"#{a['id']}  {a['patient_name']} (ID:#{a['patient_id']}) → Dr. {a['doctor_name']} (ID:#{a['doctor_id']})  |  {a['scheduled_date']}"
                    ):
                        c1, c2, c3 = st.columns([2, 2, 1])
                        c1.markdown(f"**Patient ID:** #{a['patient_id']} | **Doctor ID:** #{a['doctor_id']}")
                        c1.markdown(f"**Reason:** {a['reason'] or '—'}")
                        c2.markdown(f"**Status:** {badge}", unsafe_allow_html=True)
                        opts  = ["pending", "confirmed", "completed", "cancelled"]
                        new_s = c3.selectbox("", opts,
                                             index=opts.index(status if status in opts else "pending"),
                                             key=f"appt_s_c_{a['id']}", label_visibility="collapsed")
                        if st.button("Update", key=f"upd_c_{a['id']}", type="primary"):
                            db.update_appointment_status(a["id"], new_s)
                            st.success("Updated!")
                            st.rerun()
            else:
                st.info("No appointments found.")

        # ── Medicines Tab ─────────────────────────────────────────────────
        with tab_medicines:
            st.markdown("### 💊 Medicine Management")

            # Load sample medicines button
            if st.button("🧪 Load Sample Medicines"):
                success, msg = db.seed_dummy_medicines()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            st.markdown("---")

            # Tabs for medicine management
            tab_med_list, tab_med_add, tab_med_stock, tab_med_cats = st.tabs(["📋 All Medicines", "➕ Add Medicine", "📦 Stock Management", "📂 Categories"])

            with tab_med_list:
                st.markdown("#### All Available Medicines")

                # Search and filter
                col_search, col_cat = st.columns([2, 1])
                search_term = col_search.text_input("🔍 Search medicines...", placeholder="Search by name or manufacturer")
                categories = ["All"] + db.get_medicine_categories()
                category_filter = col_cat.selectbox("Category", categories)

                medicines = db.fetch_all_medicines(category=category_filter if category_filter != "All" else None, search=search_term)

                st.markdown(f"**Showing {len(medicines)} medicines**")

                if medicines:
                    for med in medicines:
                        stock_color = "green" if med["stock_quantity"] > 50 else "orange" if med["stock_quantity"] > 20 else "red"
                        st.markdown(f"""
                        <div style="background: #ffffff; border: 1.5px solid #e2e8f0;
                                    border-radius: 12px; padding: 1rem; margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                            <div style="display: flex; justify-content: space-between; align-items: center;">
                                <div>
                                    <b style="color:#0369a1; font-size: 1.1rem;">{med['name']}</b>
                                    <span style="color:#475569; margin-left: 10px;">{med['category']}</span>
                                </div>
                                <div style="text-align: right;">
                                    <div style="color: {stock_color}; font-weight: bold;">Stock: {med['stock_quantity']}</div>
                                    <div style="color:#0f172a; font-size: 0.85rem; font-weight:600;">₹{med['unit_price']}</div>
                                </div>
                            </div>
                            <div style="font-size: 0.85rem; color:#475569; margin-top: 5px;">
                                {med['manufacturer']} | {med['dosage']} | Exp: {med['expiry_date']}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Actions for each medicine
                        col_act1, col_act2, col_act3 = st.columns([1, 1, 1])
                        with col_act1:
                            if st.button(f"✏️ Edit", key=f"edit_med_{med['id']}"):
                                st.session_state.edit_medicine_id = med['id']
                                st.rerun()
                        with col_act2:
                            if st.button(f"➕ Stock", key=f"add_stock_{med['id']}"):
                                st.session_state.add_stock_id = med['id']
                                st.rerun()
                        with col_act3:
                            if st.button(f"🗑️ Delete", key=f"del_med_{med['id']}"):
                                success, msg = db.delete_medicine(med['id'])
                                if success:
                                    st.success(msg)
                                    st.rerun()
                                else:
                                    st.error(msg)
                else:
                    st.info("No medicines found.")

            with tab_med_add:
                st.markdown("#### Add New Medicine")
                with st.form("add_medicine_form"):
                    col1, col2 = st.columns(2)
                    name = col1.text_input("Medicine Name *", placeholder="e.g. Aspirin")
                    category = col2.selectbox("Category", ["Pain Relief", "Antibiotic", "Allergy", "Diabetes", "Blood Pressure", "Gastric", "Supplements", "Other"])
                    manufacturer = col1.text_input("Manufacturer", placeholder="e.g. Cipla")
                    composition = col2.text_input("Composition", placeholder="e.g. Acetylsalicylic acid")
                    dosage = col1.text_input("Dosage", placeholder="e.g. 500mg")
                    unit_price = col2.number_input("Unit Price (₹)", min_value=0.0, value=0.0, step=1.0)
                    stock_quantity = col1.number_input("Initial Stock", min_value=0, value=0, step=1)
                    expiry_date = col2.date_input("Expiry Date", value=None)

                    description = st.text_area("Description", placeholder="Brief description of the medicine...")

                    if st.form_submit_button("➕ Add Medicine", type="primary"):
                        if not name:
                            st.error("Medicine name is required!")
                        else:
                            success, msg = db.add_medicine(name, category, manufacturer, composition, dosage, unit_price, stock_quantity, str(expiry_date) if expiry_date else None, description)
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

            with tab_med_stock:
                st.markdown("#### Stock Management")
                medicines = db.fetch_all_medicines()
                if medicines:
                    for med in medicines:
                        col_info, col_action = st.columns([3, 1])
                        with col_info:
                            stock_color = "green" if med["stock_quantity"] > 50 else "orange" if med["stock_quantity"] > 20 else "red"
                            st.markdown(f"""
                            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-radius: 10px; padding: 0.8rem; margin: 0.3rem 0; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                                <b style="color:#0f172a;">{med['name']}</b> - <span style="color:{stock_color}; font-weight:600;">Stock: {med['stock_quantity']}</span>
                                <div style="font-size: 0.8rem; color:#475569;">₹{med['unit_price']} per unit</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col_action:
                            col_plus, col_minus = st.columns(2)
                            new_qty = col_plus.number_input(f"Qty {med['id']}", min_value=0, value=med['stock_quantity'], key=f"qty_{med['id']}")
                            if new_qty != med['stock_quantity']:
                                if st.button("Update", key=f"update_{med['id']}"):
                                    diff = new_qty - med['stock_quantity']
                                    db.update_medicine_stock(med['id'], diff)
                                    st.success("Stock updated!")
                                    st.rerun()
                else:
                    st.info("No medicines available.")

            with tab_med_cats:
                st.markdown("#### Medicine Categories")

                # Get category statistics
                medicines = db.fetch_all_medicines()
                categories = db.get_medicine_categories()

                if categories:
                    for cat in categories:
                        cat_medicines = [m for m in medicines if m.get("category") == cat]
                        total_stock = sum(m.get("stock_quantity", 0) for m in cat_medicines)
                        total_value = sum(m.get("stock_quantity", 0) * m.get("unit_price", 0) for m in cat_medicines)

                        with st.expander(f"📦 {cat} ({len(cat_medicines)} medicines | Stock: {total_stock} | Value: ₹{total_value:,.0f})"):
                            # Show medicines in a proper grid with images - 4 columns
                            cols_per_row = 4
                            for row_start in range(0, len(cat_medicines), cols_per_row):
                                cols = st.columns(cols_per_row)
                                row_meds = cat_medicines[row_start:row_start + cols_per_row]

                                for col_idx, med in enumerate(row_meds):
                                    with cols[col_idx]:
                                        with st.container():
                                            img_url = med.get("image_url", "")
                                            if img_url and os.path.exists(img_url):
                                                st.image(img_url, width=100, use_container_width=False)
                                            else:
                                                st.markdown('''
                                                <div style="width:100%;height:100px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2.5rem;margin-bottom:8px;">
                                                    💊
                                                </div>
                                                ''', unsafe_allow_html=True)
                                            st.markdown(f"**{med['name']}**")
                                            st.markdown(f"💰 ₹{med['unit_price']} | 📦 {med['stock_quantity']}")
                                            st.markdown("---")
                else:
                    st.info("No categories found.")

        # ── Debug Tab ─────────────────────────────────────────────────
        with tab_debug:
            st.markdown("### 🔧 Database Debug")
            st.markdown("This shows raw data from the database.")

            if st.button("🔄 Refresh Data"):
                st.rerun()

            st.markdown("---")
            st.markdown("### 🧪 Create Test Appointment")
            if st.button("➕ Create Test Appointment"):
                success, msg = db.create_test_appointment()
                if success:
                    st.success(msg)
                    st.rerun()
                else:
                    st.error(msg)

            # Show raw appointments
            raw_appts = db.debug_get_all_appointments()
            st.markdown(f"**Total appointments in DB: {len(raw_appts)}**")

            if raw_appts:
                st.markdown("#### Raw Appointments Data:")
                for a in raw_appts:
                    st.markdown(f"""
                    <div style="background: rgba(17,24,39,0.5); border: 1px solid rgba(14,165,233,0.2);
                                border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0; font-family: monospace; font-size: 0.85rem;">
                        <b>ID:</b> {a['id']} | <b>Patient ID:</b> {a['patient_id']} | <b>Doctor ID:</b> {a['doctor_id']}<br>
                        <b>Date:</b> {a['scheduled_date']} | <b>Time:</b> {a['start_time']} - {a['end_time']}<br>
                        <b>Status:</b> {a['status']} | <b>Reason:</b> {a['reason']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No appointments found in database!")

            st.markdown("---")

            # Show all users
            st.markdown("#### All Users in Database:")
            all_users = db.fetch_all_users()
            st.markdown(f"**Total users: {len(all_users)}**")
            for u in all_users:
                st.markdown(f"- ID:{u['id']} | {u['full_name']} | {u['email']} | {u['role']}")

            st.markdown("---")

            # Show all doctors
            st.markdown("#### All Doctors in Database:")
            all_docs = db.fetch_all_doctors()
            st.markdown(f"**Total doctors: {len(all_docs)}**")
            for d in all_docs:
                st.markdown(f"- ID:{d['id']} | {d['full_name']} | {d['specialty']} | User ID: {d.get('user_id', 'N/A')}")

    # ════════════════════════════════════════════════════════════════════
    # MANAGE DOCTORS — Add logins + view/manage existing
    # ════════════════════════════════════════════════════════════════════
    elif page == "manage_doctors":
        import auth as auth_mod
        page_header("Manage Doctors", "Create, view and manage all doctor accounts")

        tab_add, tab_all = st.tabs(["➕  Add Doctor Login", "📋  All Doctor Accounts"])

        # ── Tab 1: Add Doctor Login ───────────────────────────────────
        with tab_add:
            st.markdown("""
            <div style="background: linear-gradient(135deg, rgba(14,165,233,0.1), rgba(20,184,166,0.08));
                        border: 1px solid rgba(14,165,233,0.25);
                        border-radius: 14px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem;
                        box-shadow: 0 4px 16px rgba(14,165,233,0.15);">
                <div style="font-size: 0.98rem; font-weight: 700; color: #0ea5e9; margin-bottom: 5px;">
                    👨‍⚕️ Create Doctor Login
                </div>
                <div style="font-size: 0.85rem; color: #9ca3af;">
                    Fill in the form below to create a new doctor account.
                    The doctor can log in immediately with the email and password you set.
                </div>
            </div>
            """, unsafe_allow_html=True)

            specialties = db.fetch_all_specialties()
            sp_names = [s["name"] for s in specialties] or ["General Medicine"]

            with st.form("add_doctor_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                doc_name  = c1.text_input("Full Name",           placeholder="e.g. Dr. Ayesha Khan")
                doc_email = c2.text_input("Email Address",       placeholder="doctor@hospital.com")
                doc_pass  = c1.text_input("Password",            type="password", placeholder="••••••••")
                doc_pass2 = c2.text_input("Confirm Password",    type="password", placeholder="••••••••")
                doc_sp    = c1.selectbox("Specialty",            sp_names)
                doc_exp   = c2.number_input("Experience (years)", min_value=0, max_value=60, value=5, step=1)
                doc_fee   = c1.number_input("Consultation Fee (₹)", min_value=0, max_value=50000, value=500, step=50)
                doc_phone = c2.text_input("Phone",               placeholder="+91 XXXXX XXXXX")
                doc_bio   = st.text_area("Short Bio",
                    placeholder="Brief description of expertise, qualifications and approach…",
                    height=90)

                submitted = st.form_submit_button("✅ Create Doctor Account", type="primary", use_container_width=True)

            if submitted:
                if not doc_name or not doc_email or not doc_pass:
                    st.error("Name, email and password are required.")
                elif doc_pass != doc_pass2:
                    st.error("Passwords do not match.")
                elif len(doc_pass) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    ok, msg = auth_mod.register_user(doc_email, doc_pass, doc_name, "Doctor")
                    if ok:
                        new_user = auth_mod.get_user_by_email(doc_email)
                        if new_user:
                            sp_map = {s["name"]: s["id"] for s in specialties}
                            sp_id  = sp_map.get(doc_sp)
                            db.update_doctor_profile(new_user["id"], doc_bio, int(doc_exp), float(doc_fee), sp_id)
                        st.success(f"✅ Doctor account created for **{doc_name}** ({doc_email})!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")

        # ── Tab 2: All Doctor Accounts ────────────────────────────────
        with tab_all:
            doctors = db.fetch_all_doctors()

            if not doctors:
                st.info("No doctor accounts yet. Use the 'Add Doctor Login' tab to create one.")
            else:
                # Summary bar
                total   = len(doctors)
                active  = sum(1 for d in doctors if d.get("is_active"))
                st.markdown(f"""
                <div style="display:flex;gap:1rem;margin-bottom:1.4rem;flex-wrap:wrap;">
                    <div style="background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(14,165,233,0.08));
                                border: 1px solid rgba(14,165,233,0.3); border-radius: 12px;
                                padding: 0.75rem 1.2rem; min-width: 120px; box-shadow: 0 4px 12px rgba(14,165,233,0.15);">
                        <div style="font-size: 1.6rem; font-weight: 800; color: #0ea5e9;">{total}</div>
                        <div style="font-size: 0.78rem; color: #9ca3af;">Total Doctors</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(20,184,166,0.15), rgba(20,184,166,0.08));
                                border: 1px solid rgba(20,184,166,0.3); border-radius: 12px;
                                padding: 0.75rem 1.2rem; min-width: 120px; box-shadow: 0 4px 12px rgba(20,184,166,0.15);">
                        <div style="font-size: 1.6rem; font-weight: 800; color: #14b8a6;">{active}</div>
                        <div style="font-size: 0.78rem; color: #9ca3af;">Active</div>
                    </div>
                    <div style="background: linear-gradient(135deg, rgba(239,68,68,0.15), rgba(239,68,68,0.08));
                                border: 1px solid rgba(239,68,68,0.3); border-radius: 12px;
                                padding: 0.75rem 1.2rem; min-width: 120px; box-shadow: 0 4px 12px rgba(239,68,68,0.15);">
                        <div style="font-size: 1.6rem; font-weight: 800; color: #ef4444;">{total - active}</div>
                        <div style="font-size: 0.78rem; color: #9ca3af;">Inactive</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                search_doc = st.text_input("🔍 Search by name or email…",
                                           placeholder="Type to filter…", key="mgr_search")
                filtered = [d for d in doctors if
                            search_doc.lower() in d["full_name"].lower() or
                            search_doc.lower() in d["email"].lower()
                            ] if search_doc else doctors

                for doc in filtered:
                    is_active   = bool(doc.get("is_active"))
                    status_col  = "#14b8a6" if is_active else "#ef4444"
                    status_lbl  = "Active" if is_active else "Inactive"
                    sp          = doc["specialty"] or "General"
                    joined      = str(doc.get("created_at", ""))[:10]

                    with st.expander(
                        f"🩺 Dr. {doc['full_name']}  ·  {sp}  ·  {doc['email']}"
                    ):
                        col_info, col_actions = st.columns([3, 2])

                        with col_info:
                            st.markdown(f"""
                            <div style="font-size: 0.85rem; color: #9ca3af; line-height: 2.1;">
                                <b style="color: #e2e8f0;">Email:</b> {doc['email']}<br>
                                <b style="color: #e2e8f0;">Specialty:</b> {sp}<br>
                                <b style="color: #e2e8f0;">Experience:</b> {doc['experience_years'] or 0} yrs<br>
                                <b style="color: #e2e8f0;">Fee:</b> ₹{doc['consultation_fee'] or 0}<br>
                                <b style="color: #e2e8f0;">Joined:</b> {joined}<br>
                                <b style="color: #e2e8f0;">Status:</b>
                                <span style="color: {status_col}; font-weight: 700;"> ● {status_lbl}</span>
                            </div>
                            """, unsafe_allow_html=True)
                            if doc.get("bio"):
                                st.caption(f"📝 {doc['bio']}")

                        with col_actions:
                            # Reset password
                            st.markdown("**🔑 Reset Password**")
                            with st.form(f"reset_pw_{doc['user_id']}"):
                                new_pw  = st.text_input("New password", type="password",
                                                        placeholder="Min 6 chars",
                                                        key=f"np_{doc['user_id']}",
                                                        label_visibility="collapsed")
                                if st.form_submit_button("Reset", type="primary", use_container_width=True):
                                    if len(new_pw) < 6:
                                        st.warning("Min 6 characters.")
                                    else:
                                        ok, msg = auth_mod.reset_doctor_password(doc["user_id"], new_pw)
                                        st.success(msg) if ok else st.error(msg)

                            # Activate / Deactivate
                            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                            if is_active:
                                if st.button("🔴 Deactivate Account",
                                             key=f"deact_{doc['user_id']}",
                                             use_container_width=True):
                                    auth_mod.toggle_user_active(doc["user_id"], False)
                                    st.warning(f"Account for Dr. {doc['full_name']} deactivated.")
                                    st.rerun()
                            else:
                                if st.button("🟢 Activate Account",
                                             key=f"act_{doc['user_id']}",
                                             use_container_width=True,
                                             type="primary"):
                                    auth_mod.toggle_user_active(doc["user_id"], True)
                                    st.success(f"Account for Dr. {doc['full_name']} activated.")
                                    st.rerun()

    # ════════════════════════════════════════════════════════════════════
    # DOCTORS — browse panel
    # ════════════════════════════════════════════════════════════════════
    elif page == "doctors":
        page_header("Doctors", "Browse specialists and their focus areas")

        doctors = db.fetch_all_doctors()
        sp_icons = {"Cardiology": "🫀", "Neurology": "🧠", "Pediatrics": "👶",
                    "Orthopedics": "🦴", "General Medicine": "⚕️", "Dermatology": "🩹",
                    "Psychiatry": "🧘", "Ophthalmology": "👁️", "Gynecology": "🌸",
                    "Oncology": "🎗️", "Gastroenterology": "🫃", "Pulmonology": "🫁",
                    "Nephrology": "🫘", "Urology": "🔬", "Endocrinology": "⚗️"}

        if doctors:
            search = st.text_input("🔍 Search doctors…", placeholder="Name or specialty",
                                   label_visibility="collapsed")
            filtered = [d for d in doctors if
                        search.lower() in d["full_name"].lower() or
                        search.lower() in (d["specialty"] or "").lower()
                        ] if search else doctors

            cols = st.columns(3)
            for i, doc in enumerate(filtered):
                sp   = doc["specialty"] or "General"
                icon = sp_icons.get(sp, "🩺")
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="doc-card">
                        <div class="doc-card-icon">{icon}</div>
                        <div class="doc-card-specialty">{sp}</div>
                        <div class="doc-card-name">Dr. {doc['full_name']}</div>
                        <div class="doc-card-desc">
                            {doc['bio'] or 'Specialist in ' + sp + '.'}
                        </div>
                        <div style="margin-top: 0.9rem; display: flex; gap: 0.6rem; flex-wrap: wrap;">
                            <span style="font-size: 0.75rem; color: #6b7280; display: flex; align-items: center; gap: 3px;">
                                🏆 {doc['experience_years'] or 0} yrs exp
                            </span>
                            <span style="font-size: 0.75rem; color: #6b7280; display: flex; align-items: center; gap: 3px;">
                                💰 ₹{doc['consultation_fee'] or 0}
                            </span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        else:
            st.info("No doctors registered.")

    # ════════════════════════════════════════════════════════════════════
    # PATIENTS — full patient management panel
    # ════════════════════════════════════════════════════════════════════
    elif page == "patients":
        page_header("Patients", "Full overview of all registered patients")

        patients = db.fetch_all_patients()
        all_appts = db.fetch_appointments()
        all_records = db.fetch_health_records()

        if not patients:
            st.info("No patients registered yet.")
        else:
            total_pat    = len(patients)
            active_pat   = sum(1 for p in patients if p.get("is_active"))
            total_appts  = len(all_appts)
            total_recs   = len(all_records)

            # Summary stats
            stat_cards([
                ("👥", "Total Patients",   str(total_pat)),
                ("✅", "Active Patients",  str(active_pat)),
                ("📅", "Total Appt.",      str(total_appts)),
                ("📋", "Health Records",   str(total_recs)),
            ])

            st.markdown("<br>", unsafe_allow_html=True)

            # Search
            search_p = st.text_input("🔍 Search patients by name or email…", key="admin_pat_search")
            filtered_pats = [p for p in patients if
                             not search_p or
                             search_p.lower() in p["full_name"].lower() or
                             search_p.lower() in (p["email"] or "").lower()]

            for p in filtered_pats:
                is_active   = bool(p.get("is_active"))
                status_col  = "#14b8a6" if is_active else "#ef4444"
                status_lbl  = "Active" if is_active else "Inactive"
                joined      = str(p.get("created_at", ""))[:10]

                with st.expander(
                    f"👤 {p['full_name']}  ·  {p['email']}  ·  "
                    f"📅 {p['appt_count']} appt  ·  📋 {p['record_count']} records"
                ):
                    col_info, col_records = st.columns([1, 2])

                    with col_info:
                        st.markdown(f"""
                        <div style="font-size: 0.85rem; color: #475569; line-height: 2.2;">
                            <b style="color: #0f172a;">Email:</b> {p['email']}<br>
                            <b style="color: #0f172a;">Gender:</b> {p.get('gender') or '—'}<br>
                            <b style="color: #0f172a;">DOB:</b> {p.get('dob') or '—'}<br>
                            <b style="color: #0f172a;">Phone:</b> {p.get('phone') or '—'}<br>
                            <b style="color: #0f172a;">Joined:</b> {joined}<br>
                            <b style="color: #0f172a;">Status:</b>
                            <span style="color: {status_col}; font-weight: 700;"> ● {status_lbl}</span>
                        </div>
                        """, unsafe_allow_html=True)

                        # Patient's appointments
                        pat_appts = [a for a in all_appts if a["patient_id"] == p["id"]]
                        if pat_appts:
                            st.markdown("**📅 Appointments:**")
                            for a in pat_appts[:5]:
                                badge = status_badge(a["status"] or "pending")
                                st.markdown(
                                    f"• Dr. {a['doctor_name']} · {a['scheduled_date']} "
                                    f"@ {str(a['start_time'])[:5]} — {badge}",
                                    unsafe_allow_html=True
                                )
                            if len(pat_appts) > 5:
                                st.caption(f"… and {len(pat_appts)-5} more.")

                    with col_records:
                        pat_recs = [r for r in all_records if r["patient_id"] == p["id"]]
                        if pat_recs:
                            st.markdown("**📋 Health Records:**")
                            for r in pat_recs[:5]:
                                st.markdown(f"""
                                <div style="background: #ffffff;
                                            border: 1.5px solid #e2e8f0;
                                            border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 8px;
                                            font-size: 0.85rem; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                                    <b style="color: #0369a1;">{str(r['recorded_at'])[:10]}</b>
                                    &nbsp;·&nbsp;Dr. {r['doctor_name'] or 'N/A'}
                                    {"  ·  <span style='color:#0f172a;font-weight:600;'>Dx: " + (r['diagnosis'] or '') + "</span>" if r['diagnosis'] else ''}<br>
                                    <span style="color: #475569;">
                                        ❤️ {r['heart_rate'] or '—'} bpm &nbsp;|&nbsp;
                                        🩸 {r['blood_pressure'] or '—'} &nbsp;|&nbsp;
                                        💨 SpO₂ {r['pulse_oximetry'] or '—'}%
                                    </span>
                                    {f'<br><span style="color: #64748b;">{r["notes"]}</span>' if r['notes'] else ''}
                                </div>
                                """, unsafe_allow_html=True)
                            if len(pat_recs) > 5:
                                st.caption(f"… and {len(pat_recs)-5} more records.")
                        else:
                            st.info("No health records for this patient.")

    # ════════════════════════════════════════════════════════════════════
    # APPOINTMENTS — full appointment management panel
    # ════════════════════════════════════════════════════════════════════
    elif page == "appointments":
        page_header("Appointments", "Manage all appointments")

        col_f1, col_f2 = st.columns(2)
        date_filter   = col_f1.date_input("Filter by Date", value=None, key="af_date")
        status_filter = col_f2.selectbox("Filter by Status",
                                          ["All", "pending", "confirmed", "completed", "cancelled"],
                                          key="af_status_top")

        appts = db.fetch_appointments(date_filter=date_filter if date_filter else None)
        if status_filter != "All":
            appts = [a for a in appts if (a["status"] or "pending") == status_filter]

        if appts:
            rows = []
            for a in appts:
                rows.append({
                    "#":        a["id"],
                    "Patient":  f"{a['patient_name']} (ID: #{a['patient_id']})",
                    "Doctor":   f"Dr. {a['doctor_name']} (ID: #{a['doctor_id']})",
                    "Date":     str(a["scheduled_date"]),
                    "Time":     str(a["start_time"]),
                    "Status":   (a["status"] or "pending").title(),
                    "Reason":   a["reason"] or "—",
                })
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)

            st.markdown("<br>**Update Appointment Status**", unsafe_allow_html=True)
            for a in appts[:10]:
                status = a["status"] or "pending"
                badge  = status_badge(status)
                with st.expander(
                    f"#{a['id']}  {a['patient_name']} (ID:#{a['patient_id']}) → Dr. {a['doctor_name']} (ID:#{a['doctor_id']})  |  {a['scheduled_date']}"
                ):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.markdown(f"**Patient ID:** #{a['patient_id']} | **Doctor ID:** #{a['doctor_id']}")
                    c1.markdown(f"**Reason:** {a['reason'] or '—'}")
                    c2.markdown(f"**Status:** {badge}", unsafe_allow_html=True)
                    opts  = ["pending", "confirmed", "completed", "cancelled"]
                    new_s = c3.selectbox("", opts,
                                         index=opts.index(status if status in opts else "pending"),
                                         key=f"appt_s_{a['id']}", label_visibility="collapsed")
                    if st.button("Update", key=f"upd_{a['id']}", type="primary"):
                        db.update_appointment_status(a["id"], new_s)
                        st.success("Updated!")
                        st.rerun()
        else:
            st.info("No appointments found.")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: ORDERS - Manage medicine orders
    # ════════════════════════════════════════════════════════════════════
    elif page == "orders":
        page_header("📦 Medicine Orders", "Manage patient medicine orders")

        orders = db.fetch_all_orders()

        if not orders:
            st.info("No medicine orders yet.")
        else:
            # Stats
            pending_count = sum(1 for o in orders if o['status'] == 'pending')
            preparing_count = sum(1 for o in orders if o['status'] == 'preparing')
            ready_count = sum(1 for o in orders if o['status'] == 'ready')
            delivered_count = sum(1 for o in orders if o['status'] == 'delivered')

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Pending", pending_count)
            col2.metric("Preparing", preparing_count)
            col3.metric("Ready", ready_count)
            col4.metric("Delivered", delivered_count)

            st.markdown("---")

            # Filter by status
            status_filter = st.selectbox("Filter by Status", ["All", "pending", "preparing", "ready", "delivered", "cancelled"])

            filtered_orders = orders if status_filter == "All" else [o for o in orders if o['status'] == status_filter]

            st.markdown(f"**Showing {len(filtered_orders)} order(s)**")

            for order in filtered_orders:
                status_colors = {
                    'pending': '#f59e0b',
                    'preparing': '#3b82f6',
                    'ready': '#8b5cf6',
                    'delivered': '#22c55e',
                    'cancelled': '#ef4444'
                }
                status_color = status_colors.get(order['status'], '#6b7280')

                with st.container():
                    st.markdown(f"""
                    <div style="background: #ffffff; border: 1.5px solid #e2e8f0;
                                border-radius: 12px; padding: 1rem; margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b style="color:#0369a1; font-size: 1.1rem;">Order #{order['id']}</b>
                                <span style="color:#0f172a; font-weight:600; margin-left: 15px;">{order['medicine_name']}</span>
                                <span style="background:#e0f2fe; color:#0369a1; border:1px solid #bae6fd; padding:2px 8px; border-radius:12px; font-size:0.75rem; font-weight:600; margin-left: 10px;">{order['category']}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {status_color}; font-weight: 700; text-transform: uppercase; font-size: 0.85rem;">{order['status']}</div>
                                <div style="color:#0f172a; font-weight:700; font-size: 1rem;">₹{order['total_price']}</div>
                            </div>
                        </div>
                        <div style="font-size: 0.85rem; color:#475569; margin-top: 6px;">
                            <b style="color:#0f172a;">Patient:</b> {order['patient_name']} | {order['patient_email']} | {order['patient_phone']}
                        </div>
                        <div style="font-size: 0.85rem; color:#475569; margin-top: 3px;">
                            <b style="color:#0f172a;">Qty:</b> {order['quantity']} x ₹{order['unit_price']} | <b>Ordered:</b> {order['order_date']}
                        </div>
                        <div style="font-size: 0.82rem; color:#334155; margin-top: 3px;">
                            📍 {order['delivery_address']}
                        </div>
                        {f"<div style='font-size:0.8rem;color:#dc2626;margin-top:3px;'>📝 {order['notes']}</div>" if order.get('notes') else ""}
                    </div>
                    """, unsafe_allow_html=True)

                # Action buttons based on status
                col_act1, col_act2, col_act3, col_act4 = st.columns(4)

                with col_act1:
                    if order['status'] == 'pending':
                        if st.button(f"📦 Prepare", key=f"prepare_{order['id']}", use_container_width=True):
                            success, msg = db.update_order_status(order['id'], 'preparing')
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                with col_act2:
                    if order['status'] == 'preparing':
                        if st.button(f"✅ Ready", key=f"ready_{order['id']}", use_container_width=True):
                            success, msg = db.update_order_status(order['id'], 'ready')
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                with col_act3:
                    if order['status'] == 'ready':
                        if st.button(f"🚚 Delivered", key=f"delivered_{order['id']}", use_container_width=True):
                            success, msg = db.update_order_status(order['id'], 'delivered')
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                with col_act4:
                    if order['status'] in ['pending', 'preparing']:
                        if st.button(f"❌ Cancel", key=f"cancel_admin_{order['id']}", use_container_width=True):
                            success, msg = db.cancel_order(order['id'])
                            if success:
                                st.success(msg)
                                st.rerun()
                            else:
                                st.error(msg)

                st.markdown("---")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: AI CARE
    # ════════════════════════════════════════════════════════════════════
    elif page == "ai_care":
        ai_care.render_ai_care_tab(user)

    # Standalone MEDICINES page (Admin - Full CRUD)
    elif page == "medicines":
        page_header("💊 Medicines", "Manage pharmacy inventory")

        # Get all medicines
        medicines = db.fetch_all_medicines()

        # Search and filters
        col_search1, col_search2, col_search3 = st.columns([2, 1, 1])
        with col_search1:
            search_term = st.text_input("🔍 Search medicines", placeholder="Search by name...")
        with col_search2:
            category_filter = st.selectbox("Category", ["All"] + list(set(m.get("category", "General") for m in medicines)))
        with col_search3:
            stock_filter = st.selectbox("Stock", ["All", "In Stock", "Low Stock", "Out of Stock"])

        # Apply filters
        filtered_meds = medicines
        if search_term:
            filtered_meds = [m for m in filtered_meds if search_term.lower() in m.get("name", "").lower()]
        if category_filter != "All":
            filtered_meds = [m for m in filtered_meds if m.get("category") == category_filter]
        if stock_filter == "In Stock":
            filtered_meds = [m for m in filtered_meds if m.get("stock_quantity", 0) > 10]
        elif stock_filter == "Low Stock":
            filtered_meds = [m for m in filtered_meds if 0 < m.get("stock_quantity", 0) <= 10]
        elif stock_filter == "Out of Stock":
            filtered_meds = [m for m in filtered_meds if m.get("stock_quantity", 0) == 0]

        # Stats
        total_meds = len(filtered_meds)
        total_value = sum(m.get("unit_price", 0) * m.get("stock_quantity", 0) for m in filtered_meds)
        low_stock = sum(1 for m in filtered_meds if 0 < m.get("stock_quantity", 0) <= 10)

        stat_cards([
            ("💊", "Medicines", str(total_meds)),
            ("₹", "Total Value", f"₹{total_value:,.0f}"),
            ("⚠️", "Low Stock", str(low_stock)),
        ])

        st.markdown("---")

        # Add New Medicine Button
        col_add_btn, col_view = st.columns([1, 4])
        with col_add_btn:
            if st.button("➕ Add Medicine", type="primary", use_container_width=True):
                st.session_state["show_add_medicine"] = True

        # Show add form if button clicked
        if st.session_state.get("show_add_medicine", False):
            with st.expander("➕ Add New Medicine", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    add_name = st.text_input("Medicine Name *", key="add_med_name")
                    add_category = st.selectbox("Category", ["General", "Pain Relief", "Antibiotics", "Cardiac", "Diabetes", "Respiratory", "Gastrointestinal", "Neurological", "Dermatology", "Other"], key="add_med_cat")
                    add_manufacturer = st.text_input("Manufacturer", key="add_med_man")
                with col2:
                    add_composition = st.text_input("Composition", key="add_med_comp")
                    add_dosage = st.text_input("Dosage", key="add_med_dos")
                    add_unit = st.selectbox("Unit", ["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"], key="add_med_unit")

                col3, col4 = st.columns(2)
                with col3:
                    add_price = st.number_input("Price (₹) *", min_value=0.0, step=1.0, key="add_med_price")
                    add_expiry = st.date_input("Expiry Date", key="add_med_expiry")
                with col4:
                    add_stock = st.number_input("Stock Quantity *", min_value=0, step=10, key="add_med_stock")
                    add_description = st.text_area("Description", key="add_med_desc")

                # Image upload
                add_image = st.file_uploader("Upload Medicine Image (Optional)", type=["jpg", "jpeg", "png", "webp"], key="add_med_image")
                add_image_url = None
                if add_image:
                    from pathlib import Path
                    static_dir = Path("static/medicines")
                    static_dir.mkdir(parents=True, exist_ok=True)
                    img_path = static_dir / f"{add_name.replace(' ', '_')}_{add_image.name}"
                    with open(img_path, "wb") as f:
                        f.write(add_image.getbuffer())
                    add_image_url = str(img_path)
                    st.success(f"Image uploaded: {add_image.name}")

                col_btns = st.columns([1, 1])
                with col_btns[0]:
                    if st.button("✅ Save Medicine", type="primary", use_container_width=True, key="save_med_btn"):
                        if add_name and add_price >= 0 and add_stock >= 0:
                            success, msg = db.add_medicine(
                                add_name, add_category, add_manufacturer, add_composition,
                                add_dosage, add_price, add_stock,
                                str(add_expiry) if add_expiry else None, add_description, add_image_url
                            )
                            if success:
                                st.success("Medicine added successfully!")
                                st.session_state["show_add_medicine"] = False
                                st.rerun()
                            else:
                                st.error(f"Error: {msg}")
                        else:
                            st.warning("Please fill required fields (*)")
                with col_btns[1]:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_add_med"):
                        st.session_state["show_add_medicine"] = False
                        st.rerun()

        st.markdown("---")
        st.markdown(f"### 📋 Medicines List ({len(filtered_meds)} found)")

        if not filtered_meds:
            st.warning("No medicines found.")
        else:
            # Vertical card layout like Amazon/Flipkart
            for m in filtered_meds:
                stock = m.get("stock_quantity", 0)
                stock_color = "#22c55e" if stock > 50 else "#f59e0b" if stock > 10 else "#ef4444"
                stock_text = "In Stock" if stock > 10 else "Low Stock" if stock > 0 else "Out of Stock"
                stock_icon = "✅" if stock > 10 else "⚠️" if stock > 0 else "❌"

                # Card layout with image on left, info on right
                img_url = m.get("image_url", "")

                # Use columns for layout
                col_img, col_info = st.columns([1, 5])
                with col_img:
                    if img_url and os.path.exists(img_url):
                        st.image(img_url, width=80)
                    else:
                        st.markdown('<div style="width:80px;height:80px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2rem;">💊</div>', unsafe_allow_html=True)

                with col_info:
                    st.markdown(f"""
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                        <div>
                            <div style="font-size: 1.1rem; font-weight: 700; color: #f8fafc; margin-bottom: 0.3rem;">
                                {m.get('name', 'Unknown')}
                            </div>
                            <div style="font-size: 0.8rem; color: #94a3b8; margin-bottom: 0.5rem;">
                                {m.get('category', 'General')} | {m.get('unit', 'tablet')} | {m.get('manufacturer', 'N/A')}
                            </div>
                            <div style="font-size: 0.85rem; color: #cbd5e1;">
                                {m.get('composition', 'N/A')} | {m.get('dosage', 'N/A')}
                            </div>
                        </div>
                        <div style="text-align: right; min-width: 120px;">
                            <div style="font-size: 1.4rem; font-weight: 800; color: #0ea5e9; margin-bottom: 0.3rem;">
                                ₹{m.get('unit_price', 0)}
                            </div>
                            <div style="font-size: 0.85rem; font-weight: 600; color: {stock_color};">
                                {stock_icon} {stock_text}
                            </div>
                            <div style="font-size: 0.75rem; color: #64748b;">
                                Stock: {stock}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Action buttons for admin
                    col_act1, col_act2, col_act3 = st.columns([1, 1, 1])
                    with col_act1:
                        if st.button(f"✏️ Edit", key=f"edit_{m['id']}", use_container_width=True):
                            st.session_state[f"edit_medicine_{m['id']}"] = True
                    with col_act2:
                        if st.button(f"🗑️ Delete", key=f"delete_{m['id']}", use_container_width=True):
                            st.session_state[f"confirm_delete_{m['id']}"] = True
                    with col_act3:
                        pass

                    # Edit form
                    if st.session_state.get(f"edit_medicine_{m['id']}", False):
                        with st.expander(f"✏️ Edit: {m.get('name')}", expanded=True):
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                edit_name = st.text_input("Name", value=m.get('name', ''), key=f"edit_name_{m['id']}")
                                edit_category = st.selectbox("Category", ["General", "Pain Relief", "Antibiotics", "Cardiac", "Diabetes", "Respiratory", "Gastrointestinal", "Neurological", "Dermatology", "Other"],
                                                           index=["General", "Pain Relief", "Antibiotics", "Cardiac", "Diabetes", "Respiratory", "Gastrointestinal", "Neurological", "Dermatology", "Other"].index(m.get('category', 'General')) if m.get('category') in ["General", "Pain Relief", "Antibiotics", "Cardiac", "Diabetes", "Respiratory", "Gastrointestinal", "Neurological", "Dermatology", "Other"] else 0,
                                                           key=f"edit_cat_{m['id']}")
                                edit_manufacturer = st.text_input("Manufacturer", value=m.get('manufacturer', ''), key=f"edit_man_{m['id']}")
                            with col_e2:
                                edit_composition = st.text_input("Composition", value=m.get('composition', ''), key=f"edit_comp_{m['id']}")
                                edit_dosage = st.text_input("Dosage", value=m.get('dosage', ''), key=f"edit_dos_{m['id']}")
                                edit_unit = st.selectbox("Unit", ["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"],
                                                        index=["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"].index(m.get('unit', 'tablet')) if m.get('unit') in ["tablet", "capsule", "syrup", "injection", "cream", "ointment", "drops", "inhaler"] else 0,
                                                        key=f"edit_unit_{m['id']}")

                            col_e3, col_e4 = st.columns(2)
                            with col_e3:
                                edit_price = st.number_input("Price (₹)", min_value=0.0, value=float(m.get('unit_price', 0)), step=1.0, key=f"edit_price_{m['id']}")
                                edit_expiry = st.date_input("Expiry Date", value=m.get('expiry_date', ''), key=f"edit_expiry_{m['id']}")
                            with col_e4:
                                edit_stock = st.number_input("Stock Quantity", min_value=0, value=m.get('stock_quantity', 0), step=1, key=f"edit_stock_{m['id']}")
                                edit_description = st.text_area("Description", value=m.get('description', ''), key=f"edit_desc_{m['id']}")

                                # Show current image
                                current_img = m.get('image_url', '')
                                if current_img and os.path.exists(current_img):
                                    st.image(current_img, width=150, caption="Current Image")
                                edit_new_image = st.file_uploader("Change Image (Optional)", type=["jpg", "jpeg", "png", "webp"], key=f"edit_image_{m['id']}")

                            col_e_btn1, col_e_btn2 = st.columns(2)
                            with col_e_btn1:
                                if st.button(f"✅ Update", type="primary", key=f"update_{m['id']}"):
                                    # Handle image update
                                    edit_image_url = m.get('image_url', '')
                                    if st.session_state.get(f"edit_image_{m['id']}"):
                                        uploaded_img = st.session_state[f"edit_image_{m['id']}"]
                                        if uploaded_img:
                                            from pathlib import Path
                                            static_dir = Path("static/medicines")
                                            static_dir.mkdir(parents=True, exist_ok=True)
                                            img_path = static_dir / f"{edit_name.replace(' ', '_')}_{uploaded_img.name}"
                                            with open(img_path, "wb") as f:
                                                f.write(uploaded_img.getbuffer())
                                            edit_image_url = str(img_path)

                                    success, msg = db.update_medicine(
                                        m['id'], edit_name, edit_category, edit_manufacturer,
                                        edit_composition, edit_dosage, edit_price, edit_stock,
                                        str(edit_expiry) if edit_expiry else None, edit_description, edit_image_url
                                    )
                                    if success:
                                        st.success("Medicine updated!")
                                        st.session_state[f"edit_medicine_{m['id']}"] = False
                                        st.rerun()
                                    else:
                                        st.error(f"Error: {msg}")
                            with col_e_btn2:
                                if st.button(f"Cancel", key=f"cancel_edit_{m['id']}"):
                                    st.session_state[f"edit_medicine_{m['id']}"] = False
                                    st.rerun()

                    # Delete confirmation
                    if st.session_state.get(f"confirm_delete_{m['id']}", False):
                        st.warning(f"⚠️ Are you sure you want to delete '{m.get('name')}'?")
                        col_del1, col_del2 = st.columns(2)
                        with col_del1:
                            if st.button(f"✅ Yes, Delete", type="primary", key=f"confirm_del_{m['id']}"):
                                success, msg = db.delete_medicine(m['id'])
                                if success:
                                    st.success("Medicine deleted!")
                                    st.session_state[f"confirm_delete_{m['id']}"] = False
                                    st.rerun()
                                else:
                                    st.error(f"Error: {msg}")
                        with col_del2:
                            if st.button(f"❌ No, Cancel", key=f"cancel_del_{m['id']}"):
                                st.session_state[f"confirm_delete_{m['id']}"] = False
                                st.rerun()

                    st.markdown("---")
