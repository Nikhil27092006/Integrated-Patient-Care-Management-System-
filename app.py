import streamlit as st
import auth
import db as db_module
import base64
import os

def _get_bg_image_b64() -> str:
    """Load the background image and return as a base64 data URI."""
    img_path = os.path.join(os.path.dirname(__file__), "background",
                            "WhatsApp Image 2026-07-21 at 9.26.52 PM.jpeg")
    img_path = os.path.abspath(img_path)
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{data}"

# Set page configuration with medical theme styling
st.set_page_config(
    page_title="IPCMS - Integrated Patient Care Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Deep Obsidian & Neon Teal/Cyan Medical Theme
_bg_uri = _get_bg_image_b64()
_LOGIN_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
    
    /* Immersive Dark Background with background image */
    .stApp {
        background-image: url('__BG_IMAGE_URI__');
        background-size: cover !important;
        background-position: center center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
        font-family: 'Plus Jakarta Sans', sans-serif;
        color: #f3f4f6;
    }

    /* Dark overlay to make content readable */
    .stApp::before {
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(3, 7, 18, 0.85) !important;
        z-index: -1;
    }
    
    /* Hide Streamlit default UI elements */
    header, footer, [data-testid="stHeader"], [data-testid="stDecoration"] {
        visibility: hidden !important;
        height: 0px !important;
    }

    /* Prevent top text clipping */
    .block-container,
    [data-testid="stMainBlockContainer"],
    [data-testid="stAppViewContainer"] section.main > div {
        padding-top: 2.5rem !important;
        padding-bottom: 2.5rem !important;
    }

    /* Alert & notification box formatting */
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
        border-radius: 14px !important;
        border-left-width: 6px !important;
        backdrop-filter: blur(12px) !important;
        padding: 1rem 1.25rem !important;
        margin-top: 0.75rem !important;
        margin-bottom: 1.25rem !important;
        line-height: 1.6 !important;
        min-height: 52px !important;
        overflow: visible !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4) !important;
    }

    [data-testid="stAlert"] *,
    [data-baseweb="notification"] *,
    div[role="alert"] *,
    [data-testid="stNotification"] *,
    div[class*="stAlert"] *,
    .stException * {
        color: #ffffff !important;
        text-shadow: 0 1px 4px rgba(0, 0, 0, 0.7) !important;
        line-height: 1.6 !important;
        overflow: visible !important;
        vertical-align: middle !important;
        font-size: 0.98rem !important;
        font-weight: 500 !important;
    }

    div[class*="stError"],
    div[class*="Alert"][class*="error"],
    [data-baseweb="notification"][kind="negative"] {
        background: rgba(220, 38, 38, 0.35) !important;
        border: 1px solid rgba(239, 68, 68, 0.7) !important;
        border-left: 6px solid #ef4444 !important;
        color: #ffffff !important;
    }
    
    /* Neon Glassmorphism Card */
    .auth-card {
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(20px) saturate(180%);
        -webkit-backdrop-filter: blur(20px) saturate(180%);
        padding: 3rem 2.5rem;
        border-radius: 28px;
        box-shadow: 0 0 40px rgba(14, 165, 233, 0.15), 
                    inset 0 1px 2px rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(14, 165, 233, 0.25);
        margin: 2rem auto;
        max-width: 540px;
        animation: slideUp 0.7s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Glowing Title & Identity */
    .med-logo {
        text-align: center;
        font-size: 4rem;
        margin-bottom: 0.5rem;
        filter: drop-shadow(0 0 20px rgba(20, 184, 166, 0.6));
    }
    
    .med-title {
        font-family: 'Space Grotesk', sans-serif;
        color: #ffffff;
        font-size: 2.5rem;
        font-weight: 700;
        text-align: center;
        letter-spacing: -0.03em;
        margin-bottom: 0.5rem;
        background: linear-gradient(135deg, #ffffff 30%, #0ea5e9 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 12px rgba(14, 165, 233, 0.1);
    }
    
    .med-subtitle {
        color: #9ca3af;
        font-size: 1.05rem;
        font-weight: 400;
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    /* Styled Input Fields (Streamlit overrides for dark mode) */
    div[data-baseweb="input"] {
        border-radius: 14px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        background-color: rgba(3, 7, 18, 0.6) !important;
        transition: all 0.25s ease !important;
    }
    
    div[data-baseweb="input"]:focus-within {
        border-color: #14b8a6 !important;
        box-shadow: 0 0 15px rgba(20, 184, 166, 0.25) !important;
        background-color: rgba(3, 7, 18, 0.8) !important;
    }
    
    input {
        color: #f3f4f6 !important;
    }
    
    /* Custom tab navigation styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        background-color: rgba(3, 7, 18, 0.6);
        padding: 8px;
        border-radius: 18px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 44px;
        background-color: transparent;
        border-radius: 12px;
        color: #9ca3af;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        flex: 1;
        text-align: center;
        border: none !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #0ea5e9 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4) !important;
    }
    
    /* Styled Submit Button */
    button[kind="primary"] {
        background: linear-gradient(135deg, #0ea5e9 0%, #14b8a6 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        padding: 0.85rem 1.5rem !important;
        font-weight: 700 !important;
        font-size: 1.05rem !important;
        letter-spacing: 0.025em;
        box-shadow: 0 4px 20px rgba(14, 165, 233, 0.3) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        width: 100% !important;
    }
    
    button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 24px rgba(20, 184, 166, 0.45) !important;
        background: linear-gradient(135deg, #14b8a6 0%, #0ea5e9 100%) !important;
    }
    
    button[kind="primary"]:active {
        transform: translateY(0) !important;
    }
    
    /* Role Card Selector CSS */
    .role-container {
        display: flex;
        gap: 12px;
        margin-bottom: 1.5rem;
    }
    
    .role-option {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 12px;
        text-align: center;
        cursor: pointer;
        transition: all 0.25s ease;
    }
    
    .role-option:hover {
        background: rgba(14, 165, 233, 0.05);
        border-color: rgba(14, 165, 233, 0.3);
    }
    
    .role-option.active {
        background: rgba(14, 165, 233, 0.12);
        border-color: #0ea5e9;
        box-shadow: 0 0 15px rgba(14, 165, 233, 0.2);
    }
    
    /* Fixed Bottom Left Compliance Card */
    .bottom-left-decor {
        position: fixed;
        bottom: 24px;
        left: 24px;
        background: rgba(17, 24, 39, 0.6);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(14, 165, 233, 0.2);
        border-radius: 16px;
        padding: 16px;
        max-width: 280px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 999;
        animation: slideRight 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    }
    
    @keyframes slideRight {
        from {
            opacity: 0;
            transform: translateX(-30px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    
    /* Google OAuth Button */
    .google-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: rgba(255, 255, 255, 0.05);
        color: #f3f4f6;
        border: 1px solid rgba(255, 255, 255, 0.1);
        padding: 0.85rem 1.5rem;
        border-radius: 14px;
        font-weight: 600;
        font-size: 1rem;
        text-decoration: none;
        transition: all 0.25s ease;
        margin-top: 1rem;
    }
    
    .google-btn:hover {
        background-color: rgba(255, 255, 255, 0.1);
        border-color: rgba(14, 165, 233, 0.5);
        box-shadow: 0 0 20px rgba(14, 165, 233, 0.2);
        color: #ffffff;
        transform: translateY(-1px);
    }
    
    .google-icon {
        margin-right: 12px;
        width: 22px;
        height: 22px;
    }
    
    /* Divider styling */
    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        color: #6b7280;
        margin: 2.2rem 0 1.2rem 0;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.1em;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .divider:not(:empty)::before {
        margin-right: 1.2em;
    }
    
    .divider:not(:empty)::after {
        margin-left: 1.2em;
    }
    
</style>
"""
st.markdown(_LOGIN_CSS.replace("__BG_IMAGE_URI__", _bg_uri), unsafe_allow_html=True)

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
        <div style="font-size: 0.75rem; text-transform: uppercase; color: #14b8a6; font-weight: 800; letter-spacing: 0.08em; display: flex; align-items: center; gap: 6px;">
            <span style="display:inline-block; width:6px; height:6px; background:#14b8a6; border-radius:50%; box-shadow: 0 0 8px #14b8a6;"></span>
            HIPAA COMPLIANT
        </div>
        <div style="font-size: 0.85rem; font-weight: 700; color: #ffffff; margin-top: 6px;">
            Secure CareNet Gateway
        </div>
        <div style="font-size: 0.75rem; color: #9ca3af; margin-top: 4px; line-height: 1.4;">
            End-to-end encrypted medical logs. Unauthorized access is strictly monitored.
        </div>
        <div style="display: flex; align-items: center; gap: 6px; margin-top: 10px; padding-top: 8px; border-top: 1px solid rgba(255,255,255,0.08);">
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
    st.markdown("""
    <div class="med-logo">
        <span>🏥</span>
    </div>
    <div class="med-title">CareNet Platform</div>
    <div class="med-subtitle">Integrated Patient Care Management System</div>
    """, unsafe_allow_html=True)

    # Modern CSS styled login container
    st.markdown('<div class="auth-card">', unsafe_allow_html=True)
    
    # Segmented Control / Tabs
    tab_login, tab_signup = st.tabs(["🔒 Secure Login", "📝 Create Account"])
    
    with tab_login:
        st.markdown("<p style='font-size:0.9rem; color:#9ca3af; margin-bottom:0.5rem;'>SELECT PORTAL ROLE</p>", unsafe_allow_html=True)
        col_pat, col_doc, col_adm = st.columns(3)
        with col_pat:
            if st.button("👤 Patient", key="btn_login_patient", use_container_width=True, type="secondary"):
                st.session_state.selected_role = "Patient"
        with col_doc:
            if st.button("🩺 Doctor", key="btn_login_doctor", use_container_width=True, type="secondary"):
                st.session_state.selected_role = "Doctor"
        with col_adm:
            if st.button("🔑 Admin", key="btn_login_admin", use_container_width=True, type="secondary"):
                st.session_state.selected_role = "Admin"
                
        # Highlight active role choice
        st.markdown(f"<div style='text-align:center; font-size:0.9rem; font-weight:600; color:#14b8a6; margin-bottom:1.5rem;'>Access Level Selected: {st.session_state.selected_role}</div>", unsafe_allow_html=True)
        
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
        st.markdown("<p style='font-size:0.9rem; color:#9ca3af; margin-bottom:0.5rem;'>REGISTER AS</p>", unsafe_allow_html=True)
        col_pat_s, col_adm_s = st.columns(2)
        with col_pat_s:
            if st.button("👤 Patient", key="btn_signup_patient", use_container_width=True):
                st.session_state.selected_role = "Patient"
        with col_adm_s:
            if st.button("🔑 Admin", key="btn_signup_admin", use_container_width=True):
                st.session_state.selected_role = "Admin"
                
        if st.session_state.selected_role not in ["Patient", "Admin"]:
            st.session_state.selected_role = "Patient"
            
        st.markdown(f"<div style='text-align:center; font-size:0.9rem; font-weight:600; color:#14b8a6; margin-bottom:1.5rem;'>Account Type Selected: {st.session_state.selected_role}</div>", unsafe_allow_html=True)
        
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
