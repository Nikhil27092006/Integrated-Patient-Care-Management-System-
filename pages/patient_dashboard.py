import streamlit as st
import sys, os

# Add local site-packages to path FIRST (for portable packages)
local_packages = os.path.join(os.path.dirname(__file__), "..", "patient_care", "Lib", "site-packages")
if os.path.exists(local_packages):
    sys.path.insert(0, local_packages)

# Add project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import db
from datetime import time, timedelta, datetime as dt
from pages.shared_styles import (inject_css, sidebar_header, page_header,
                                  stat_cards, status_badge, sidebar_footer, medical_banner)
import ai_care

# PDF generation imports - check local packages first
REPORTLAB_AVAILABLE = False
try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    # Try alternate path
    try:
        alt_path = os.path.join(os.path.dirname(__file__), "patient_care", "Lib", "site-packages")
        if alt_path not in sys.path:
            sys.path.insert(0, alt_path)
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        REPORTLAB_AVAILABLE = True
    except ImportError:
        pass  # Will try again at runtime

def check_reportlab():
    """Check if reportlab is available, try importing from different paths."""
    global REPORTLAB_AVAILABLE
    if REPORTLAB_AVAILABLE:
        return True
    # Try again at runtime
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.pdfgen import canvas
        from reportlab.lib import colors
        REPORTLAB_AVAILABLE = True
        return True
    except ImportError:
        # Try local packages path
        try:
            local_path = os.path.join(os.path.dirname(__file__), "..", "patient_care", "Lib", "site-packages")
            if local_path not in sys.path:
                sys.path.insert(0, local_path)
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
            from reportlab.lib import colors
            REPORTLAB_AVAILABLE = True
            return True
        except ImportError:
            return False

# ── Groq AI setup ──────────────────────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()

def generate_prescription_pdf(prescriptions, patient_name, output_path="prescription.pdf", patient_info=None, doctor_info=None):
    # Try to detect reportlab at runtime
    if not check_reportlab():
        raise ImportError("reportlab is not installed. Run: pip install reportlab")

    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib import colors

    c = pdf_canvas.Canvas(output_path, pagesize=letter)
    width, height = letter

    # ========== HEADER ==========
    # Blue header bar
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.rect(0, height - 120, width, 120, fill=True, stroke=False)

    # Clinic name
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 28)
    c.drawCentredString(width/2, height - 45, "🏥 PATIENT CARE MANAGEMENT SYSTEM FOR HEALTHCARE SERVICES")

    c.setFont("Helvetica", 14)
    c.drawCentredString(width/2, height - 70, "Medical Center & Pharmacy")

    c.setFont("Helvetica", 10)
    c.drawCentredString(width/2, height - 90, "Healthcare | Pharmacy | AI Assistant")

    # ========== PATIENT INFO BOX ==========
    y = height - 150
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.setLineWidth(1)
    c.roundRect(40, y - 100, width - 80, 90, 5, fill=True, stroke=True)

    # Patient info title
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, "👤 PATIENT DETAILS")

    # Patient details
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    # Left column
    c.drawString(50, y - 45, f"Name: {patient_name}")
    if patient_info:
        c.drawString(50, y - 65, f"Age/Gender: {patient_info.get('age', 'N/A')} years / {patient_info.get('gender', 'N/A')}")
        c.drawString(50, y - 85, f"Phone: {patient_info.get('phone', 'N/A')}")
    else:
        c.drawString(50, y - 65, f"Age/Gender: N/A")
        c.drawString(50, y - 85, f"Phone: N/A")

    # Right column - Date
    c.drawString(width/2 + 20, y - 45, f"Date: {dt.now().strftime('%d-%m-%Y')}")
    c.drawString(width/2 + 20, y - 65, f"Time: {dt.now().strftime('%H:%M')}")
    c.drawString(width/2 + 20, y - 85, f"Rx No: {dt.now().strftime('%Y%m%d%H%M%S')[-10:]}")

    # ========== DOCTOR INFO BOX ==========
    y = y - 120
    c.setFillColor(colors.white)
    c.setStrokeColor(colors.HexColor("#cbd5e1"))
    c.roundRect(40, y - 70, width - 80, 60, 5, fill=True, stroke=True)

    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(50, y - 20, "👨‍⚕️ PRESCRIBING DOCTOR")

    c.setFillColor(colors.black)
    c.setFont("Helvetica", 10)

    if doctor_info:
        c.drawString(50, y - 40, f"Dr. {doctor_info.get('name', 'N/A')}")
        c.drawString(50, y - 55, f"Specialty: {doctor_info.get('specialty', 'General Medicine')}")
        c.drawString(width/2 + 20, y - 40, f"Reg. No: {doctor_info.get('reg_no', 'N/A')}")
    else:
        # Get from prescription
        if prescriptions:
            doc_name = prescriptions[0].get('doctor_name', 'N/A')
        else:
            doc_name = 'N/A'
        c.drawString(50, y - 40, f"Dr. {doc_name}")
        c.drawString(50, y - 55, f"Specialty: General Medicine")

    # ========== MEDICINES TABLE ==========
    y = y - 95
    c.setFillColor(colors.HexColor("#1e3a8a"))
    c.rect(40, y - 25, width - 80, 30, fill=True, stroke=False)

    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(50, y - 15, "Rx")

    # Table headers
    table_headers = ["Medicine Name", "Composition", "Dosage", "Frequency", "Duration", "Qty"]
    header_x = [90, 200, 320, 400, 480, 550]
    for i, header in enumerate(table_headers):
        c.drawString(header_x[i], y - 15, header)

    # Table content
    c.setFillColor(colors.black)
    c.setFont("Helvetica", 9)
    y -= 45

    for i, pres in enumerate(prescriptions):
        # Check for page break
        if y < 120:
            c.showPage()
            # Redraw header on new page
            c.setFillColor(colors.HexColor("#1e3a8a"))
            c.rect(0, height - 80, width, 80, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width/2, height - 45, "MEDICAL PRESCRIPTION (Cont.)")
            c.setFont("Helvetica", 10)
            c.drawCentredString(width/2, height - 65, f"Patient: {patient_name} | Rx No: {dt.now().strftime('%Y%m%d%H%M%S')[-10:]}")
            y = height - 120

        # Alternating row colors
        if i % 2 == 0:
            c.setFillColor(colors.HexColor("#f1f5f9"))
            c.rect(40, y - 18, width - 80, 22, fill=True, stroke=False)
        else:
            c.setFillColor(colors.white)
            c.rect(40, y - 18, width - 80, 22, fill=True, stroke=False)

        c.setFillColor(colors.black)

        # Medicine details
        med_name = str(pres.get('medicine_name', 'N/A'))[:35]
        composition = str(pres.get('composition', pres.get('medicine_name', 'N/A')))[:25]
        dosage = str(pres.get('dosageInstructions', pres.get('dosage', 'N/A')))[:15]
        frequency = str(pres.get('frequency', 'N/A'))[:12]
        duration = str(pres.get('duration', 'N/A'))[:12]
        quantity = str(pres.get('quantity', '1'))

        c.drawString(50, y, f"{i+1}. {med_name}")
        c.drawString(200, y, composition[:25])
        c.drawString(320, y, dosage)
        c.drawString(400, y, frequency)
        c.drawString(480, y, duration)
        c.drawString(550, y, quantity)

        y -= 28

    # ========== INSTRUCTIONS ==========
    y -= 20
    c.setFillColor(colors.HexColor("#fef3c7"))
    c.roundRect(40, y - 50, width - 80, 45, 5, fill=True, stroke=False)

    c.setFillColor(colors.HexColor("#92400e"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y - 20, "⚠️ INSTRUCTIONS:")

    c.setFont("Helvetica", 9)
    c.setFillColor(colors.HexColor("#78350f"))
    c.drawString(50, y - 35, "• Take medicines as prescribed by the doctor")
    c.drawString(280, y - 35, "• Complete the full course of antibiotics")
    c.drawString(50, y - 48, "• Store in a cool, dry place away from direct sunlight")
    c.drawString(280, y - 48, "• Consult doctor if symptoms persist")

    # ========== FOOTER ==========
    y = 80

    # Divider line
    c.setStrokeColor(colors.HexColor("#1e3a8a"))
    c.setLineWidth(2)
    c.line(40, y + 40, width - 40, y + 40)

    # Footer content
    c.setFillColor(colors.HexColor("#64748b"))
    c.setFont("Helvetica", 8)

    c.drawCentredString(width/2, y + 25, "Patient Care Management System for Healthcare Services")
    c.drawCentredString(width/2, y + 15, "📍 Medical Center | 📞 Emergency: +91-XXX-XXX-XXXX | 📧 care@integratedpatientcare.com")

    c.setFont("Helvetica-Oblique", 7)
    c.setFillColor(colors.gray)
    c.drawCentredString(width/2, y + 5, "This is a computer-generated prescription. Valid without signature.")

    # ========== DOCTOR SIGNATURE AREA ==========
    c.setFont("Helvetica", 10)
    c.setFillColor(colors.black)
    c.drawRightString(width - 60, y + 30, "Dr. Signature")
    c.line(width - 150, y + 35, width - 50, y + 35)

    c.save()
    return output_path


def _get_groq_llm():
    """Lazy-load the Groq LLM."""
    try:
        from langchain_groq import ChatGroq
        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            return None, "GROQ_API_KEY not found in .env"
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.3,
            api_key=api_key,
        )
        return llm, None
    except ImportError:
        return None, "langchain-groq not installed. Run: pip install langchain-groq"
    except Exception as e:
        return None, str(e)

def _ai_chat(messages: list, patient_id=None) -> str:
    """Call Groq with full message history and handle structured queries."""
    # Get the latest user message
    latest_msg = ""
    for m in reversed(messages):
        if m["role"] == "user":
            latest_msg = m["content"].lower()
            break

    # Handle structured queries
    if patient_id:
        # List doctors
        if any(kw in latest_msg for kw in ["list doctors", "show doctors", "available doctors", "all doctors", "doctors list"]):
            doctors = db.fetch_all_doctors()
            if not doctors:
                return "No doctors available yet."
            response = "Here are our available doctors:\n\n"
            for d in doctors:
                response += f"• **Dr. {d['full_name']}** - {d['specialty'] or 'General Medicine'}\n"
                response += f"  💰 Fee: ₹{d['consultation_fee']} | 🏆 Experience: {d['experience_years']} years\n\n"
            return response

        # Highest fee / top doctors
        if any(kw in latest_msg for kw in ["highest fee", "top doctors", "most expensive", "top 3"]):
            doctors = db.fetch_all_doctors()
            if doctors:
                sorted_docs = sorted(doctors, key=lambda x: x.get("consultation_fee", 0), reverse=True)[:3]
                response = "Here are the top 3 doctors by consultation fee:\n\n"
                for i, d in enumerate(sorted_docs, 1):
                    response += f"**{i}. Dr. {d['full_name']}** - ₹{d['consultation_fee']}/visit\n"
                    response += f"   Specialty: {d['specialty'] or 'General'} | Experience: {d['experience_years']} years\n\n"
                return response
            return "No doctors available."

        # My appointments / upcoming appointments
        if any(kw in latest_msg for kw in ["my appointments", "upcoming appointment", "show my appointments", "list appointments"]):
            appts = db.fetch_appointments(patient_id=patient_id)
            if not appts:
                return "You don't have any appointments yet."
            upcoming = [a for a in appts if str(a["scheduled_date"]) >= str(dt.today().date())]
            if not upcoming:
                return "You don't have any upcoming appointments."
            response = "Your upcoming appointments:\n\n"
            for a in upcoming:
                status_icon = {"confirmed": "✅", "pending": "⏳", "completed": "✔️"}.get(a.get("status", ""), "📅")
                response += f"{status_icon} **{a['scheduled_date']}** at {str(a['start_time'])[:5]}\n"
                response += f"   Dr. {a['doctor_name']} - {a.get('reason', 'Consultation')}\n\n"
            return response

        # Completed appointments count
        if any(kw in latest_msg for kw in ["completed appointments", "how many completed", "appointments done", "finished appointments"]):
            appts = db.fetch_appointments(patient_id=patient_id)
            completed = [a for a in appts if a.get("status") == "completed"]
            return f"You have **{len(completed)}** completed appointment(s)."

        # Pending appointments count
        if any(kw in latest_msg for kw in ["pending appointments", "how many pending", "waiting appointments"]):
            appts = db.fetch_appointments(patient_id=patient_id)
            pending = [a for a in appts if a.get("status") == "pending"]
            return f"You have **{len(pending)}** pending appointment(s) waiting for confirmation."

        # Health condition / health status
        if any(kw in latest_msg for kw in ["health condition", "my health", "health status", "medical condition", "my records", "health records"]):
            records = db.fetch_health_records(patient_id=patient_id)
            if not records:
                return "You don't have any health records yet. Please consult a doctor to get your health assessment."
            latest = records[0]  # Most recent
            response = "Based on your latest health record:\n\n"
            response += f"📊 **Heart Rate:** {latest.get('heart_rate', 'N/A')} bpm\n"
            response += f"💉 **Blood Pressure:** {latest.get('blood_pressure', 'N/A')} mmHg\n"
            response += f"🫁 **Pulse Oximetry:** {latest.get('pulse_oximetry', 'N/A')}%\n"
            response += f"❤️ **Ejection Fraction:** {latest.get('ejection_fraction', 'N/A')}%\n"
            response += f"💪 **Cardiac Output:** {latest.get('cardiac_output', 'N/A')} L/min\n"
            if latest.get('diagnosis'):
                response += f"\n📋 **Diagnosis:** {latest['diagnosis']}\n"
            if latest.get('notes'):
                response += f"📝 **Notes:** {latest['notes']}\n"
            response += "\n_For specific concerns, please consult your doctor._"
            return response

        # Book appointment - detect intent and create appointment
        if any(kw in latest_msg for kw in ["book appointment", "create appointment", "schedule appointment", "book an appointment", "need appointment", "want to book"]):
            doctors = db.fetch_all_doctors()
            if not doctors:
                return "⚠️ No doctors available. Please load doctors first from Edit Profile tab, or try again later."

            # Try to find doctor name in the message
            selected_doctor = None
            for d in doctors:
                # Check both full name and just first name
                doc_first_name = d['full_name'].split()[1].lower() if len(d['full_name'].split()) > 1 else d['full_name'].lower()
                if d['full_name'].lower() in latest_msg or doc_first_name in latest_msg:
                    selected_doctor = d
                    break

            if not selected_doctor:
                # Use the first available doctor automatically
                selected_doctor = doctors[0]
                # List doctors and confirm
                response = "I'll book an appointment for you with the first available doctor. Here's the list:\n\n"
                for i, d in enumerate(doctors[:5]):
                    response += f"{i+1}. **Dr. {d['full_name']}** - {d['specialty'] or 'General'} (₹{d['consultation_fee']})\n"
                response += f"\nI'll book with **Dr. {selected_doctor['full_name']}**. Say 'yes' to confirm or tell me which doctor you prefer."
                return response

            # Check for confirmation (yes, confirm, proceed)
            if any(kw in latest_msg for kw in ["yes", "confirm", "proceed", "ok", "sure", "okay"]):
                # Book with previously selected doctor or first one
                if selected_doctor is None and doctors:
                    selected_doctor = doctors[0]

            # Book with selected doctor
            tomorrow = dt.today().date() + timedelta(days=1)

            # Try to find a date in message
            import re
            date_match = re.search(r'(\d{4}-\d{2}-\d{2})', latest_msg)
            if date_match:
                book_date = date_match.group(1)
            else:
                book_date = str(tomorrow)

            # Check for slot conflicts
            if db.check_slot_conflict(selected_doctor['id'], book_date, "10:00:00"):
                # Try next available slot
                slot = "14:00:00"
                end_slot = "14:30:00"
                if db.check_slot_conflict(selected_doctor['id'], book_date, "14:00:00"):
                    slot = "09:00:00"
                    end_slot = "09:30:00"
            else:
                slot = "10:00:00"
                end_slot = "10:30:00"

            reason = "Booked via AI Care Chat"

            # Debug: log the booking attempt
            print(f"DEBUG: Booking appointment - Patient: {patient_id}, Doctor: {selected_doctor['id']}, Date: {book_date}, Slot: {slot}")

            success, msg = db.book_appointment(patient_id, selected_doctor['id'], book_date, slot, end_slot, reason)

            if success:
                return f"✅ Appointment Booked Successfully!\n\n📅 **Date:** {book_date}\n⏰ **Time:** {slot[:5]}\n👨‍⚕️ **Doctor:** Dr. {selected_doctor['full_name']}\n🩺 **Specialty:** {selected_doctor.get('specialty', 'General Medicine')}\n\nYour appointment status is **PENDING**. The doctor will confirm soon.\n\nYou can view it in the 'Appointments' tab."
            else:
                return f"❌ Booking Failed: {msg}\n\nPlease try again or book manually from the Appointments page."

    # Fall back to general AI chat
    llm, err = _get_groq_llm()
    if err:
        return f"⚠️ AI unavailable: {err}"
    try:
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        lc_msgs = [
            SystemMessage(content=(
                "You are SmartCare AI, a helpful medical assistant integrated into PCMHS "
                "(Patient Care Management System for Healthcare Services). You help patients understand "
                "general health topics, explain medical terms, and guide them on using the platform. "
                "Always remind users you are NOT a doctor and cannot diagnose or prescribe. "
                "For emergencies, always direct them to call emergency services. "
                "Keep replies concise, friendly and medically accurate."
            ))
        ]
        for m in messages:
            if m["role"] == "user":
                lc_msgs.append(HumanMessage(content=m["content"]))
            elif m["role"] == "assistant":
                lc_msgs.append(AIMessage(content=m["content"]))
        response = llm.invoke(lc_msgs)
        return response.content
    except Exception as e:
        return f"⚠️ Error: {e}"

# ── Weekly calendar helper ──────────────────────────────────────────────────────
def _weekly_calendar(appts: list, week_start):
    days      = [week_start + timedelta(days=i) for i in range(6)]
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    today     = dt.today().date()
    cal       = {str(d): [] for d in days}
    for a in appts:
        ds = str(a["scheduled_date"])
        if ds in cal:
            cal[ds].append(a)

    cols = st.columns(6)
    for i, (d, col) in enumerate(zip(days, cols)):
        is_today = (d == today)
        hdr_col  = "#0369a1" if is_today else "#64748b"
        border   = "#7dd3fc" if is_today else "#e2e8f0"
        bg       = "#f0f9ff" if is_today else "#ffffff"

        events = ""
        for a in cal[str(d)]:
            s_color = {"confirmed":"#059669","pending":"#d97706",
                       "completed":"#0369a1","cancelled":"#dc2626"}.get(
                           a.get("status","pending"), "#64748b")
            events += f"""
            <div class="cal-event" style="border-left-color: {s_color}; background:#ffffff; color:#0f172a; border: 1px solid #e2e8f0; border-left: 4px solid {s_color};">
                <b style="color:#0f172a;">{str(a['start_time'])[:5]}</b> <span style="color:#0f172a;">{a['doctor_name']}</span><br>
                <span style="color:#64748b;">{a.get('reason','') or ''}</span>
            </div>"""

        with col:
            st.markdown(f"""
            <div style="background:{bg};border:1.5px solid {border};border-radius:12px;
                        padding:0.7rem 0.6rem;min-height:140px;box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                <div style="font-size:0.7rem;font-weight:700;color:{hdr_col};
                            text-transform:uppercase;margin-bottom:3px;">{day_names[i]}</div>
                <div style="font-size:0.9rem;font-weight:700;color:#0f172a;margin-bottom:8px;">
                    {d.strftime('%d')} <span style="font-size:0.65rem;color:#64748b;">{d.strftime('%b')}</span>
                </div>
                {events or '<div style="font-size:0.7rem;color:#94a3b8;margin-top:4px;">—</div>'}
            </div>
            """, unsafe_allow_html=True)

# ── Health Vitals Display with Animations ─────────────────────────────────────
def _health_vitals_card(records):
    """Display health vitals with animated icons and ECG effects."""
    if not records:
        return None

    r = records[0]

    # Create vital cards with animations
    st.markdown("""
    <style>
    .vitals-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 1rem;
        margin: 1rem 0;
    }
    @media (max-width: 768px) {
        .vitals-grid { grid-template-columns: repeat(2, 1fr); }
    }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="vital-card" style="border-left: 4px solid #ef4444;">
            <span class="vital-icon" style="animation: heartbeat 1.2s ease-in-out infinite;">❤️</span>
            <div class="vital-label">Heart Rate</div>
            <div class="vital-value">{r['heart_rate'] or '—'}<span class="vital-unit"> bpm</span></div>
            <div class="ecg-pqrst" style="height: 35px; margin-top: 10px;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="vital-card" style="border-left: 4px solid #8b5cf6;">
            <span class="vital-icon" style="animation: bp-pulse 1s ease-in-out infinite;">🩸</span>
            <div class="vital-label">Blood Pressure</div>
            <div class="vital-value" style="font-size: 1.3rem;">{r["blood_pressure"] or "—"}</div>
            <div class="pulse-line" style="margin-top: 10px; height: 30px;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="vital-card" style="border-left: 4px solid #0ea5e9;">
            <span class="vital-icon">
                <span class="oxygen-bubble">💨</span>
            </span>
            <div class="vital-label">SpO₂</div>
            <div class="vital-value">{r['pulse_oximetry'] or '—'}<span class="vital-unit">%</span></div>
            <div class="spo2-ring" style="margin: 10px auto 0; width: 40px; height: 40px;"></div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="vital-card" style="border-left: 4px solid #14b8a6;">
            <span class="vital-icon" style="animation: heartbeat 1.5s ease-in-out infinite;">🫀</span>
            <div class="vital-label">Ejection Fraction</div>
            <div class="vital-value">{r['ejection_fraction'] or '—'}<span class="vital-unit">%</span></div>
            <div style="margin-top: 10px; display: flex; align-items: center; justify-content: center; gap: 6px;">
                <span class="heart-monitor"></span>
                <span style="font-size: 0.65rem; color: #14b8a6; text-transform: uppercase;">Normal</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ── Main render ────────────────────────────────────────────────────────────────
def render():
    inject_css()
    user = st.session_state.user_data
    sidebar_header("Patient", user["name"])

    PAGES = {
        "My Health":      "health",
        "AI Assistant":   "chat",
        "Appointments":   "appointments",
        "My Medicines":   "medicines",
        "Find Doctors":   "doctors",
        "Shop Medicines": "shop",
        "My Orders":      "orders",
    }
    if "patient_page" not in st.session_state:
        st.session_state.patient_page = "health"

    with st.sidebar:
        st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

        # ── Live notification: confirmed / new health records ──────────
        appts_all = db.fetch_appointments(patient_id=user["id"])
        new_confirmed = [a for a in appts_all if (a["status"] or "") == "confirmed"]
        records_all   = db.fetch_health_records(patient_id=user["id"])

        seen_confirmed = st.session_state.get("_seen_confirmed", set())
        new_notifs = [a for a in new_confirmed if a["id"] not in seen_confirmed]
        if new_notifs:
            st.markdown(f"""
            <div class="notification-toast">
                ✅ {len(new_notifs)} appointment(s) confirmed by doctor!
            </div>
            """, unsafe_allow_html=True)

        seen_records = st.session_state.get("_seen_records", set())
        new_recs = [r for r in records_all if r["id"] not in seen_records]
        if new_recs:
            st.markdown(f"""
            <div class="notification-toast" style="color: #0ea5e9; border-color: rgba(14,165,233,0.35); background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(20,184,166,0.1));">
                📋 {len(new_recs)} new health record(s) added by your doctor!
            </div>
            """, unsafe_allow_html=True)

        user_id = user.get("id", 0)
        for label, key in PAGES.items():
            is_active = (st.session_state.patient_page == key)
            kind = "primary" if is_active else "secondary"
            if st.button(label, key=f"pnav_{key}", use_container_width=True, type=kind):
                st.session_state.patient_page = key
                # Reset voice panel when leaving chat page
                if key != "chat":
                    voice_key = f"voice_active_patient_{user_id}"
                    st.session_state[voice_key] = False
                # Mark as seen when they navigate to appointments / health
                if key == "appointments":
                    st.session_state["_seen_confirmed"] = {a["id"] for a in new_confirmed}
                if key == "health":
                    st.session_state["_seen_records"] = {r["id"] for r in records_all}
                st.rerun()

        st.markdown("<hr style='border-color:rgba(14,165,233,0.15);margin:0.8rem 0;'>",
                    unsafe_allow_html=True)
        if st.button("↩  Log out", key="pat_logout", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.user_data = None
            st.rerun()
        sidebar_footer()

    page = st.session_state.patient_page

    # ════════════════════════════════════════════════════════════════════
    # PAGE: MY HEALTH
    # ════════════════════════════════════════════════════════════════════
    if page == "health":
        # Animated medical elements header
        medical_banner("Patient")

        page_header(f"My Health Dashboard", f"Personal overview for {user['name']} (Patient ID: #{user['id']})")

        records  = db.fetch_health_records(patient_id=user["id"])
        appts    = db.fetch_appointments(patient_id=user["id"])
        _today_str = str(dt.today().date())
        upcoming = [a for a in appts if str(a["scheduled_date"]) >= _today_str]
        confirmed_appts = [a for a in upcoming if (a["status"] or "") == "confirmed"]
        # Mark records as seen
        st.session_state["_seen_records"] = {r["id"] for r in records}

        stat_cards([
            ("V", "Vitals Logged",        str(len(records))),
            ("A", "Upcoming Appointments", str(len(upcoming))),
            ("C", "Confirmed Appts",       str(len(confirmed_appts))),
            ("S", "General Status",        "Good" if records else "Unknown"),
        ])

        # Alert: upcoming confirmed appointment with animation
        if confirmed_appts:
            next_c = sorted(confirmed_appts, key=lambda a: str(a["scheduled_date"]))[0]
            st.markdown(f"""
            <div style="background: #f0fdf4;
                        border: 1.5px solid #a7f3d0;
                        border-radius: 14px; padding: 1rem 1.4rem; margin: 1rem 0;
                        box-shadow: 0 2px 10px rgba(5,150,105,0.08); animation: fadeSlideUp 0.5s ease;">
                <div style="display: flex; align-items: center; gap: 12px;">
                    <span style="font-size: 1.6rem; animation: heartbeat 1.5s ease-in-out infinite;">📅</span>
                    <div>
                        <b style="color:#059669; font-size: 0.95rem;">Upcoming Confirmed Appointment</b>
                        <div style="font-size: 0.85rem; color: #334155; margin-top: 4px;">
                            Dr. {next_c['doctor_name']} · {next_c['scheduled_date']} @ {str(next_c['start_time'])[:5]}
                            — {next_c['reason'] or ''}
                        </div>
                    </div>
                    <span class="heart-monitor" style="margin-left: auto;"></span>
                </div>
            </div>
            """, unsafe_allow_html=True)

        # Show upcoming appointments summary on dashboard
        if upcoming:
            st.markdown("### 📅 Your Appointments")
            for a in upcoming[:3]:  # Show first 3 upcoming
                status = a["status"] or "pending"
                icon = {"confirmed": "✅", "pending": "⏳", "completed": "✔️"}.get(status, "📅")
                st.markdown(f"""
                <div style="background: #ffffff; border: 1.5px solid #e2e8f0;
                            border-radius: 10px; padding: 0.8rem 1rem; margin: 0.4rem 0; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
                    <span style="margin-right: 8px;">{icon}</span>
                    <b style="color:#0f172a;">{a['scheduled_date']}</b> <span style="color:#334155;">at {str(a['start_time'])[:5]} —</span>
                    <span style="color:#0f172a; font-weight:600;">Dr. {a['doctor_name']}</span> <span style="color:#64748b;">({status})</span>
                </div>
                """, unsafe_allow_html=True)
            if len(upcoming) > 3:
                st.caption(f"+ {len(upcoming) - 3} more appointments")

        st.markdown("<br>", unsafe_allow_html=True)
        tab_vit, tab_prof = st.tabs(["📊 Vitals & Timeline", "⚙️ Edit Profile"])

        with tab_vit:
            if records:
                # Enhanced vitals display
                _health_vitals_card(records)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="content-card-title">📋 Medical History Timeline</div>', unsafe_allow_html=True)
                for i, rec in enumerate(records):
                    with st.expander(f"📋 Record #{i+1} · {str(rec['recorded_at'])[:16]} · Dr. {rec['doctor_name'] or 'N/A'}"):
                        col_a, col_b = st.columns(2)
                        col_a.markdown(f"**Diagnosis:** {rec['diagnosis'] or 'N/A'}")
                        col_a.markdown(f"**ECG:** {rec['ecg_note'] or 'N/A'}")
                        col_b.markdown(f"**Cardiac Output:** {rec['cardiac_output'] or '—'} L/min")
                        col_b.markdown(f"**Troponin:** {rec['troponin'] or '—'} ng/mL")
                        if rec["notes"]:
                            st.markdown(f"📝 **Notes:** {rec['notes']}")
            else:
                st.info("No health records logged yet. Your doctor will record them during consultations.")
                if st.button("➕ Load Sample Health Records", key="load_dummy_records"):
                    success, msg = db.add_dummy_health_records(user["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_prof:
            profile = db.get_user_profile(user["id"])
            with st.form("pat_profile_inner"):
                full_name = st.text_input("Full Name", value=profile["full_name"] if profile else "")
                phone     = st.text_input("Phone Number", value=str(profile["phone"] or "") if profile else "")
                genders   = ["", "Male", "Female", "Other"]
                g_idx     = genders.index(profile["gender"] or "") if profile and profile.get("gender") in genders else 0
                gender    = st.selectbox("Gender", genders, index=g_idx)
                # Parse DOB from profile
                dob_value = None
                if profile and profile.get("dob"):
                    try:
                        dob_value = dt.strptime(str(profile["dob"]), "%Y-%m-%d").date()
                    except:
                        dob_value = None
                dob       = st.date_input("Date of Birth", value=dob_value)
                if st.form_submit_button("Save Profile Info", type="primary"):
                    db.update_user_profile(user["id"], full_name, gender or None, str(dob) if dob else None, phone or None)
                    st.session_state.user_data["name"] = full_name
                    st.success("Profile saved successfully!")
                    st.rerun()

            st.markdown("---")
            st.markdown("### 🧪 Sample Data")
            st.caption("Load sample data to test the system")

            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("👨‍⚕️ Load Doctors", key="load_doctors", use_container_width=True):
                    success, msg = db.seed_dummy_data()
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            with col2:
                if st.button("📋 Load Appointments", key="load_appts", use_container_width=True):
                    success, msg = db.add_dummy_appointments(user["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
            with col3:
                if st.button("❤️ Load Health Records", key="load_records", use_container_width=True):
                    success, msg = db.add_dummy_health_records(user["id"])
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)

    # ════════════════════════════════════════════════════════════════════
    # PAGE: APPOINTMENTS
    # ════════════════════════════════════════════════════════════════════
    elif page == "appointments":
        page_header("Appointments", "Book, track and manage your slots")

        appts    = db.fetch_appointments(patient_id=user["id"])
        upcoming = [a for a in appts if str(a["scheduled_date"]) >= str(dt.today().date())]
        past     = [a for a in appts if str(a["scheduled_date"]) < str(dt.today().date())]
        # Mark confirmed as seen
        st.session_state["_seen_confirmed"] = {a["id"] for a in appts if (a["status"] or "") == "confirmed"}

        tab_bk, tab_cal, tab_list, tab_hist = st.tabs(
            ["📝 Book", "📆 Weekly Calendar", "📋 Upcoming", "🕐 History"])

        # ── Book tab ──────────────────────────────────────────────────
        with tab_bk:
            doctors = db.fetch_all_doctors()
            if not doctors:
                st.warning("No doctors available yet.")
            else:
                specialties = sorted({d["specialty"] or "General" for d in doctors})
                col_sp, col_doc = st.columns(2)
                sp_choice  = col_sp.selectbox("🏥 Specialty", ["All"] + specialties, key="bk_sp_tab")
                filtered   = doctors if sp_choice == "All" else [d for d in doctors if d["specialty"] == sp_choice]

                if filtered:
                    def _fmt_doc_name(d):
                        name = d['full_name']
                        pfx = "" if name.startswith("Dr.") else "Dr. "
                        return f"{pfx}{name} ({d['specialty'] or 'General'})"

                    doc_names   = {d["id"]: _fmt_doc_name(d) for d in filtered}
                    selected_id = col_doc.selectbox("🩺 Doctor", list(doc_names.keys()),
                                                    format_func=lambda x: doc_names[x], key="bk_doc_tab")
                    selected_doc = next((d for d in filtered if d["id"] == selected_id), None)

                    if selected_doc:
                        dname = selected_doc['full_name']
                        doc_title = dname if dname.startswith("Dr.") else f"Dr. {dname}"
                        st.markdown(f"""
                        <div class="doc-card" style="margin-bottom:1rem;">
                            <div class="doc-card-specialty">{selected_doc['specialty'] or 'General'}</div>
                            <div class="doc-card-name">{doc_title}</div>
                            <div class="doc-card-desc">{selected_doc['bio'] or 'Specialist'}</div>
                            <div style="margin-top:0.5rem;display:flex;gap:1rem;font-size:0.85rem;color:#475569;">
                                <span style="display:flex;align-items:center;gap:4px;">💰 <b style="color:#0f172a;">Fee: ₹{selected_doc['consultation_fee']}</b></span>
                                <span style="display:flex;align-items:center;gap:4px;">🏆 <b style="color:#0f172a;">Exp: {selected_doc['experience_years']} yrs</b></span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Date + slot selection with conflict highlighting
                    with st.form("bk_form_tab"):
                        c1, c2 = st.columns(2)
                        appt_date = c1.date_input("📅 Date",
                                                   min_value=dt.today().date() + timedelta(days=1),
                                                   value=dt.today().date() + timedelta(days=1))
                        ALL_SLOTS = ["09:00","09:30","10:00","10:30","11:00","11:30",
                                     "14:00","14:30","15:00","15:30","16:00","16:30"]

                        # Show booked slots greyed out
                        booked = db.get_booked_slots(selected_id, appt_date)
                        free_slots = [s for s in ALL_SLOTS if s not in booked]

                        if not free_slots:
                            c2.warning("No available slots on this date. Pick another date.")
                            free_slots = ALL_SLOTS  # fallback so form renders

                        slot   = c2.selectbox("🕐 Available Slot", free_slots)
                        reason = st.text_input("Reason for visit", placeholder="Symptoms or check-up type")
                        sh, sm = map(int, slot.split(":"))
                        end_t  = time((sh + (sm + 30) // 60) % 24, (sm + 30) % 60).strftime("%H:%M")

                        if booked:
                            st.markdown(f"""
                            <div style="font-size:0.78rem;color:#f59e0b;padding:6px 0;
                                        display:flex;align-items:center;gap:6px;">
                                ⚠️ {len(booked)} slot(s) already taken: {', '.join(booked)}
                            </div>
                            """, unsafe_allow_html=True)

                        if st.form_submit_button("✅ Confirm Appointment Booking", type="primary"):
                            if not reason:
                                st.warning("Please specify a reason.")
                            elif db.check_slot_conflict(selected_id, appt_date, slot):
                                st.error("⚠️ This slot was just taken. Please choose another time.")
                            else:
                                ok, msg = db.book_appointment(
                                    user["id"], selected_id, appt_date, slot, end_t, reason)
                                if ok:
                                    st.success(f"✅ {msg} — Your doctor will confirm soon.")
                                    st.balloons()
                                    st.rerun()
                                else:
                                    st.error(msg)
                else:
                    st.info("No doctors found for this specialty.")

        # ── Weekly Calendar tab ───────────────────────────────────────
        with tab_cal:
            if "pat_cal_offset" not in st.session_state:
                st.session_state.pat_cal_offset = 0
            today      = dt.today().date()
            week_start = today - timedelta(days=today.weekday()) + timedelta(weeks=st.session_state.pat_cal_offset)
            week_end   = week_start + timedelta(days=5)

            nav_l, nav_mid, nav_r = st.columns([1, 3, 1])
            with nav_l:
                if st.button("◀ Prev", key="pat_prev", type="primary"):
                    st.session_state.pat_cal_offset -= 1; st.rerun()
            with nav_mid:
                st.markdown(f"""
                <div style="text-align:center;font-weight:700;color:#0ea5e9;padding:0.6rem 0;
                            font-size:1.05rem; font-family: 'Space Grotesk', sans-serif;">
                    {week_start.strftime('%d %b')} – {week_end.strftime('%d %b %Y')}
                </div>""", unsafe_allow_html=True)
            with nav_r:
                if st.button("Next ▶", key="pat_next", type="primary"):
                    st.session_state.pat_cal_offset += 1; st.rerun()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            _weekly_calendar(appts, week_start)

        # ── Upcoming tab ──────────────────────────────────────────────
        with tab_list:
            if upcoming:
                for a in upcoming:
                    status = a["status"] or "pending"
                    badge  = status_badge(status)
                    with st.expander(
                        f"Dr. {a['doctor_name']} · {a['scheduled_date']} @ {str(a['start_time'])[:5]}  [{status.upper()}]"
                    ):
                        col_d, col_a = st.columns([3, 1])
                        with col_d:
                            st.markdown(f"**Doctor ID:** #{a['doctor_id']}")
                            st.markdown(f"**Reason:** {a['reason'] or 'N/A'}")
                            st.markdown(f"**Status:** {badge}", unsafe_allow_html=True)
                            if status == "confirmed":
                                st.markdown("""
                                <div style="font-size:0.8rem;color:#14b8a6;margin-top:5px;
                                            display:flex;align-items:center;gap:5px;">
                                    ✅ Your doctor has confirmed this appointment.
                                </div>""", unsafe_allow_html=True)
                            elif status == "pending":
                                st.markdown("""
                                <div style="font-size:0.8rem;color:#f59e0b;margin-top:5px;
                                            display:flex;align-items:center;gap:5px;">
                                    🕐 Awaiting doctor confirmation.
                                </div>""", unsafe_allow_html=True)
                            elif status == "completed":
                                st.markdown("""
                                <div style="font-size:0.8rem;color:#10b981;margin-top:5px;
                                            display:flex;align-items:center;gap:5px;">
                                    ✅ This consultation has been completed.
                                </div>""", unsafe_allow_html=True)
                        with col_a:
                            if status in ["pending", "confirmed", "booked"]:
                                if st.button("❌ Cancel", key=f"pat_cancel_{a['id']}", use_container_width=True):
                                    db.update_appointment_status(a["id"], "cancelled")
                                    st.success("Appointment cancelled. Doctor has been notified.")
                                    st.rerun()
            else:
                st.info("No upcoming appointments. Book one from the 'Book' tab!")
                if st.button("📅 Book an Appointment →", type="primary"):
                    st.session_state.patient_page = "appointments"
                    st.rerun()

        # ── History tab ──────────────────────────────────────────────
        with tab_hist:
            all_past = sorted(
                [a for a in appts if str(a["scheduled_date"]) < str(dt.today().date())
                 or a["status"] in ["completed", "cancelled"]],
                key=lambda a: str(a["scheduled_date"]), reverse=True
            )
            if all_past:
                for a in all_past:
                    status = a["status"] or "pending"
                    badge  = status_badge(status)
                    with st.expander(
                        f"Dr. {a['doctor_name']} · {a['scheduled_date']} [{status.upper()}]"
                    ):
                        st.markdown(f"**Appointment ID:** #{a['id']}")
                        st.markdown(f"**Doctor ID:** #{a['doctor_id']}")
                        st.markdown(f"**Reason:** {a['reason'] or 'N/A'}")
                        st.markdown(f"**Status:** {badge}", unsafe_allow_html=True)
                        if status == "completed":
                            # Show associated health record if any
                            recs = db.fetch_health_records(patient_id=user["id"])
                            st.markdown("**Health Record from this consultation:**")
                            shown = False
                            for r in recs:
                                if str(r["recorded_at"])[:10] == str(a["scheduled_date"]):
                                    shown = True
                                    col_a, col_b = st.columns(2)
                                    col_a.markdown(f"❤️ HR: {r['heart_rate'] or '—'} bpm")
                                    col_a.markdown(f"🩸 BP: {r['blood_pressure'] or '—'}")
                                    col_b.markdown(f"💨 SpO₂: {r['pulse_oximetry'] or '—'}%")
                                    col_b.markdown(f"🫀 EF: {r['ejection_fraction'] or '—'}%")
                                    if r["diagnosis"]:
                                        st.markdown(f"**Diagnosis:** {r['diagnosis']}")
                                    if r["notes"]:
                                        st.markdown(f"📝 {r['notes']}")
                            if not shown:
                                st.caption("No health record linked for this date.")
            else:
                st.info("No past appointments yet.")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: MY MEDICINES
    # ════════════════════════════════════════════════════════════════════
    elif page == "medicines":
        page_header("💊 My Medicines", "View your prescribed medicines")

        # Get prescriptions for this patient
        prescriptions = db.fetch_prescriptions(patient_id=user["id"])

        if not prescriptions:
            st.info("No prescriptions yet. Your doctor will prescribe medicines during consultations.")
        else:
            # PDF Download Section
            st.markdown("### 📥 Download Prescription Report")
            col_pdf1, col_pdf2 = st.columns([3, 1])
            with col_pdf1:
                st.info("💡 Generate a PDF prescription report with all your prescribed medicines, doctor details, and more.")
                unique_doctors = list(set(p.get('doctor_name', 'N/A') for p in prescriptions))
                st.markdown("**Report will include:**")
                st.markdown(f"- Patient: **{user.get('name', 'N/A')}**")
                st.markdown(f"- Prescribing Doctors: {', '.join(['Dr. ' + str(d) for d in unique_doctors])}")
                st.markdown(f"- Total Medicines: **{len(prescriptions)}**")
            with col_pdf2:
                st.markdown("<br>", unsafe_allow_html=True)
                if not check_reportlab():
                    st.warning("📄 PDF generation requires reportlab. Please install: pip install reportlab")
                elif st.button("📄 Generate PDF", type="primary", use_container_width=True):
                    try:
                        pdf_path = f"prescription_{user['id']}_{dt.now().strftime('%Y%m%d_%H%M%S')}.pdf"

                        # Get patient info
                        patient_info = {
                            'name': user.get('name', 'N/A'),
                            'age': user.get('age', 'N/A'),
                            'gender': user.get('gender', 'N/A'),
                            'phone': user.get('phone', 'N/A'),
                            'email': user.get('email', 'N/A')
                        }

                        # Get doctor info from first prescription
                        doctor_info = {}
                        if prescriptions:
                            first_pres = prescriptions[0]
                            doctor_info = {
                                'name': first_pres.get('doctor_name', 'N/A'),
                                'specialty': first_pres.get('doctor_specialty', 'General Medicine')
                            }

                        output_path = generate_prescription_pdf(
                            prescriptions,
                            user.get('name', 'Patient'),
                            pdf_path,
                            patient_info=patient_info,
                            doctor_info=doctor_info
                        )
                        with open(output_path, "rb") as pdf_file:
                            pdf_bytes = pdf_file.read()
                        st.download_button(
                            label="📥 Download PDF",
                            data=pdf_bytes,
                            file_name=f"prescription_{user['name']}_{dt.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                        os.remove(output_path)
                    except Exception as e:
                        st.error(f"Error: {e}")

            st.markdown("---")
            st.markdown("### Your Prescribed Medicines")

            # Filter by status
            col_active, col_completed = st.columns(2)
            status_filter = col_active.selectbox("Filter by Status", ["All", "active", "completed", "cancelled"])

            filtered = prescriptions if status_filter == "All" else [p for p in prescriptions if p["status"] == status_filter]

            if filtered:
                for pres in filtered:
                    status_color = {"active": "#14b8a6", "completed": "#10b981", "cancelled": "#ef4444"}.get(pres["status"], "#9ca3af")

                    # Get medicine image from medicines database
                    med_name = pres.get('medicine_name', '')
                    all_meds = db.fetch_all_medicines()
                    med_details = next((m for m in all_meds if m.get('name', '').lower() == med_name.lower()), None)
                    img_url = med_details.get('image_url', '') if med_details else ''
                    has_img = img_url and os.path.exists(img_url)

                    # Display with image on left
                    col_img, col_info = st.columns([1, 5])
                    with col_img:
                        if has_img:
                            st.image(img_url, width=80)
                        else:
                            st.markdown('<div style="width:80px;height:80px;background:linear-gradient(135deg,#14b8a6,#0d9488);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:2rem;">💊</div>', unsafe_allow_html=True)

                    with col_info:
                        st.markdown(f'<div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 16px; border-left: 5px solid {status_color};"><div style="display: flex; justify-content: space-between; align-items: start; border-bottom: 1px solid #f1f5f9; padding-bottom: 12px;"><div><h4 style="margin:0; color:#0f172a; font-size:1.1rem; display:flex; align-items:center; gap:8px;">💊 {pres["medicine_name"]}</h4><span style="color:#475569; margin-left: 8px; font-weight:500;">{pres["medicine_dosage"]}</span></div><span style="background: {status_color}; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.78rem; font-weight: 700;">{pres["status"].upper()}</span></div><div style="margin-top: 10px; font-size: 0.9rem; color: #0f172a; line-height: 1.7;"><div><b style="color:#0369a1;">👨‍⚕️ Prescribed by:</b> Dr. {pres["doctor_name"]}</div><div><b style="color:#0f172a;">💊 Dosage:</b> {pres["dosageInstructions"]}</div><div><b style="color:#0f172a;">⏰ Frequency:</b> {pres["frequency"]}</div><div><b style="color:#0f172a;">📅 Duration:</b> {pres["duration"]}</div><div><b style="color:#0f172a;">📦 Quantity:</b> {pres["quantity"]} units</div>' + (f'<div><b style="color:#0f172a;">📝 Notes:</b> {pres["notes"]}</div>' if pres.get('notes') else '') + f'</div><div style="margin-top: 8px; font-size: 0.8rem; color: #64748b;">Prescribed on: {str(pres["prescribed_at"])[:16]}</div></div>', unsafe_allow_html=True)
            else:
                st.info(f"No {status_filter} prescriptions found.")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: DOCTORS — with quick-book button
    # ════════════════════════════════════════════════════════════════════
    elif page == "doctors":
        page_header("Doctors Directory", "Meet our medical experts")
        doctors  = db.fetch_all_doctors()
        sp_icons = {"Cardiology": "🫀", "Neurology": "🧠", "Pediatrics": "👶",
                    "Orthopedics": "🦴", "General Medicine": "⚕️", "Dermatology": "🩹",
                    "Psychiatry": "🧘", "Ophthalmology": "👁️", "Gynecology": "🌸",
                    "Oncology": "🎗️", "Gastroenterology": "🫃", "Pulmonology": "🫁",
                    "Nephrology": "🫘", "Urology": "🔬", "Endocrinology": "⚗️"}
        if doctors:
            col_search, col_sp = st.columns(2)
            search = col_search.text_input("🔍 Search Doctors…", placeholder="Name or specialty",
                                            label_visibility="collapsed")
            sp_filter = col_sp.selectbox("Filter by Specialty", ["All"] +
                                          sorted({d["specialty"] or "General" for d in doctors}),
                                          label_visibility="collapsed")
            filtered = [d for d in doctors if
                        (not search or search.lower() in d["full_name"].lower() or
                         search.lower() in (d["specialty"] or "").lower()) and
                        (sp_filter == "All" or d["specialty"] == sp_filter)]

            cols = st.columns(3)
            for i, d in enumerate(filtered):
                sp   = d["specialty"] or "General"
                icon = sp_icons.get(sp, "🩺")
                with cols[i % 3]:
                    st.markdown(f"""
                    <div class="doc-card">
                        <div class="doc-card-icon">{icon}</div>
                        <div class="doc-card-specialty">{sp}</div>
                        <div class="doc-card-name">Dr. {d['full_name']}</div>
                        <div class="doc-card-desc">{d['bio'] or 'Healthcare specialist.'}</div>
                        <div style="margin-top:0.7rem;display:flex;gap:1rem;font-size:0.78rem;color:#6b7280;">
                            <span style="display:flex;align-items:center;gap:4px;">🏆 {d['experience_years']} yrs exp</span>
                            <span style="display:flex;align-items:center;gap:4px;">💰 ₹{d['consultation_fee']}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"📅 Book Dr. {d['full_name'].split()[0]}",
                                 key=f"quick_book_{d['id']}", use_container_width=True, type="primary"):
                        # Pre-select this doctor in booking tab
                        st.session_state["bk_doc_tab"] = d["id"]
                        st.session_state["bk_sp_tab"]  = d["specialty"] or "All"
                        st.session_state.patient_page  = "appointments"
                        st.rerun()
                    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
        else:
            st.info("No doctors registered.")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: SHOP MEDICINES — Browse and view all medicines
    # ════════════════════════════════════════════════════════════════════
    elif page == "shop":
        page_header("💊 Medicine Shop", "Browse our pharmacy inventory")

        # Get all medicines
        all_medicines = db.fetch_all_medicines()

        if not all_medicines:
            st.info("No medicines available in the pharmacy.")
        else:
            # Search and filter
            col_search, col_cat = st.columns([2, 1])
            with col_search:
                search = st.text_input("🔍 Search medicines", placeholder="Search by name...")
            with col_cat:
                categories = ["All"] + list(set(m.get("category", "General") for m in all_medicines))
                cat_filter = st.selectbox("Category", categories)

            # Apply filters
            filtered = all_medicines
            if search:
                filtered = [m for m in filtered if search.lower() in m.get("name", "").lower()]
            if cat_filter != "All":
                filtered = [m for m in filtered if m.get("category") == cat_filter]

            st.markdown(f"**Showing {len(filtered)} medicines**")

            # Proper grid layout with consistent cards - 4 columns
            cols_per_row = 4
            for row_start in range(0, len(filtered), cols_per_row):
                cols = st.columns(cols_per_row)
                row_meds = filtered[row_start:row_start + cols_per_row]

                for col_idx, med in enumerate(row_meds):
                    with cols[col_idx]:
                        # Card container
                        with st.container():
                            img_url = med.get("image_url", "")
                            if img_url and os.path.exists(img_url):
                                st.image(img_url, width=120, use_container_width=False)
                            else:
                                st.markdown('''
                                <div style="width:100%;height:120px;background:linear-gradient(135deg,#3b82f6,#1d4ed8);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:3rem;margin-bottom:10px;">
                                    💊
                                </div>
                                ''', unsafe_allow_html=True)

                            # Medicine name
                            st.markdown(f"**{med.get('name', 'Unknown')}**")

                            # Category
                            st.markdown(f"<span style='color:#6b7280;font-size:0.85rem;'>📦 {med.get('category', 'General')}</span>", unsafe_allow_html=True)

                            # Price
                            st.markdown(f"<span style='color:#0ea5e9;font-size:1.1rem;font-weight:bold;'>💰 ₹{med.get('unit_price', 0)}</span>", unsafe_allow_html=True)

                            # Stock status
                            stock = med.get('stock_quantity', 0)
                            if stock > 10:
                                st.success("✅ In Stock")
                            elif stock > 0:
                                st.warning("⚠️ Low Stock")
                            else:
                                st.error("❌ Out of Stock")

                            # Composition
                            if med.get('composition'):
                                st.caption(f"Composition: {med['composition'][:40]}...")

                            # Dosage
                            if med.get('dosage'):
                                st.caption(f"Dosage: {med['dosage']}")

                            # Buy button
                            if stock > 0:
                                if st.button(f"🛒 Buy Now", key=f"buy_{med['id']}", use_container_width=True):
                                    st.session_state[f"show_order_form_{med['id']}"] = True

                            # Order form
                            if st.session_state.get(f"show_order_form_{med['id']}", False):
                                with st.expander(f"Order {med.get('name')}", expanded=True):
                                    qty = st.number_input("Quantity", min_value=1, max_value=stock, value=1, key=f"qty_{med['id']}")
                                    total = qty * med.get('unit_price', 0)
                                    st.markdown(f"**Total: ₹{total}**")

                                    address = st.text_area("Delivery Address", key=f"addr_{med['id']}")
                                    phone = st.text_input("Contact Phone", key=f"phone_{med['id']}")
                                    notes = st.text_input("Notes (optional)", key=f"notes_{med['id']}")

                                    col_confirm, col_cancel = st.columns(2)
                                    with col_confirm:
                                        if st.button("✅ Confirm Order", key=f"confirm_{med['id']}", use_container_width=True):
                                            if not address or not phone:
                                                st.error("Please provide delivery address and phone!")
                                            else:
                                                success, msg = db.create_medicine_order(
                                                    user['id'], med['id'], qty, address, phone, notes
                                                )
                                                if success:
                                                    st.success(msg)
                                                    st.session_state[f"show_order_form_{med['id']}"] = False
                                                else:
                                                    st.error(msg)
                                    with col_cancel:
                                        if st.button("❌ Cancel", key=f"cancel_{med['id']}", use_container_width=True):
                                            st.session_state[f"show_order_form_{med['id']}"] = False
                                            st.rerun()

                            st.markdown("---")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: MY ORDERS — View order history
    # ════════════════════════════════════════════════════════════════════
    elif page == "orders":
        page_header("📦 My Orders", "View your medicine order history")

        orders = db.fetch_patient_orders(user['id'])

        if not orders:
            st.info("You haven't placed any medicine orders yet.")
            st.markdown("Visit the [Shop Medicines](#) to browse and order medicines.")
        else:
            st.markdown(f"**You have {len(orders)} order(s)**")

            for order in orders:
                # Status color
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
                                border-radius: 14px; padding: 1.2rem; margin: 0.8rem 0; box-shadow: 0 2px 10px rgba(0,0,0,0.04);">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <div>
                                <b style="color:#0369a1; font-size: 1.15rem;">{order['medicine_name']}</b>
                                <span style="background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; padding: 2px 10px; border-radius: 20px; font-size: 0.78rem; font-weight: 600; margin-left: 10px;">{order['category']}</span>
                            </div>
                            <div style="text-align: right;">
                                <div style="color: {status_color}; font-weight: 700; text-transform: uppercase; font-size: 0.85rem; letter-spacing: 0.05em;">{order['status']}</div>
                                <div style="color:#0f172a; font-weight: 700; font-size: 1.05rem; margin-top: 2px;">₹{order['total_price']}</div>
                            </div>
                        </div>
                        <div style="font-size: 0.88rem; color:#475569; margin-top: 10px; line-height: 1.6;">
                            <span style="font-weight: 600; color:#0f172a;">Qty: {order['quantity']} x ₹{order['unit_price']}</span> · <span style="color:#64748b;">Ordered: {order['order_date']}</span>
                        </div>
                        <div style="font-size: 0.85rem; color:#334155; margin-top: 6px; display: flex; gap: 16px; align-items: center; flex-wrap: wrap;">
                            <span>📍 <span style="color:#0f172a;">{order['delivery_address']}</span></span>
                            <span>📞 <span style="color:#0f172a;">{order['contact_phone']}</span></span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Cancel button for pending orders
                if order['status'] == 'pending':
                    if st.button(f"❌ Cancel Order #{order['id']}", key=f"cancel_order_{order['id']}"):
                        success, msg = db.cancel_order(order['id'], user['id'])
                        if success:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)

                st.markdown("---")

    # ════════════════════════════════════════════════════════════════════
    # PAGE: SMARTCARE AI — powered by Groq LLaMA & Local DB
    # ════════════════════════════════════════════════════════════════════
    elif page == "chat":
        ai_care.render_ai_care_tab(user)