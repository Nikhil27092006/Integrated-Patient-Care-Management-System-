import streamlit as st
import auth
import db as db_module
import base64
import os
from dotenv import load_dotenv

load_dotenv()

@st.cache_data
def _get_bg_image_b64() -> str:
    """Load the background image and return as a base64 data URI (cached)."""
    try:
        img_path = os.path.join(os.path.dirname(__file__), "background",
                                "Gemini_Generated_Image_cd9c9qcd9c9qcd9c.png")
        img_path = os.path.abspath(img_path)
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except Exception:
        return ""

@st.cache_data
def _get_logo_b64() -> str:
    """Load the custom logo image and return as a base64 data URI (cached)."""
    try:
        img_path = os.path.join(os.path.dirname(__file__), "static", "logo.jpg")
        img_path = os.path.abspath(img_path)
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/jpeg;base64,{data}"
    except Exception:
        return ""

# Load favicon image for browser tab
_favicon_path = os.path.join(os.path.dirname(__file__), "static", "logo.jpg")
try:
    from PIL import Image
    _page_icon = Image.open(_favicon_path)
except Exception:
    _page_icon = "🏥"

# Set page configuration with medical theme styling & custom logo favicon
st.set_page_config(
    page_title="PCMHS - Patient Care Management System for Healthcare Services",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Colorful White Medical Theme
_bg_uri = _get_bg_image_b64()
_LOGIN_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    /* ── App Background ───────────────────────────────────── */
    .stApp {
        background-image: url('app/static/background.png');
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        font-family: 'Inter', sans-serif;
        color: #0f172a;
    }
    .stApp::before {
        content: "";
        position: fixed; top: 0; left: 0;
        width: 100%; height: 100%;
        background: rgba(248, 250, 252, 0.88) !important;
        z-index: -1;
    }

    /* ── Hide Streamlit chrome ────────────────────────────── */
    header, footer, [data-testid="stHeader"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* ── Layout padding ───────────────────────────────────── */
    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] section.main > div {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }

    /* ── Global text guarantee ────────────────────────────── */
    p, span, label, div, h1, h2, h3, h4, h5, h6, li, td, th {
        color: #0f172a;
    }

    /* ── Alert boxes ──────────────────────────────────────── */
    [data-testid="stAlert"],
    [data-baseweb="notification"],
    div[role="alert"],
    div[class*="stAlert"],
    [data-testid="stNotification"],
    div[class*="stError"],
    div[class*="stWarning"],
    div[class*="stSuccess"],
    div[class*="stInfo"],
    .stException {
        border-radius: 12px !important;
        border-left-width: 5px !important;
        padding: 1rem 1.25rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 1.25rem !important;
        line-height: 1.6 !important;
        min-height: 48px !important;
        overflow: visible !important;
    }
    [data-testid="stAlert"] *, [data-baseweb="notification"] *,
    div[role="alert"] *, [data-testid="stNotification"] *,
    div[class*="stAlert"] *, .stException * {
        text-shadow: none !important;
        line-height: 1.6 !important;
        overflow: visible !important;
        font-size: 0.95rem !important;
        font-weight: 500 !important;
    }
    div[class*="stError"],
    [data-baseweb="notification"][kind="negative"] {
        background: #fef2f2 !important;
        border-left: 5px solid #dc2626 !important;
        color: #7f1d1d !important;
    }
    div[class*="stError"] * { color: #7f1d1d !important; }
    div[class*="stSuccess"],
    [data-baseweb="notification"][kind="positive"] {
        background: #f0fdf4 !important;
        border-left: 5px solid #059669 !important;
        color: #14532d !important;
    }
    div[class*="stSuccess"] * { color: #14532d !important; }
    div[class*="stWarning"],
    [data-baseweb="notification"][kind="warning"] {
        background: #fffbeb !important;
        border-left: 5px solid #d97706 !important;
        color: #78350f !important;
    }
    div[class*="stWarning"] * { color: #78350f !important; }
    div[class*="stInfo"],
    [data-baseweb="notification"][kind="info"] {
        background: #f0f9ff !important;
        border-left: 5px solid #0369a1 !important;
        color: #0c4a6e !important;
    }
    div[class*="stInfo"] * { color: #0c4a6e !important; }

    /* ── Login card ───────────────────────────────────────── */
    .auth-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px) saturate(160%);
        -webkit-backdrop-filter: blur(20px) saturate(160%);
        padding: 2.5rem 2.5rem;
        border-radius: 24px;
        box-shadow: 0 8px 40px rgba(3, 105, 161, 0.12),
                    0 2px 12px rgba(0, 0, 0, 0.06),
                    inset 0 1px 2px rgba(255, 255, 255, 1);
        border: 1.5px solid #e2e8f0;
        margin: 1.5rem auto;
        max-width: 520px;
        animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    /* ── Logo & titles ────────────────────────────────────── */
    .med-logo {
        text-align: center;
        margin-bottom: 0.8rem;
    }
    .med-logo-img {
        width: 90px;
        height: 90px;
        object-fit: contain;
        filter: drop-shadow(0 6px 20px rgba(13, 148, 136, 0.35));
        transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
        border-radius: 20px;
        background: #ffffff;
        padding: 8px;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    }
    .med-logo-img:hover {
        transform: scale(1.1) rotate(3deg);
    }
    .med-title {
        font-family: 'Plus Jakarta Sans', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #0f172a 0%, #0369a1 50%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: none;
    }
    .med-subtitle {
        color: #475569;
        font-size: 0.95rem;
        font-weight: 500;
        text-align: center;
        margin-bottom: 2rem;
    }

    /* ── Role selection buttons ───────────────────────────── */
    .role-selector-label {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #475569;
        margin-bottom: 0.6rem;
        display: block;
    }

    /* Patient role button */
    button[data-testid="baseButton-secondary"][key="btn_login_patient"],
    button[kind="secondary"] {
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        color: #0f172a !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
        transition: all 0.2s ease !important;
    }
    button[kind="secondary"]:hover {
        background: #f0f9ff !important;
        border-color: #0ea5e9 !important;
        color: #0369a1 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 14px rgba(3, 105, 161, 0.15) !important;
    }

    /* ── Inputs & Selectboxes ─────────────────────────────── */
    div[data-baseweb="input"],
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] > div > div {
        border-radius: 12px !important;
        border: 1.5px solid #cbd5e1 !important;
        background-color: #ffffff !important;
        color: #0f172a !important;
        transition: all 0.25s ease !important;
    }
    div[data-baseweb="input"]:focus-within,
    div[data-baseweb="select"] > div:focus-within {
        border-color: #0369a1 !important;
        box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.12) !important;
        background-color: #ffffff !important;
    }
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input,
    div[data-baseweb="value-container"] * {
        color: #0f172a !important;
        fill: #0f172a !important;
    }
    div[data-baseweb="select"] svg { fill: #0f172a !important; }
    input {
        color: #0f172a !important;
        font-family: 'Inter', sans-serif !important;
    }
    input::placeholder { color: #94a3b8 !important; }

    /* Popover dropdown menu */
    ul[data-baseweb="menu"],
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] > div,
    [data-baseweb="popover"] [role="listbox"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 12px !important;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
    }
    li[role="option"],
    div[role="option"],
    [data-baseweb="popover"] li,
    [data-baseweb="popover"] div,
    [data-baseweb="menu"] * {
        background-color: #ffffff !important;
        color: #0f172a !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 0.92rem !important;
    }
    li[role="option"]:hover,
    div[role="option"]:hover,
    [data-baseweb="menu"] li:hover {
        background-color: #e0f2fe !important;
        color: #0369a1 !important;
    }

    /* Widget label visibility */
    [data-testid="stWidgetLabel"],
    [data-testid="stWidgetLabel"] * {
        color: #0f172a !important;
        font-weight: 500 !important;
    }

    /* ── Tabs — login page ────────────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        background: #f1f5f9;
        padding: 6px;
        border-radius: 16px;
        margin-bottom: 1.8rem;
        border: 1.5px solid #e2e8f0;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        background-color: transparent;
        border-radius: 10px;
        color: #64748b !important;
        font-weight: 600;
        font-size: 0.9rem;
        transition: all 0.25s ease;
        flex: 1;
        text-align: center;
        border: none !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 14px rgba(3, 105, 161, 0.3) !important;
        border: none !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #ffffff !important;
        color: #0369a1 !important;
    }

    /* ── Primary button ───────────────────────────────────── */
    button[kind="primary"] {
        background: linear-gradient(135deg, #0369a1 0%, #0ea5e9 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.02em;
        box-shadow: 0 4px 18px rgba(3, 105, 161, 0.3) !important;
        transition: all 0.3s ease !important;
        width: 100% !important;
    }
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 28px rgba(3, 105, 161, 0.45) !important;
        background: linear-gradient(135deg, #0ea5e9 0%, #0369a1 100%) !important;
    }
    button[kind="primary"]:active { transform: translateY(0) !important; }

    /* ── Bottom-left compliance card ──────────────────────── */
    .bottom-left-decor {
        position: fixed;
        bottom: 24px; left: 24px;
        background: rgba(255, 255, 255, 0.97);
        backdrop-filter: blur(20px);
        border: 1.5px solid #e2e8f0;
        border-radius: 16px;
        padding: 16px;
        max-width: 280px;
        box-shadow: 0 8px 30px rgba(3, 105, 161, 0.12);
        z-index: 999;
        animation: slideRight 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    @keyframes slideRight {
        from { opacity: 0; transform: translateX(-30px); }
        to   { opacity: 1; transform: translateX(0); }
    }

    /* ── Google OAuth button ──────────────────────────────── */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #ffffff;
        color: #0f172a;
        border: 1.5px solid #e2e8f0;
        padding: 0.8rem 1.5rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        text-decoration: none;
        transition: all 0.25s ease;
        margin-top: 1rem;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
    }
    .google-btn:hover {
        background-color: #f0f9ff;
        border-color: #0ea5e9;
        box-shadow: 0 6px 20px rgba(3, 105, 161, 0.18);
        color: #0f172a;
        transform: translateY(-2px);
    }
    .google-icon { margin-right: 12px; width: 22px; height: 22px; }

    /* ── Divider ──────────────────────────────────────────── */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #94a3b8;
        margin: 2rem 0 1rem 0;
        font-size: 0.8rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    .divider::before, .divider::after {
        content: ''; flex: 1;
        border-bottom: 1px solid #e2e8f0;
    }
    .divider:not(:empty)::before { margin-right: 1em; }
    .divider:not(:empty)::after  { margin-left: 1em; }

    /* ── Role button highlights (active role indicator) ───── */
    .role-active-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .role-badge-patient {
        background: #e0f2fe;
        color: #0369a1;
        border: 1.5px solid #7dd3fc;
    }
    .role-badge-doctor {
        background: #d1fae5;
        color: #059669;
        border: 1.5px solid #6ee7b7;
    }
    .role-badge-admin {
        background: #fef3c7;
        color: #d97706;
        border: 1.5px solid #fcd34d;
    }

</style>
"""
st.markdown(_LOGIN_CSS, unsafe_allow_html=True)
if _bg_uri:
    st.markdown(f"<style>.stApp {{ background-image: url('{_bg_uri}') !important; }}</style>", unsafe_allow_html=True)

# Get current DB type for status indicator
try:
    _db_type = db_module.current_db_type
    _db_color = "#14b8a6" if "MySQL" in _db_type else "#f59e0b"
    _db_label = f"MySQL Connected" if "MySQL" in _db_type else "SQLite Active"
except:
    _db_color = "#9ca3af"
    _db_label = "DB Initializing"

# Initialize Session State
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_data" not in st.session_state:
    st.session_state.user_data = None
if "oauth_flow" not in st.session_state:
    st.session_state.oauth_flow = False
if "oauth_user" not in st.session_state:
    st.session_state.oauth_user = None
if "selected_role" not in st.session_state:
    st.session_state.selected_role = "Patient"
if "processed_codes" not in st.session_state:
    st.session_state.processed_codes = set()

# Hide Sidebar ONLY on Login page; force it VISIBLE for all authenticated users
if not st.session_state.authenticated:
    # --- Login page: hide sidebar and collapse control ---
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        display: none !important;
        visibility: hidden !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="bottom-left-decor">
        <div style="font-size: 0.72rem; text-transform: uppercase; color: #059669; font-weight: 800; letter-spacing: 0.08em; display: flex; align-items: center; gap: 6px;">
            <span style="display:inline-block; width:6px; height:6px; background:#059669; border-radius:50%; box-shadow: 0 0 6px #059669;"></span>
            HIPAA COMPLIANT
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #0f172a; margin-top: 6px;">
            🔒 Secure CareNet Gateway
        </div>
        <div style="font-size: 0.75rem; color: #475569; margin-top: 4px; line-height: 1.4;">
            End-to-end encrypted medical logs. Unauthorized access is strictly monitored.
        </div>
        <div style="display: flex; align-items: center; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px solid #e2e8f0;">
            <span style="display:inline-block; width:6px; height:6px; background:{_db_color}; border-radius:50%; box-shadow: 0 0 6px {_db_color}; flex-shrink:0;"></span>
            <span style="font-size: 0.72rem; color: {_db_color}; font-weight: 700;">{_db_label}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # --- Authenticated: permanently force sidebar visible for ALL user types ---
    st.markdown("""
    <style>
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        display: flex !important;
        visibility: visible !important;
        opacity: 1 !important;
        transform: none !important;
        pointer-events: auto !important;
        width: 255px !important;
        min-width: 230px !important;
        max-width: 255px !important;
        position: relative !important;
        flex-shrink: 0 !important;
    }
    section[data-testid="stSidebar"] > div {
        display: flex !important;
        flex-direction: column !important;
        visibility: visible !important;
    }
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Handle Google OAuth Callback Redirect parameters
query_params = st.query_params
if "code" in query_params:
    code = query_params["code"]
    if code not in st.session_state.processed_codes:
        st.session_state.processed_codes.add(code)
        # Clear query parameters to clean up URL
        st.query_params.clear()
        
        # Retrieve user info from Google
        user_info, error = auth.get_google_user_info(code)
        if error:
            st.error(error)
        elif user_info:
            st.session_state.oauth_flow = True
            st.session_state.oauth_user = user_info

# Logout helper
def logout():
    st.session_state.authenticated = False
    st.session_state.user_data = None
    st.session_state.oauth_flow = False
    st.session_state.oauth_user = None
    st.session_state.selected_role = "Patient"
    st.rerun()

# ----------------- MAIN RENDERING -----------------

# Verify MySQL connection strictly
db_conn_ok = False
db_err_msg = ""
try:
    _conn, _ = db_module.get_connection()
    _conn.close()
    db_conn_ok = True
except Exception as e:
    db_conn_ok = False
    db_err_msg = str(e)

if not db_conn_ok:
    st.markdown("""
    <div class="auth-card">
        <div class="med-logo">⚙️</div>
        <h1 class="med-title">Database Setup</h1>
        <div class="med-subtitle">Could not connect to the MySQL server. Configure your credentials below:</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.error(f"❌ Connection Error: {db_err_msg}")
    
    with st.form("mysql_setup_form"):
        h_host = st.text_input("MySQL Host", value="localhost")
        h_user = st.text_input("MySQL Username", value="root")
        h_pass = st.text_input("MySQL Password", type="password", value="")
        h_db   = st.text_input("Database Name", value="patient_care_db")
        
        if st.form_submit_button("Test Connection & Initialize Platform", type="primary", use_container_width=True):
            try:
                import pymysql
                # Test connection directly
                test_conn = pymysql.connect(host=h_host, user=h_user, password=h_pass, autocommit=True)
                cursor = test_conn.cursor()
                cursor.execute(f"CREATE DATABASE IF NOT EXISTS {h_db}")
                test_conn.close()
                
                # Write to config file
                with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_config.py"), "w") as f:
                    f.write("# MySQL Database Configuration\n")
                    f.write(f'MYSQL_HOST = "{h_host}"\n')
                    f.write(f'MYSQL_USER = "{h_user}"\n')
                    f.write(f'MYSQL_PASSWORD = "{h_pass}"\n')
                    f.write(f'MYSQL_DB = "{h_db}"\n')
                
                # Initialize database schemas
                db_module.initialize_database()
                st.success("✅ Connected and tables generated! Reloading portal...")
                st.rerun()
            except Exception as ex:
                st.error(f"❌ Connection failed: {ex}")
    st.stop()


if st.session_state.authenticated:
    # Route to the correct role-based dashboard
    user = st.session_state.user_data
    role = user.get("role", "Patient") if user else "Patient"

    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    if role == "Admin":
        from pages.admin_dashboard import render
        render()
    elif role == "Doctor":
        from pages.doctor_dashboard import render
        render()
    else:
        from pages.patient_dashboard import render
        render()

elif st.session_state.oauth_flow:
    # Google OAuth success callback, now prompt for role selection
    g_user = st.session_state.oauth_user
    email = g_user.get("email")
    name = g_user.get("name", "Google User")
    
    st.markdown(f"""
    <div class="auth-card">
        <h2 class="med-title">Complete Sign In</h2>
        <div class="med-subtitle">Logged in with Google as <b>{email}</b>. Select your role to continue:</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if the user already exists in DB
    user_data = auth.get_user_by_email(email)
    if user_data:
        # Existing user - auto-login with stored role
        st.session_state.authenticated = True
        st.session_state.user_data = user_data
        st.session_state.oauth_flow = False
        st.rerun()

    else:
        # New Google user - prompt for Patient or Admin role choice
        role_choice = st.selectbox("Select Your Role", ["Patient", "Admin"])
        
        if st.button("Confirm and Log In", type="primary", use_container_width=True):
            # Register user into database
            auth.register_user(email, "google-oauth-placeholder", name, role_choice)
            new_user = auth.get_user_by_email(email)
            st.session_state.authenticated = True
            st.session_state.user_data = new_user
            st.session_state.oauth_flow = False
            st.success("Registration complete!")
            st.rerun()


else:
    # Login / Signup landing forms
    _logo_data = _get_logo_b64()
    _logo_markup = f'<img src="{_logo_data}" class="med-logo-img" alt="PCMHS Logo" />' if _logo_data else '<span>🏥</span>'

    st.markdown(f"""
    <div class="med-logo">
        {_logo_markup}
    </div>
    <div class="med-title">CareNet Platform</div>
    <div class="med-subtitle">Patient Care Management System for Healthcare Services</div>
    """, unsafe_allow_html=True)

    # Modern CSS styled login container
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    # Segmented Control / Tabs
    tab_login, tab_signup, tab_chatbot = st.tabs(["🔒 Secure Login", "📝 Create Account", "🤖 AI Chatbot"])
    
    with tab_login:
        st.markdown("<p class='role-selector-label'>SELECT PORTAL ROLE</p>", unsafe_allow_html=True)
        col_pat, col_doc, col_adm = st.columns(3)
        with col_pat:
            is_pat = st.session_state.selected_role == "Patient"
            if st.button(
                "👤 Patient",
                key="btn_login_patient",
                use_container_width=True,
                type="primary" if is_pat else "secondary"
            ):
                st.session_state.selected_role = "Patient"
                st.rerun()
        with col_doc:
            is_doc = st.session_state.selected_role == "Doctor"
            if st.button(
                "🩺 Doctor",
                key="btn_login_doctor",
                use_container_width=True,
                type="primary" if is_doc else "secondary"
            ):
                st.session_state.selected_role = "Doctor"
                st.rerun()
        with col_adm:
            is_adm = st.session_state.selected_role == "Admin"
            if st.button(
                "🔑 Admin",
                key="btn_login_admin",
                use_container_width=True,
                type="primary" if is_adm else "secondary"
            ):
                st.session_state.selected_role = "Admin"
                st.rerun()

        # Highlight active role choice with a colorful badge
        _role_badge_cls = {"Patient": "role-badge-patient", "Doctor": "role-badge-doctor", "Admin": "role-badge-admin"}
        _role_icons     = {"Patient": "👤", "Doctor": "🩺", "Admin": "🔑"}
        _badge_cls = _role_badge_cls.get(st.session_state.selected_role, "role-badge-patient")
        _icon      = _role_icons.get(st.session_state.selected_role, "👤")
        st.markdown(
            f"<div style='text-align:center; margin-bottom:1.2rem;'>"
            f"<span class='role-active-badge {_badge_cls}'>{_icon} {st.session_state.selected_role} Portal Selected</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        email = st.text_input("Email Address", placeholder="e.g. name@carenet.com", key="login_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_pass")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign In", type="primary", use_container_width=True):
            if not email or not password:
                st.error("Please fill in all fields.")
            else:
                success, response = auth.authenticate_user(email, password, st.session_state.selected_role)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user_data = {
                        "id": response["id"],
                        "email": email,
                        "name": response["name"],
                        "role": response["role"]
                    }
                    st.success("Successfully logged in!")
                    st.rerun()
                else:
                    st.error(response)
                    
    with tab_signup:
        st.markdown("<p class='role-selector-label'>REGISTER AS</p>", unsafe_allow_html=True)
        col_pat_s, col_adm_s = st.columns(2)
        if st.session_state.selected_role not in ["Patient", "Admin"]:
            st.session_state.selected_role = "Patient"
        with col_pat_s:
            is_pat_s = st.session_state.selected_role == "Patient"
            if st.button(
                "👤 Patient",
                key="btn_signup_patient",
                use_container_width=True,
                type="primary" if is_pat_s else "secondary"
            ):
                st.session_state.selected_role = "Patient"
                st.rerun()
        with col_adm_s:
            is_adm_s = st.session_state.selected_role == "Admin"
            if st.button(
                "🔑 Admin",
                key="btn_signup_admin",
                use_container_width=True,
                type="primary" if is_adm_s else "secondary"
            ):
                st.session_state.selected_role = "Admin"
                st.rerun()

        _role_badge_cls2 = {"Patient": "role-badge-patient", "Admin": "role-badge-admin"}
        _role_icons2     = {"Patient": "👤", "Admin": "🔑"}
        _badge_cls2 = _role_badge_cls2.get(st.session_state.selected_role, "role-badge-patient")
        _icon2      = _role_icons2.get(st.session_state.selected_role, "👤")
        st.markdown(
            f"<div style='text-align:center; margin-bottom:1.2rem;'>"
            f"<span class='role-active-badge {_badge_cls2}'>{_icon2} {st.session_state.selected_role} Account</span>"
            f"</div>",
            unsafe_allow_html=True
        )
        
        name_signup = st.text_input("Full Name", placeholder="e.g. John Doe", key="signup_name")
        email_signup = st.text_input("Email Address", placeholder="e.g. john@domain.com", key="signup_email")
        password_signup = st.text_input("Password", type="password", placeholder="••••••••", key="signup_pass")
        confirm_pass = st.text_input("Confirm Password", type="password", placeholder="••••••••", key="signup_confirm")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Sign Up", type="primary", use_container_width=True):
            if not name_signup or not email_signup or not password_signup or not confirm_pass:
                st.error("Please fill in all fields.")
            elif password_signup != confirm_pass:
                st.error("Passwords do not match.")
            else:
                success, msg = auth.register_user(email_signup, password_signup, name_signup, st.session_state.selected_role)
                if success:
                    st.success("Registration successful! You can now log in.")
                else:
                    st.error(msg)

    with tab_chatbot:
        import chatbot
        chatbot.render_public_chatbot()
                    
    # Divider for OAuth
    st.markdown('<div class="divider">or continue with</div>', unsafe_allow_html=True)
    
    # Google OAuth Sign-in Button
    google_url = auth.get_google_auth_url()
    st.markdown(f"""
        <a href="{google_url}" target="_self" class="google-btn">
            <svg class="google-icon" viewBox="0 0 24 24">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z"/>
            </svg>
            Continue with Google
        </a>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Demo Credentials helper for easy review
    with st.expander("💡 View Demo Test Accounts"):
        st.markdown("""
        **Patients:** `patient@care.com` / `patient123`
        **Doctors:** `doctor@care.com` / `doctor123`
        **Admins:** `admin@care.com` / `admin123`
        """)
