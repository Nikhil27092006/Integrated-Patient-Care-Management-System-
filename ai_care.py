
"""
AI Care Module — LangChain + Groq AI Assistant integrated with local database (db.py).

Provides intelligent database query resolution, appointment booking, patient health insights,

doctor schedule oversight, admin analytics, and general medical advice.

"""


import sys
import os
import streamlit as st
from datetime import datetime as dt, timedelta

# Ensure root workspace is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))


import db

from dotenv import load_dotenv

# Load .env from the project root
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '.env'))
load_dotenv(env_path)

def _format_doc_name(name: str) -> str:

    """Format doctor name cleanly without duplicate 'Dr.' prefix."""

    if not name:

        return "Doctor"

    clean = name.strip()

    if clean.lower().startswith("dr.") or clean.lower().startswith("dr "):

        return clean

    return f"Dr. {clean}"

def _get_groq_llm():

    """Lazy-load the Groq LLM using langchain_groq."""

    try:

        from langchain_groq import ChatGroq

        api_key = os.getenv("GROQ_API_KEY", "")

        if not api_key:

            return None, "GROQ_API_KEY not found in environment or .env"

        # Using deepseek/llama model supported by Groq

        llm = ChatGroq(

            model="llama-3.3-70b-versatile",

            temperature=0.3,

            api_key=api_key,

        )

        return llm, None

    except ImportError:

        return None, "langchain-groq package not installed."

    except Exception as e:

        # Fallback try another model if specified model fails or general error

        try:

            from langchain_groq import ChatGroq

            api_key = os.getenv("GROQ_API_KEY", "")

            if api_key:

                llm = ChatGroq(

                    model="llama3-8b-8192",

                    temperature=0.3,

                    api_key=api_key,

                )

                return llm, None

        except Exception:

            pass

        return None, str(e)

def _build_db_context(user_data: dict) -> str:

    """Build a concise live ground-truth text summary of the database state."""

    role = user_data.get("role", "patient").lower()

    user_id = user_data.get("id")

    context_lines = []

    try:

        # General system metrics

        user_counts = db.fetch_user_counts()

        context_lines.append(f"System Users Summary: {user_counts.get('patients', 0)} Patients, {user_counts.get('doctors', 0)} Doctors, {user_counts.get('admins', 0)} Admins.")

        # Doctors

        doctors = db.fetch_all_doctors()

        if doctors:

            doc_summaries = [f"{_format_doc_name(d['full_name'])} ({d['specialty'] or 'General'}, Fee: ₹{d['consultation_fee']}, Exp: {d['experience_years']} yrs)" for d in doctors[:10]]

            context_lines.append("Available Doctors: " + "; ".join(doc_summaries))

        # Role specific data

        if role == "patient" and user_id:

            appts = db.fetch_appointments(patient_id=user_id)

            if appts:

                upcoming = [a for a in appts if str(a.get("scheduled_date")) >= str(dt.today().date())]

                context_lines.append(f"Current Patient ({user_data.get('name')}): Has {len(appts)} total appointment(s) ({len(upcoming)} upcoming).")

                for a in upcoming[:3]:

                    context_lines.append(f"  - Upcoming: {a.get('scheduled_date')} at {str(a.get('start_time'))[:5]} with Dr. {a.get('doctor_name')} (Status: {a.get('status')})")

            records = db.fetch_health_records(patient_id=user_id)

            if records:

                r = records[0]

                context_lines.append(f"Latest Vitals: HR={r.get('heart_rate')}bpm, BP={r.get('blood_pressure')}, SpO2={r.get('pulse_oximetry')}%, EF={r.get('ejection_fraction')}%, Diagnosis={r.get('diagnosis', 'None')}")

        elif role == "doctor" and user_id:

            doc_info = db.fetch_doctor_by_user_id(user_id)

            doc_db_id = doc_info["id"] if doc_info else user_id

            appts = db.fetch_appointments(doctor_id=doc_db_id)

            today_str = str(dt.today().date())

            today_appts = [a for a in appts if str(a.get("scheduled_date")) == today_str]

            context_lines.append(f"Current Doctor ({user_data.get('name')}): Has {len(appts)} total appointment(s) ({len(today_appts)} today).")

        elif role == "admin":

            all_users = db.fetch_all_users()

            active_users = sum(1 for u in all_users if u.get("is_active"))

            context_lines.append(f"Admin View: Total active users = {active_users}/{len(all_users)}.")

            meds = db.fetch_all_medicines()

            if meds:

                low_stock = [m for m in meds if m.get("stock_quantity", 0) < 20]

                context_lines.append(f"Pharmacy Overview: {len(meds)} medicines cataloged, {len(low_stock)} low-stock alerts.")

    except Exception as e:

        context_lines.append(f"DB Context Fetch Note: {e}")

    return "\n".join(context_lines)


def analyze_medicine_image(image_bytes: bytes, image_type: str = "image/jpeg") -> str:
    """
    Analyze a medicine/drug image using Groq's vision model.
    Returns a structured analysis of the medicine shown in the image.
    """
    import base64

    try:
        from groq import Groq

        api_key = os.getenv("GROQ_API_KEY", "")
        if not api_key:
            return "⚠️ GROQ_API_KEY not configured. Cannot perform image analysis."

        client = Groq(api_key=api_key)

        # Encode image to base64
        image_b64 = base64.b64encode(image_bytes).decode("utf-8")
        image_data_url = f"data:{image_type};base64,{image_b64}"

        prompt = (
            "You are a highly knowledgeable pharmaceutical expert and medical AI assistant. "
            "A patient has uploaded a photo of a medicine/drug. "
            "Carefully analyze the image and provide a comprehensive, structured report.\n\n"
            "Please include ALL of the following sections in your response:\n\n"
            "💊 **Medicine Name & Brand**: Identify the medicine name, brand, and active ingredient(s).\n"
            "📋 **Description**: Brief description of what this medicine is.\n"
            "🏥 **Medical Uses**: What conditions / diseases it treats. List all indications.\n"
            "✅ **Benefits / Pros**: Key benefits of this medicine.\n"
            "⚠️ **Cons / Limitations**: Disadvantages, dependency risks, or limitations.\n"
            "💉 **Dosage & Administration**: Typical dosage, frequency, and how to take it.\n"
            "🚫 **Side Effects**: Common and serious side effects to watch for.\n"
            "🔴 **Contraindications**: Who should NOT take this medicine (allergies, conditions, age groups).\n"
            "🔄 **Drug Interactions**: Important drug-drug or drug-food interactions.\n"
            "🛡️ **Storage Instructions**: How to store this medicine properly.\n"
            "⚕️ **Medical Disclaimer**: Remind the patient to always consult a licensed doctor before use.\n\n"
            "If you cannot clearly identify the medicine from the image, say so and ask for a clearer photo or the medicine name."
        )

        # Query active models dynamically or use validated working Groq vision models
        vision_models = ["qwen/qwen3.6-27b"]

        try:
            available_models = [m.id for m in client.models.list().data]
            for m in available_models:
                if m not in vision_models and any(k in m.lower() for k in ["qwen", "vision", "multimodal"]):
                    vision_models.append(m)
        except Exception:
            pass

        err_details = []
        analysis_text = ""

        for v_model in vision_models:
            try:
                response = client.chat.completions.create(
                    model=v_model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image_url",
                                    "image_url": {"url": image_data_url},
                                },
                                {
                                    "type": "text",
                                    "text": prompt,
                                },
                            ],
                        }
                    ],
                    max_tokens=2048,
                )
                analysis_text = response.choices[0].message.content or ""
                if analysis_text.strip():
                    break
            except Exception as ex:
                err_details.append(f"[{v_model}]: {str(ex)}")
                continue

        if not analysis_text.strip():
            combined_err = " | ".join(err_details) if err_details else "Unknown model error"
            return f"⚠️ Medicine image analysis failed: {combined_err}\n\nPlease ensure the image is clear and shows the medicine label/packaging."

        # Clean up any <think> tags if returned by reasoning vision models
        import re
        clean_res = re.sub(r"<think>.*?</think>", "", analysis_text, flags=re.DOTALL).strip()
        return clean_res if clean_res else analysis_text.strip()

    except ImportError:
        return "⚠️ `groq` package not installed. Run: `pip install groq`"
    except Exception as e:
        return f"⚠️ Medicine image analysis failed: {str(e)}\n\nPlease ensure the image is clear and shows the medicine label/packaging."



def process_ai_care_message(messages: list, user_data: dict) -> str:

    """

    Main processing entry point for AI Care.

    Combines direct database intent handling (e.g. appointment booking, query lookup)

    with Groq ChatGroq LLM invocation.

    """

    if not messages:

        return "Hello! How can I assist you today? Is there anything specific you need help with?"

    user_id = user_data.get("id")

    role = user_data.get("role", "patient").lower()

    # Get latest user message

    latest_msg = ""

    for m in reversed(messages):

        if m.get("role") == "user":

            latest_msg = m.get("content", "").strip()

            break

    msg_lower = latest_msg.lower()

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT: BOOK AN APPOINTMENT (Show Form)

    # ──────────────────────────────────────────────────────────────────────────

    booking_form_key = f"booking_form_{role}_{user_id}"

    booking_state_key = f"booking_state_{role}_{user_id}"

    booking_closed_key = f"booking_closed_{role}_{user_id}"

    booking_keywords = ["book appointment", "create appointment", "schedule appointment",
                        "book an appointment", "need appointment", "want to book", "book doctor", "book dr",
                        "booking appointment", "book a doctor", "appointment with", "booking appoitnment"]
    if any(kw in msg_lower for kw in booking_keywords):

        if role == "doctor":

            return "👨‍⚕️ As a Doctor, appointment booking is managed by patients or admins. You can review your schedule in the 'Appointments' tab.\n\n💬 Is there anything else you need help with?"

        doctors = db.fetch_all_doctors()

        if not doctors:

            return "⚠️ No doctors available in the system right now. Please load/create doctor profiles first.\n\n💬 Let me know if you need anything else!"

        # Set state to show the booking form

        st.session_state[booking_state_key] = "show_form"

        # Reset the closed flag so form can be shown

        st.session_state[booking_closed_key] = False

        if booking_form_key in st.session_state:

            del st.session_state[booking_form_key]

        return (

            "📅 **I'll open the booking form for you!**\n\n"

            "Just fill in the details below:\n"

            "1. Select your preferred doctor\n"

            "2. Pick a date\n"

            "3. Choose an available time slot\n"

            "4. Confirm your booking\n\n"

            "The form is ready below! 👇"

        )

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT 2: LIST / SEARCH DOCTORS

    # ──────────────────────────────────────────────────────────────────────────

    if any(kw in msg_lower for kw in ["list doctors", "show doctors", "available doctors", "all doctors", "doctors list", "find doctor"]):

        doctors = db.fetch_all_doctors()

        if not doctors:

            return "No doctors available in the system yet.\n\n💬 Is there anything else you need help with?"

        res = "🩺 **Available Doctors List:**\n\n"

        for d in doctors:

            res += f"• **{_format_doc_name(d['full_name'])}** ({d['specialty'] or 'General Medicine'})\n"

            res += f"  💰 Fee: ₹{d['consultation_fee']} | 🏆 Experience: {d['experience_years']} years\n\n"

        res += "_To book an appointment, say: 'Book appointment with Dr. <name>'_\n\n"

        res += "💬 **Is there anything else you need assistance with?**"

        return res

    if any(kw in msg_lower for kw in ["highest fee", "top doctor", "most expensive", "fee details"]):

        doctors = db.fetch_all_doctors()

        if doctors:

            sorted_docs = sorted(doctors, key=lambda x: x.get("consultation_fee", 0), reverse=True)[:3]

            res = "🏆 **Top Doctors by Consultation Fee:**\n\n"

            for i, d in enumerate(sorted_docs, 1):

                res += f"**{i}. {_format_doc_name(d['full_name'])}** — ₹{d['consultation_fee']}/visit\n"

                res += f"   Specialty: {d['specialty'] or 'General'} | Experience: {d['experience_years']} yrs\n\n"

            res += "💬 **Is there anything else I can help you with?**"

            return res

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT 3: MY APPOINTMENTS & SCHEDULE

    # ──────────────────────────────────────────────────────────────────────────

    if any(kw in msg_lower for kw in ["my appointments", "upcoming appointment", "show my appointments", "list appointments", "my schedule"]):

        if role == "patient" and user_id:

            appts = db.fetch_appointments(patient_id=user_id)

            if not appts:

                return "📅 You don't have any appointments scheduled yet.\n\n💬 Would you like me to help you book one?"

            upcoming = [a for a in appts if str(a.get("scheduled_date")) >= str(dt.today().date())]

            if not upcoming:

                return "📅 You have no upcoming appointments. (Past appointments can be viewed in the Appointments tab).\n\n💬 Is there anything else you need assistance with?"

            res = "📅 **Your Upcoming Appointments:**\n\n"

            for a in upcoming:

                icon = {"confirmed": "✅", "pending": "⏳", "completed": "✔️", "cancelled": "❌"}.get(a.get("status", ""), "📅")

                res += f"{icon} **{a['scheduled_date']}** at {str(a['start_time'])[:5]}\n"

                res += f"   Dr. {a.get('doctor_name', 'Doctor')} — Reason: {a.get('reason', 'Consultation')} (Status: **{a.get('status','').upper()}**)\n\n"

            res += "💬 **Is there anything else you need help with?**"

            return res

        elif role == "doctor" and user_id:

            doc_info = db.fetch_doctor_by_user_id(user_id)

            doc_db_id = doc_info["id"] if doc_info else user_id

            appts = db.fetch_appointments(doctor_id=doc_db_id)

            if not appts:

                return "📅 No appointments booked with you yet.\n\n💬 Is there anything else you need assistance with?"

            today_str = str(dt.today().date())

            today_appts = [a for a in appts if str(a.get("scheduled_date")) == today_str]

            res = f"👨‍⚕️ **Your Schedule Overview ({len(appts)} total, {len(today_appts)} today):**\n\n"

            for a in appts[:5]:

                icon = {"confirmed": "✅", "pending": "⏳", "completed": "✔️"}.get(a.get("status", ""), "📅")

                res += f"{icon} **{a['scheduled_date']}** ({str(a['start_time'])[:5]}) — Patient: **{a.get('patient_name')}** ({a.get('status')})\n"

            res += "\n💬 **Is there anything else I can assist you with today?**"

            return res

        elif role == "admin":

            all_appts = db.fetch_appointments()

            if not all_appts:

                return "📅 No appointments found in the system.\n\n💬 Is there anything else you need help with?"

            pending_count = sum(1 for a in all_appts if a.get("status") == "pending")

            confirmed_count = sum(1 for a in all_appts if a.get("status") == "confirmed")

            return (

                f"📊 **System Appointments Oversight:**\n\n"

                f"• **Total Appointments:** {len(all_appts)}\n"

                f"• **Pending Confirmation:** {pending_count}\n"

                f"• **Confirmed:** {confirmed_count}\n\n"

                f"💬 **Is there anything else you need assistance with?**"

            )

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT 4: HEALTH VITALS & RECORDS

    # ──────────────────────────────────────────────────────────────────────────

    if any(kw in msg_lower for kw in ["health condition", "my health", "vitals", "health status", "medical records", "my vitals"]):

        if role == "patient" and user_id:

            records = db.fetch_health_records(patient_id=user_id)

            if not records:

                return "📋 No health records found for your profile yet. Please consult a doctor to record your vitals.\n\n💬 Is there anything else you need help with?"

            r = records[0]

            return (

                f"📊 **Latest Health Vitals Assessment:**\n\n"

                f"❤️ **Heart Rate:** {r.get('heart_rate', 'N/A')} bpm\n"

                f"💉 **Blood Pressure:** {r.get('blood_pressure', 'N/A')} mmHg\n"

                f"🫁 **Pulse Oximetry (SpO₂):** {r.get('pulse_oximetry', 'N/A')}%\n"

                f"🫀 **Ejection Fraction:** {r.get('ejection_fraction', 'N/A')}%\n"

                f"💪 **Cardiac Output:** {r.get('cardiac_output', 'N/A')} L/min\n\n"

                f"📋 **Diagnosis:** {r.get('diagnosis', 'None recorded')}\n"

                f"📝 **Doctor Notes:** {r.get('notes', 'None recorded')}\n\n"

                f"💬 **Is there anything else you need assistance with?**"

            )

        elif role in ["doctor", "admin"]:

            patients = db.fetch_all_patients()

            return f"👥 **Patients Database:** {len(patients)} patients registered. You can review detailed records in the 'My Patients' / 'Patients' section.\n\n💬 Is there anything else you need help with?"

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT 5: ADMIN / SYSTEM STATS

    # ──────────────────────────────────────────────────────────────────────────

    if any(kw in msg_lower for kw in ["admin stats", "system stats", "user counts", "how many patients", "how many doctors", "system health", "overall summary"]):

        user_counts = db.fetch_user_counts()

        all_appts = db.fetch_appointments()

        meds = db.fetch_all_medicines()

        specs = db.fetch_all_specialties()

        return (

            f"🛡️ **System Overview & Health Metrics:**\n\n"

            f"👥 **User Accounts:** {user_counts.get('patients',0)} Patients | {user_counts.get('doctors',0)} Doctors | {user_counts.get('admins',0)} Admins\n"

            f"📅 **Total Appointments:** {len(all_appts)}\n"

            f"💊 **Pharmacy Inventory:** {len(meds)} Medicines cataloged\n"

            f"🩺 **Medical Specialties:** {len(specs)} Specialties configured\n\n"

            f"💬 **Is there anything else you need assistance with?**"

        )

    # ──────────────────────────────────────────────────────────────────────────

    # INTENT 6: PHARMACY & MEDICINES

    # ──────────────────────────────────────────────────────────────────────────

    if any(kw in msg_lower for kw in ["medicine", "medicines", "pharmacy", "stock", "prescription"]):

        meds = db.fetch_all_medicines()

        if not meds:

            return "💊 No medicines in the pharmacy database currently.\n\n💬 Is there anything else you need help with?"

        res = f"💊 **Pharmacy Catalog Summary ({len(meds)} items):**\n\n"

        for m in meds[:5]:

            res += f"• **{m['name']}** ({m.get('category','General')}) — ₹{m['unit_price']} | Stock: {m['stock_quantity']} units\n"

        if len(meds) > 5:

            res += f"\n_...and {len(meds) - 5} more medicines available in the Pharmacy tab._\n\n"

        res += "💬 **Is there anything else you need assistance with?**"

        return res

    # ──────────────────────────────────────────────────────────────────────────

    # FALLBACK: GROQ CHATGROQ LLM WITH LIVE DB CONTEXT

    # ──────────────────────────────────────────────────────────────────────────

    llm, err = _get_groq_llm()

    if err:

        return f"⚠️ Groq AI API Notice: {err}\n\n(I can still assist with database commands like 'list doctors', 'my appointments', 'book appointment', 'my health', or 'admin stats')."

    try:

        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

        db_context = _build_db_context(user_data)

        system_prompt = (

            "You are SmartCare AI, an advanced medical AI assistant integrated into IPCMS "

            "(Integrated Patient Care Management System).\n"

            f"Current User Info: Name={user_data.get('name')}, Role={role.upper()}.\n\n"

            "LIVE DATABASE GROUND TRUTH CONTEXT:\n"

            f"{db_context}\n\n"

            "INSTRUCTIONS:\n"

            "1. Assist users with general medical knowledge, platform guidance, and health explanations.\n"

            "2. Use the live database context above to provide accurate answers when asked about doctors, appointments, patients, health vitals, or system statistics.\n"

            "3. ALWAYS state clearly that you are an AI assistant, NOT a doctor, and cannot diagnose or prescribe.\n"

            "4. For medical emergencies, direct users immediately to local emergency services (e.g. 108 / 911).\n"

            "5. Keep responses structured, concise, empathetic, and professional.\n"
            "6. ALWAYS end your response warmly asking the user if they need help with anything else (e.g. 'Is there anything else I can assist you with today?').\n"
            "7. IF the user wants to book an appointment with a doctor, you MUST include the EXACT string [OPEN_BOOKING_FORM] anywhere in your response."
        )

        lc_msgs = [SystemMessage(content=system_prompt)]

        for m in messages:

            if m.get("role") == "user":

                lc_msgs.append(HumanMessage(content=m["content"]))

            elif m.get("role") == "assistant":

                lc_msgs.append(AIMessage(content=m["content"]))

        response = llm.invoke(lc_msgs)

        reply_content = response.content

        if "[OPEN_BOOKING_FORM]" in reply_content:
            reply_content = reply_content.replace("[OPEN_BOOKING_FORM]", "").strip()
            
            booking_state_key = f"booking_state_{role}_{user_data.get('id', 0)}"
            booking_closed_key = f"booking_closed_{role}_{user_data.get('id', 0)}"
            booking_form_key = f"booking_form_{role}_{user_data.get('id', 0)}"
            
            st.session_state[booking_state_key] = "show_form"
            st.session_state[booking_closed_key] = False
            if booking_form_key in st.session_state:
                del st.session_state[booking_form_key]
                
            if not reply_content:
                reply_content = "📅 **I'll open the booking form for you!**\n\nThe form is ready below! 👇"

        if "anything else" not in reply_content.lower() and "need help" not in reply_content.lower():

            reply_content += "\n\n💬 *Is there anything else I can assist you with today?*"

        return reply_content

    except Exception as e:

        return f"⚠️ SmartCare AI encountered an error: {e}"

def render_ai_care_tab(user_data: dict):

    """

    Renders the unified AI Care Chatbot interface in Streamlit.

    Can be placed in Patient, Doctor, or Admin dashboard.

    Text-based AI assistant only (no voice).

    """

    role = user_data.get("role", "patient").lower()

    user_name = user_data.get("name", "User")

    user_id = user_data.get("id", 0)

    first_name = user_name.split()[0] if user_name else "User"

    # Medical Header Banner with Brand Logo
    from pages.shared_styles import medical_banner
    medical_banner(role.capitalize())

    # Medical Disclaimer Banner

    st.markdown(
        '<div style="background: linear-gradient(135deg, rgba(245,158,11,0.1), rgba(245,158,11,0.05)); '
        'border: 1px solid rgba(245,158,11,0.25); '
        'border-radius: 12px; '
        'padding: 1rem; '
        'margin-bottom: 1rem; '
        'word-wrap: break-word; '
        'overflow-wrap: break-word; '
        'white-space: normal; '
        'overflow: hidden;">'
        '<strong>⚠️ Medical Disclaimer:</strong> SmartCare AI provides information from the local system '
        'and general medical knowledge. It does not constitute medical advice. '
        'Please consult a licensed healthcare professional for any medical concerns.'
        '</div>',
        unsafe_allow_html=True
    )

    # Session key for role-specific chat history

    history_key = f"ai_care_history_{role}_{user_data.get('id', 0)}"

    # Initialize chat history if not present

    if history_key not in st.session_state:

        st.session_state[history_key] = [

            {"role": "assistant", "content": f"Hello {first_name}! 👋 I am **SmartCare AI**, your medical assistant.\n\nHow can I help you today?"}

        ]

    for msg in st.session_state[history_key]:

        msg_role = msg.get("role", "assistant")

        avatar = "👤" if msg_role == "user" else "🤖"

        with st.chat_message(msg_role, avatar=avatar):

            st.markdown(msg.get("content", ""))

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    # ── Inject custom CSS for professional chat interface ───────────────────────

    st.markdown("""

    <style>

        /* Professional Input Bar Container */

        div[data-testid="stHorizontalBlock"]:has(> div > div > div > div > input) {

            background: linear-gradient(145deg, #1a1f2e, #0d1117);

            border-radius: 14px;

            padding: 8px 12px;

            border: 1px solid #2d3748;

            box-shadow: 0 4px 20px rgba(0,0,0,0.3);

        }

        /* Input field styling - Pure Black Text for High Visibility */

        div[data-testid="stHorizontalBlock"] input,
        div[data-testid="stTextInput"] input,
        div[data-baseweb="input"] input,
        input[type="text"] {

            background: transparent !important;

            color: #000000 !important;

            -webkit-text-fill-color: #000000 !important;

            font-family: 'Segoe UI', system-ui, sans-serif;

            font-size: 0.95rem !important;

            font-weight: 500 !important;

        }

        div[data-testid="stHorizontalBlock"] input::placeholder,
        div[data-testid="stTextInput"] input::placeholder,
        div[data-baseweb="input"] input::placeholder,
        input::placeholder {

            color: #64748b !important;

            -webkit-text-fill-color: #64748b !important;

            font-style: italic;

        }

        /* Send button - Professional blue gradient */

        div[data-testid="stHorizontalBlock"]:has(button[kind="secondary"]) button[kind="primary"],

        button[key*="send_btn"] {

            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;

            color: #ffffff !important;

            border: none !important;

            border-radius: 10px !important;

            font-weight: 600 !important;

            font-family: 'Segoe UI', system-ui, sans-serif;

            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4) !important;

            transition: all 0.3s ease !important;

        }

        button[key*="send_btn"]:hover {

            background: linear-gradient(135deg, #2563eb, #1d4ed8) !important;

            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.5) !important;

            transform: translateY(-1px) !important;

        }

        /* Chat message styling - User bubble */

        .chat-user-bubble {

            background: linear-gradient(135deg, #3b82f6, #2563eb) !important;

            color: #ffffff !important;

            border-radius: 18px 18px 4px 18px !important;

            padding: 0.9rem 1.2rem !important;

            font-family: 'Segoe UI', system-ui, sans-serif;

            font-size: 0.95rem !important;

            line-height: 1.5 !important;

            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;

        }

        /* Chat message styling - AI bubble */

        .chat-ai-bubble {

            background: linear-gradient(145deg, #1e293b, #0f172a) !important;

            border: 1px solid #334155 !important;

            color: #e2e8f0 !important;

            border-radius: 4px 18px 18px 18px !important;

            padding: 1rem 1.3rem !important;

            font-family: 'Segoe UI', system-ui, sans-serif;

            font-size: 0.93rem !important;

            line-height: 1.6 !important;

            box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;

        }

    </style>

    """, unsafe_allow_html=True)

    # ── Input counter (needed for both image uploader and text input keys) ────
    input_counter_key = f"chat_input_counter_{role}_{user_data.get('id', 0)}"

    if input_counter_key not in st.session_state:
        st.session_state[input_counter_key] = 0

    # ── Medicine Image Uploader (Patient only) ───────────────────────────────
    img_uploader_key = f"med_img_upload_{role}_{user_data.get('id', 0)}_{st.session_state[input_counter_key]}"

    if role == "patient":

        st.markdown(
            '<div style="background: linear-gradient(135deg, rgba(139,92,246,0.08), rgba(14,165,233,0.08)); '
            'border: 1.5px dashed rgba(139,92,246,0.4); border-radius: 14px; '
            'padding: 0.75rem 1.2rem; margin-bottom: 0.75rem; '
            'display: flex; align-items: center; gap: 10px;">'
            '<span style="font-size: 1.3rem;">💊</span>'
            '<span style="font-size: 0.85rem; color: #4c1d95; font-weight: 600;">'
            'Upload a medicine photo for AI analysis — get full details, pros, cons & warnings'
            '</span>'
            '</div>',
            unsafe_allow_html=True
        )

        med_image_file = st.file_uploader(
            "📸 Upload Medicine Image",
            type=["jpg", "jpeg", "png", "webp", "bmp"],
            key=img_uploader_key,
            label_visibility="collapsed",
            help="Upload a clear photo of the medicine packaging, strip, or label. AI will analyse it."
        )

        if med_image_file is not None:

            # Show preview
            col_prev, col_btn = st.columns([3, 1])

            with col_prev:
                st.image(med_image_file, caption="📷 Uploaded Medicine Image", use_column_width=True)

            with col_btn:
                st.markdown('<div style="height: 30px;"></div>', unsafe_allow_html=True)
                analyse_clicked = st.button(
                    "🔍 Analyse",
                    key=f"analyse_img_btn_{role}_{user_data.get('id',0)}",
                    type="primary",
                    use_container_width=True
                )

            if analyse_clicked:

                image_bytes = med_image_file.getvalue()
                img_type = med_image_file.type or "image/jpeg"

                # Add user message with image indicator to chat
                st.session_state[history_key].append({
                    "role": "user",
                    "content": f"📷 **[Medicine Image Uploaded]** — `{med_image_file.name}`\n\nPlease analyse this medicine image and provide full details."
                })

                with st.spinner("🔬 Analysing medicine image with AI Vision... Please wait..."):
                    analysis_result = analyze_medicine_image(image_bytes, img_type)

                st.session_state[history_key].append({
                    "role": "assistant",
                    "content": f"## 🔬 Medicine Image Analysis\n\n{analysis_result}"
                })

                # Increment counter to reset the uploader
                st.session_state[input_counter_key] = st.session_state.get(input_counter_key, 0) + 1

                st.rerun()

    # ── Input bar: text field | Send button ─────────────

    prompt_key = f"chat_prompt_{role}_{user_data.get('id', 0)}_{st.session_state[input_counter_key]}"

    c_inp, c_send = st.columns([4.5, 1.1])

    user_prompt = c_inp.text_input(
        "Chat Input",
        placeholder="Ask SmartCare AI (e.g. 'list doctors', 'my health', 'book appointment')...",
        label_visibility="collapsed",
        key=prompt_key
    )

    send_clicked = c_send.button("Send ➤", type="primary", use_container_width=True, key=f"send_btn_{role}_{user_data.get('id',0)}")

    # Handle text send

    if send_clicked and user_prompt.strip():

        st.session_state[history_key].append({"role": "user", "content": user_prompt.strip()})

        st.session_state[input_counter_key] += 1

        with st.spinner("🤖 SmartCare AI is thinking & querying database..."):

            reply = process_ai_care_message(st.session_state[history_key], user_data)

        st.session_state[history_key].append({"role": "assistant", "content": reply})

        st.rerun()

    # ── APPOINTMENT BOOKING FORM ────────────────────────────────────────────────

    booking_form_key = f"booking_form_{role}_{user_id}"

    booking_state_key = f"booking_state_{role}_{user_id}"

    booking_closed_key = f"booking_closed_{role}_{user_id}"

    # Check if we should show the booking form

    show_booking_form = False

    # Check if form was explicitly closed - don't reopen

    if not st.session_state.get(booking_closed_key, False):

        if st.session_state.get("_force_hide_booking", False):

            st.session_state["_force_hide_booking"] = False

        else:

            if booking_state_key in st.session_state and st.session_state[booking_state_key] == "show_form":

                show_booking_form = True

            # Check last user message for booking intent

            if st.session_state.get(history_key):

                last_msgs = st.session_state[history_key][-3:]

                for msg in last_msgs:

                    if msg.get("role") == "user":

                        msg_text = msg.get("content", "").lower()

                        if any(kw in msg_text for kw in ["book appointment", "book an appointment", "want to book", "need appointment", "schedule appointment", "book doctor", "book dr", "booking appointment", "book a doctor", "appointment with", "booking appoitnment"]):

                            show_booking_form = True

                            break

    if show_booking_form and role != "doctor":

        doctors = db.fetch_all_doctors()

        if doctors:

            # Booking Form Header

            st.markdown(
                '<div style="background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(20,184,166,0.15)); '
                'border: 1px solid rgba(14,165,233,0.3); border-radius: 16px; '
                'padding: 1rem 1.5rem; margin: 1rem 0; font-size: 1.3rem; font-weight: 700; color: #0f172a;">'
                '📅 Book Appointment'
                '</div>',
                unsafe_allow_html=True
            )

            # Initialize booking form state

            if booking_form_key not in st.session_state:

                st.session_state[booking_form_key] = {

                    "doctor": None,

                    "date": None,

                    "slot": None,

                    "step": 1

                }

            form_data = st.session_state[booking_form_key]

            current_step = form_data.get("step", 1)

            # Step indicator

            step_icons = ["👤", "📅", "⏰", "✅"]

            step_labels = ["Select Doctor", "Select Date", "Select Time", "Confirm"]

            steps_html = '<div style="display: flex; justify-content: space-between; margin-bottom: 1.5rem;">'

            for i, (icon, label) in enumerate(zip(step_icons, step_labels), 1):

                active = "color: #38bdf8; font-weight: 700;" if i <= current_step else "color: #64748b;"

                completed = "color: #14b8a6;" if i < current_step else ""

                steps_html += f'<div style="text-align: center; {active} {completed}">'

                steps_html += f'<div style="font-size: 1.5rem;">{icon}</div>'

                steps_html += f'<div style="font-size: 0.7rem;">{label}</div>'

                steps_html += '</div>'

            steps_html += '</div>'

            st.markdown(steps_html, unsafe_allow_html=True)

            # Step 1: Select Doctor

            if current_step == 1:

                doctor_options = ["Select a Doctor..."] + [f"Dr. {d['full_name']} ({d['specialty'] or 'General'}) - ₹{d['consultation_fee']}" for d in doctors]

                selected_doctor_idx = st.selectbox(

                    "👤 Step 1: Select Doctor",

                    range(len(doctor_options)),

                    format_func=lambda x: doctor_options[x],

                    key=f"doc_select_{role}_{user_id}"

                )

                if selected_doctor_idx > 0:

                    selected_doctor = doctors[selected_doctor_idx - 1]

                    form_data["doctor"] = selected_doctor

                    if st.button("Next: Select Date →", key=f"next_date_{role}_{user_id}"):

                        form_data["step"] = 2

                        st.session_state[booking_form_key] = form_data

                        st.rerun()

            # Step 2: Select Date

            elif current_step == 2:

                doctor = form_data.get("doctor")

                if doctor:

                    st.markdown(f"**Selected Doctor:** Dr. {doctor['full_name']} ({doctor.get('specialty', 'General')})", unsafe_allow_html=True)

                min_date = dt.today().date()

                max_date = dt.today().date() + timedelta(days=60)

                selected_date = st.date_input(

                    "📅 Step 2: Select Date",

                    value=min_date,

                    min_value=min_date,

                    max_value=max_date,

                    key=f"date_select_{role}_{user_id}"

                )

                col_back1, col_next1 = st.columns([1, 1])

                with col_back1:

                    if st.button("← Back", key=f"back_doc_{role}_{user_id}"):

                        form_data["step"] = 1

                        st.session_state[booking_form_key] = form_data

                        st.rerun()

                with col_next1:

                    if st.button("Next: Select Time →", key=f"next_time_{role}_{user_id}"):

                        form_data["date"] = str(selected_date)

                        form_data["step"] = 3

                        st.session_state[booking_form_key] = form_data

                        st.rerun()

            # Step 3: Select Time

            elif current_step == 3:

                doctor = form_data.get("doctor")

                book_date = form_data.get("date")

                if doctor and book_date:

                    st.markdown(f"**Doctor:** {doctor['full_name']} | **Date:** {book_date}", unsafe_allow_html=True)

                    # Get available slots

                    available_slots = []

                    all_slots = [

                        ("09:00:00", "09:00 AM", "09:30 AM"),

                        ("10:00:00", "10:00 AM", "10:30 AM"),

                        ("11:00:00", "11:00 AM", "11:30 AM"),

                        ("14:00:00", "02:00 PM", "02:30 PM"),

                        ("15:00:00", "03:00 PM", "03:30 PM"),

                        ("16:00:00", "04:00 PM", "04:30 PM"),

                        ("17:00:00", "05:00 PM", "05:30 PM"),

                    ]

                    for slot, start_label, end_label in all_slots:

                        if not db.check_slot_conflict(doctor["id"], book_date, slot):

                            available_slots.append((slot, f"{start_label} - {end_label}"))

                    if available_slots:

                        slot_options = ["Select a Time..."] + [f"{s[1]}" for s in available_slots]

                        selected_slot_idx = st.selectbox(

                            "⏰ Step 3: Select Time Slot",

                            range(len(slot_options)),

                            format_func=lambda x: slot_options[x],

                            key=f"slot_select_{role}_{user_id}"

                        )

                        if selected_slot_idx > 0:

                            selected_slot = available_slots[selected_slot_idx - 1]

                            form_data["slot"] = selected_slot[0]

                            form_data["slot_label"] = selected_slot[1]

                        col_back2, col_next2 = st.columns([1, 1])

                        with col_back2:

                            if st.button("← Back", key=f"back_date_{role}_{user_id}"):

                                form_data["step"] = 2

                                st.session_state[booking_form_key] = form_data

                                st.rerun()

                        with col_next2:

                            if selected_slot_idx > 0 and st.button("Next: Confirm →", key=f"next_confirm_{role}_{user_id}"):

                                form_data["step"] = 4

                                st.session_state[booking_form_key] = form_data

                                st.rerun()

                    else:

                        st.warning("⚠️ No slots available on this date. Please go back and select a different date.")

                        if st.button("← Go Back", key=f"back_no_slots_{role}_{user_id}"):

                            form_data["step"] = 2

                            st.session_state[booking_form_key] = form_data

                            st.rerun()

            # Step 4: Confirm

            elif current_step == 4:

                doctor = form_data.get("doctor")

                book_date = form_data.get("date")

                slot = form_data.get("slot")

                slot_label = form_data.get("slot_label")

                if doctor and book_date and slot:

                    # Calculate end time

                    hour = int(slot.split(":")[0])

                    end_slot = f"{hour+1}:00:00" if hour < 17 else "17:30:00"

                    if slot == "09:00:00":

                        end_slot = "09:30:00"

                    # Booking Summary

                    booking_html = (
                        f'<div style="background: rgba(30, 41, 59, 0.8); border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;">'
                        f'<div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin-bottom: 1rem;">📋 Booking Summary</div>'
                        f'<div style="color: #e2e8f0; line-height: 1.8;">'
                        f'<strong>👨\u200d⚕️ Doctor:</strong> {doctor["full_name"]}<br>'
                        f'<strong>🩺 Specialty:</strong> {doctor.get("specialty", "General Medicine")}<br>'
                        f'<strong>📅 Date:</strong> {book_date}<br>'
                        f'<strong>⏰ Time:</strong> {slot_label}<br>'
                        f'<strong>💰 Fee:</strong> ₹{doctor.get("consultation_fee", 0)}'
                        f'</div></div>'
                    )
                    st.markdown(booking_html, unsafe_allow_html=True)

                    col_confirm, col_cancel = st.columns([1, 1])

                    with col_confirm:

                        if st.button("✅ Confirm Booking", key=f"confirm_book_{role}_{user_id}", type="primary"):

                            # Book the appointment

                            booking_patient_id = user_id

                            if role == "admin":

                                patients = db.fetch_all_patients()

                                if patients:

                                    booking_patient_id = patients[0]["id"]

                            reason = "Booked via AI Care Assistant"

                            success, msg = db.book_appointment(booking_patient_id, doctor["id"], book_date, slot, end_slot, reason)

                            if success:

                                # Clear form and close

                                st.session_state[booking_form_key] = {

                                    "doctor": None,

                                    "date": None,

                                    "slot": None,

                                    "step": 1

                                }

                                st.session_state[booking_state_key] = None

                                # Add success message to chat

                                st.session_state[history_key].append({

                                    "role": "assistant",

                                    "content": f"✅ **Appointment Booked Successfully!**\n\n📅 **Date:** {book_date}\n⏰ **Time:** {slot_label}\n👨‍⚕️ **Doctor:** Dr. {doctor['full_name']}\n💰 **Fee:** ₹{doctor.get('consultation_fee', 0)}\n\n📌 **Status:** PENDING (Waiting for doctor confirmation)\n\n💬 Is there anything else I can help you with?"

                                })

                                st.rerun()

                            else:

                                st.error(f"❌ Booking Failed: {msg}")

                    with col_cancel:

                        if st.button("← Go Back", key=f"back_confirm_{role}_{user_id}"):

                            form_data["step"] = 3

                            st.session_state[booking_form_key] = form_data

                            st.rerun()

            # Close/Cancel button

            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)

            if st.button("✕ Close Booking Form", key=f"close_booking_{role}_{user_id}"):

                # Set flag to prevent reopening

                st.session_state[booking_closed_key] = True

                # Clear booking state completely

                st.session_state[booking_state_key] = None

                if booking_form_key in st.session_state:

                    del st.session_state[booking_form_key]

                # Remove the "booking form ready" message from chat history

                if st.session_state.get(history_key):

                    new_history = []

                    for msg in st.session_state[history_key]:

                        content = msg.get("content", "").lower()

                        # Skip messages about opening booking form

                        if msg.get("role") == "assistant" and "booking form" in content and "open" in content:

                            continue

                        new_history.append(msg)

                    st.session_state[history_key] = new_history

                # Force hide the form by setting a temp flag

                st.session_state["_force_hide_booking"] = True

                st.rerun()


    # Quick Action Pills


    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #9ca3af; text-transform: uppercase; margin-bottom: 6px;'>⚡ Quick Database Actions</div>", unsafe_allow_html=True)

    if role == "patient":

        q1, q2, q3, q4 = st.columns(4)

        if q1.button("📋 List Doctors", key=f"q_docs_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "List doctors"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q2.button("📅 My Appointments", key=f"q_appts_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Show my appointments"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q3.button("🩺 My Health Vitals", key=f"q_vitals_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "My health status"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q4.button("➕ Book Appointment", key=f"q_book_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Book appointment"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

    elif role == "doctor":

        q1, q2, q3, q4 = st.columns(4)

        if q1.button("📅 My Schedule", key=f"q_sched_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Show my schedule"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q2.button("🩺 All Doctors", key=f"q_docs_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "List doctors"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q3.button("👥 Patients Records", key=f"q_pats_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "My health records"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q4.button("💊 Pharmacy Stock", key=f"q_meds_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Show medicine stock"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

    elif role == "admin":

        q1, q2, q3, q4 = st.columns(4)

        if q1.button("📊 System Overview", key=f"q_sys_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Admin stats"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q2.button("👨‍⚕️ Doctors List", key=f"q_docs_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "List doctors"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q3.button("📅 Appointments Stats", key=f"q_appts_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Show appointments summary"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

        if q4.button("💊 Pharmacy Inventory", key=f"q_meds_{role}"):

            st.session_state[history_key].append({"role": "user", "content": "Show pharmacy inventory"})

            reply = process_ai_care_message(st.session_state[history_key], user_data)

            st.session_state[history_key].append({"role": "assistant", "content": reply})

            st.rerun()

    # Clear chat button

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    if st.button("🗑️ Clear Chat History", key=f"clear_ai_{role}_{user_data.get('id', 0)}"):

        st.session_state[history_key] = [

            {"role": "assistant", "content": f"Chat history cleared. How can I help you, {first_name}?"}

        ]

        st.rerun()
