"""
Shared CSS theme — Professional White Medical Theme with Colorful Accents.
Fixes all visibility issues: role buttons, sidebar text, badges, prescription text, etc.
"""
import streamlit as st
import base64
import os
import sys
# Allow importing from project root even when this module lives in pages/
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

@st.cache_data
def _get_bg_image_b64() -> str:
    """Load the background image and return as a base64 data URI (cached)."""
    try:
        img_path = os.path.join(os.path.dirname(__file__), "..", "background",
                                "Gemini_Generated_Image_cd9c9qcd9c9qcd9c.png")
        img_path = os.path.abspath(img_path)
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except Exception:
        return ""

@st.cache_data
def _get_medical_banner_b64() -> str:
    """Load the user's custom medical banner image as base64 data URI (cached)."""
    try:
        img_path = os.path.join(os.path.dirname(__file__), "..", "static", "medical_banner.png")
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
        img_path = os.path.join(os.path.dirname(__file__), "..", "static", "logo.jpg")
        img_path = os.path.abspath(img_path)
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/jpeg;base64,{data}"
    except Exception:
        return ""

def _get_card_img_b64(index: int) -> str:
    """Load one of the 4 stat-card images (1-indexed) and return as base64 data URI. No cache so fresh on each run."""
    ext = "png"
    try:
        img_path = os.path.join(os.path.dirname(__file__), "..", "static", f"card_img_{index}.{ext}")
        img_path = os.path.abspath(img_path)
        if not os.path.exists(img_path):
            return ""
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/{ext};base64,{data}"
    except Exception:
        return ""

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── Color Palette ──────────────────────────────────────────────────────── */
:root {
    /* Patient — Blue */
    --patient-500:  #0369a1;
    --patient-400:  #0ea5e9;
    --patient-100:  #e0f2fe;
    --patient-50:   #f0f9ff;

    /* Doctor — Emerald */
    --doctor-500:   #059669;
    --doctor-400:   #10b981;
    --doctor-100:   #d1fae5;
    --doctor-50:    #ecfdf5;

    /* Admin — Amber */
    --admin-500:    #d97706;
    --admin-400:    #f59e0b;
    --admin-100:    #fef3c7;
    --admin-50:     #fffbeb;

    /* AI / Purple */
    --purple-500:   #7c3aed;
    --purple-400:   #8b5cf6;
    --purple-100:   #ede9fe;
    --purple-50:    #f5f3ff;

    /* Semantic */
    --success:      #059669;
    --warning:      #d97706;
    --error:        #dc2626;
    --info:         #0369a1;

    /* Neutrals */
    --text-primary:   #000000;
    --text-secondary: #333333;
    --text-muted:     #333333;
    --border-light:   #e2e8f0;
    --border-medium:  #cbd5e1;
    --bg-white:       #ffffff;
    --bg-surface:     #f8fafc;
    --bg-muted:       #f1f5f9;
}

html, body, .stApp {
    font-family: 'Inter', 'DM Sans', sans-serif !important;
    color: var(--text-primary) !important;
}

/* ── App Background ────────────────────────────────────────────────────── */
.stApp {
    background-image: url('{BG_IMAGE_URI}') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

[data-testid="stAppViewContainer"] {
    background-image: url('{BG_IMAGE_URI}') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* Frosted white overlay for readability */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(248, 250, 252, 0.93) !important;
    z-index: 0;
    pointer-events: none;
}

[data-testid="stHeader"],
[data-testid="stSidebar"] > div:first-child,
section.main > div {
    background: transparent !important;
}

[data-testid="stAppViewContainer"] > * {
    position: relative;
    z-index: 1;
}

.stApp::before {
    content: "";
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(248, 250, 252, 0.93) !important;
    z-index: -1;
}

header[data-testid="stHeader"],
[data-testid="stDecoration"],
footer { visibility: hidden !important; height: 0 !important; }

/* ── Padding ───────────────────────────────────────────────────────────── */
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] section.main > div {
    padding-top: 2.5rem !important;
    padding-bottom: 2.5rem !important;
}

/* ── Global text color guarantee ──────────────────────────────────────── */
p, span, label, div, li, td, th {
    color: var(--text-primary);
}
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
}

input, textarea, select, [data-baseweb="input"] input, [data-testid="stTextInput"] input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* ── Alert / Notification Boxes ───────────────────────────────────────── */
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
    border-left-width: 5px !important;
    backdrop-filter: blur(8px) !important;
    padding: 1rem 1.25rem !important;
    margin-top: 0.75rem !important;
    margin-bottom: 1.25rem !important;
    line-height: 1.6 !important;
    min-height: 52px !important;
    overflow: visible !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08) !important;
}

[data-testid="stAlert"] *,
[data-baseweb="notification"] *,
div[role="alert"] *,
[data-testid="stNotification"] *,
div[class*="stAlert"] *,
.stException * {
    text-shadow: none !important;
    line-height: 1.6 !important;
    overflow: visible !important;
    vertical-align: middle !important;
    font-size: 0.95rem !important;
    font-weight: 500 !important;
}

div[class*="stError"],
div[class*="Alert"][class*="error"],
[data-baseweb="notification"][kind="negative"] {
    background: #fef2f2 !important;
    border-left: 5px solid #dc2626 !important;
    color: #7f1d1d !important;
}
div[class*="stError"] *,
[data-baseweb="notification"][kind="negative"] * { color: #7f1d1d !important; }

div[class*="stWarning"],
div[class*="Alert"][class*="warning"],
[data-baseweb="notification"][kind="warning"] {
    background: #fffbeb !important;
    border-left: 5px solid #d97706 !important;
    color: #78350f !important;
}
div[class*="stWarning"] *,
[data-baseweb="notification"][kind="warning"] * { color: #78350f !important; }

div[class*="stSuccess"],
div[class*="Alert"][class*="success"],
[data-baseweb="notification"][kind="positive"] {
    background: #f0fdf4 !important;
    border-left: 5px solid #059669 !important;
    color: #14532d !important;
}
div[class*="stSuccess"] *,
[data-baseweb="notification"][kind="positive"] * { color: #14532d !important; }

div[class*="stInfo"],
div[class*="Alert"][class*="info"],
[data-baseweb="notification"][kind="info"] {
    background: #f0f9ff !important;
    border-left: 5px solid #0369a1 !important;
    color: #0c4a6e !important;
}
div[class*="stInfo"] *,
[data-baseweb="notification"][kind="info"] * { color: #0c4a6e !important; }

[data-testid="stSpinner"] * { color: var(--patient-500) !important; }

/* ── Audio Input ──────────────────────────────────────────────────────── */
[data-testid="stAudioInput"],
div[class*="stAudioInput"] {
    background: #ffffff !important;
    border: 1.5px solid var(--border-medium) !important;
    border-radius: 16px !important;
    padding: 1.2rem 1.5rem !important;
    margin-top: 1rem !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 0 2px 8px rgba(3, 105, 161, 0.08) !important;
}

[data-testid="stAudioInput"] label,
[data-testid="stAudioInput"] [data-testid="stWidgetLabel"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: var(--text-primary) !important;
    margin-bottom: 0.8rem !important;
}

/* ── Voice Wave Animation ─────────────────────────────────────────────── */
.voice-wave-container {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    height: 20px;
}
.voice-wave-container span {
    display: inline-block;
    width: 4px;
    height: 100%;
    background: linear-gradient(180deg, var(--patient-500), var(--purple-400));
    border-radius: 4px;
    animation: wave-bounce 1.2s ease-in-out infinite;
}
.voice-wave-container span:nth-child(2) { animation-delay: 0.15s; }
.voice-wave-container span:nth-child(3) { animation-delay: 0.3s; }
.voice-wave-container span:nth-child(4) { animation-delay: 0.45s; }
.voice-wave-container span:nth-child(5) { animation-delay: 0.6s; }

@keyframes wave-bounce {
    0%, 100% { height: 6px; opacity: 0.4; }
    50% { height: 20px; opacity: 1; }
}

.voice-instructions {
    font-size: 0.85rem;
    color: var(--text-secondary);
    line-height: 1.6;
    margin-top: 0.8rem;
    padding: 1rem;
    background: var(--purple-50);
    border-radius: 10px;
    border-left: 3px solid var(--purple-400);
}

.mic-outer-ring {
    width: 80px; height: 80px;
    background: linear-gradient(145deg, #f0f9ff, #e0f2fe);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    border: 2px solid var(--patient-400);
    box-shadow: 0 8px 24px rgba(3, 105, 161, 0.2);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    animation: micGlowPulse 2.5s ease-in-out infinite;
}
.mic-outer-ring:hover {
    transform: scale(1.06);
    border-color: var(--purple-400);
    box-shadow: 0 12px 32px rgba(139, 92, 246, 0.3);
}
.mic-inner-circle {
    width: 50px; height: 50px;
    background: linear-gradient(135deg, var(--patient-500), var(--purple-400));
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 16px rgba(3, 105, 161, 0.4);
}
@keyframes micGlowPulse {
    0%, 100% { box-shadow: 0 8px 24px rgba(3, 105, 161, 0.2), 0 0 0 0 rgba(3, 105, 161, 0.2); }
    50% { box-shadow: 0 8px 24px rgba(3, 105, 161, 0.2), 0 0 0 12px rgba(3, 105, 161, 0); }
}

/* ── Medical Animations ───────────────────────────────────────────────── */
.heart-pulse { position: relative; display: inline-block; }
.heart-pulse::before {
    content: '❤️'; display: block;
    animation: heartbeat 1.2s ease-in-out infinite;
}
@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.15); }
    30% { transform: scale(1); }
    45% { transform: scale(1.1); }
    60% { transform: scale(1); }
}

.ecg-line {
    position: relative; height: 40px;
    background: linear-gradient(90deg,
        transparent 0%, rgba(5,150,105,0.08) 20%,
        rgba(5,150,105,0.2) 40%, rgba(5,150,105,0.08) 60%, transparent 100%);
    border-radius: 4px; overflow: hidden; margin: 10px 0;
}
.ecg-line::after {
    content: ''; position: absolute; top: 0; left: -100%;
    width: 200%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(5,150,105,0.7) 50%, transparent);
    animation: ecg-scan 2s linear infinite;
}
@keyframes ecg-scan { 0% { left: -100%; } 100% { left: 100%; } }

.medical-cross {
    position: relative; display: inline-block;
    animation: cross-pulse 2s ease-in-out infinite;
}
@keyframes cross-pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 5px rgba(3, 105, 161, 0.4)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 14px rgba(3, 105, 161, 0.7)); }
}

.stethoscope-icon { display: inline-block; animation: stetho-bounce 2s ease-in-out infinite; }
@keyframes stetho-bounce {
    0%, 100% { transform: translateY(0) rotate(-5deg); }
    50% { transform: translateY(-5px) rotate(5deg); }
}

.pills-container { display: inline-flex; gap: 4px; }
.pills-container::before, .pills-container::after {
    content: '💊'; font-size: 1.2rem;
    animation: pill-float 2s ease-in-out infinite;
}
.pills-container::after { animation-delay: 0.5s; }
@keyframes pill-float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-4px) rotate(10deg); }
}

.hospital-glow { display: inline-block; animation: hospital-pulse 2s ease-in-out infinite; }
@keyframes hospital-pulse {
    0%, 100% { filter: drop-shadow(0 0 5px rgba(3, 105, 161, 0.4)); }
    50% { filter: drop-shadow(0 0 14px rgba(3, 105, 161, 0.8)); }
}

.heart-monitor { position: relative; display: inline-flex; align-items: center; gap: 8px; }
.heart-monitor::before {
    content: ''; width: 12px; height: 12px;
    background: var(--success); border-radius: 50%;
    animation: monitor-blink 1s ease-in-out infinite;
    box-shadow: 0 0 10px var(--success);
}
@keyframes monitor-blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px var(--success); }
    50% { opacity: 0.5; box-shadow: 0 0 5px var(--success); }
}

/* ── Floating Particles Background ────────────────────────────────────── */
.particles-container {
    position: fixed; top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none; z-index: -1; overflow: hidden;
}
.particle {
    position: absolute; width: 4px; height: 4px;
    background: rgba(14, 165, 233, 0.3); border-radius: 50%;
    animation: float-particle 15s infinite ease-in-out;
}
.particle:nth-child(2) { left: 20%; animation-delay: -2s; background: rgba(16, 185, 129, 0.3); }
.particle:nth-child(3) { left: 40%; animation-delay: -4s; background: rgba(139, 92, 246, 0.25); }
.particle:nth-child(4) { left: 60%; animation-delay: -6s; background: rgba(14, 165, 233, 0.3); }
.particle:nth-child(5) { left: 80%; animation-delay: -8s; background: rgba(16, 185, 129, 0.3); }
.particle:nth-child(6) { left: 10%; animation-delay: -10s; width: 6px; height: 6px; }
.particle:nth-child(7) { left: 70%; animation-delay: -12s; width: 5px; height: 5px; background: rgba(245, 158, 11, 0.25); }

@keyframes float-particle {
    0%, 100% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 1; transform: scale(1); }
    90% { opacity: 1; }
    100% { transform: translateY(-10vh) scale(0.5); opacity: 0; }
}

/* ── Sidebar ──────────────────────────────────────────────────────────── */
[data-testid="collapsedControl"],
button[title="Collapse sidebar"],
button[title="Expand sidebar"] {
    display: none !important;
}

[data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%) !important;
    border-right: 1.5px solid #e2e8f0 !important;
    min-width: 230px !important;
    max-width: 260px !important;
    width: 260px !important;
    position: relative !important;
    flex-shrink: 0 !important;
    box-shadow: 2px 0 12px rgba(3, 105, 161, 0.06) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
    background: #ffffff !important;
    border: 1.5px solid #e2e8f0 !important;
    color: var(--text-primary) !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 0.7rem 1.1rem !important;
    border-radius: 10px !important;
    width: 100% !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
    margin-bottom: 4px !important;
    display: flex !important;
    gap: 10px !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: var(--patient-50) !important;
    border-color: var(--patient-400) !important;
    color: var(--patient-500) !important;
    transform: translateX(3px) !important;
}

[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--patient-500), var(--patient-400)) !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 8px rgba(3, 105, 161, 0.25) !important;
}

/* ── Page header card ─────────────────────────────────────────────────── */
.page-header {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.5rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.8rem;
    box-shadow: 0 4px 16px rgba(3, 105, 161, 0.07);
    animation: fadeSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 5px; height: 100%;
    background: linear-gradient(180deg, var(--patient-500), var(--doctor-400));
}
.page-header-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-primary);
    line-height: 1.2;
}
.page-header-sub {
    font-size: 0.85rem;
    color: var(--text-secondary);
    margin-top: 4px;
    font-weight: 400;
}
.page-header-btn {
    background: linear-gradient(135deg, var(--patient-500), var(--patient-400));
    border: none;
    border-radius: 10px;
    padding: 0 18px;
    height: 40px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; color: #fff; cursor: pointer;
    box-shadow: 0 2px 10px rgba(3, 105, 161, 0.25);
    transition: all 0.25s ease;
    flex-shrink: 0; font-weight: 600; gap: 6px;
}
.page-header-btn:hover {
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(3, 105, 161, 0.35);
}

/* ── Stat Cards ───────────────────────────────────────────────────────── */
.stat-card {
    border-radius: 18px;
    padding: 1.6rem 1.6rem 1.4rem;
    position: relative;
    overflow: hidden;
    min-height: 140px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: fadeSlideUp 0.65s cubic-bezier(0.22, 1, 0.36, 1) forwards;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06), 0 1px 4px rgba(0,0,0,0.04);
}
.stat-card:nth-child(1) { animation-delay: 0.08s; }
.stat-card:nth-child(2) { animation-delay: 0.16s; }
.stat-card:nth-child(3) { animation-delay: 0.24s; }
.stat-card:nth-child(4) { animation-delay: 0.32s; }

.stat-card:hover {
    transform: translateY(-6px) scale(1.01);
    box-shadow: 0 16px 40px rgba(0, 0, 0, 0.12), 0 4px 12px rgba(0,0,0,0.06);
}
.stat-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 5px; height: 100%;
    pointer-events: none;
    border-radius: 18px 0 0 18px;
}
.stat-card::after {
    content: '';
    position: absolute; top: 0; right: 0;
    width: 90px; height: 90px;
    border-radius: 50%;
    opacity: 0.07;
    pointer-events: none;
    transform: translate(30px, -30px);
}

/* Card variant accent colors */
.stat-card-1 { border-color: #bfdbfe; }
.stat-card-1::before { background: linear-gradient(180deg, var(--patient-500), var(--patient-400)); }
.stat-card-1::after { background: var(--patient-400); }
.stat-card-1 { background: linear-gradient(145deg, #ffffff 55%, #f0f9ff 100%); }

.stat-card-2 { border-color: #a7f3d0; }
.stat-card-2::before { background: linear-gradient(180deg, var(--doctor-500), var(--doctor-400)); }
.stat-card-2::after { background: var(--doctor-400); }
.stat-card-2 { background: linear-gradient(145deg, #ffffff 55%, #ecfdf5 100%); }

.stat-card-3 { border-color: #fde68a; }
.stat-card-3::before { background: linear-gradient(180deg, var(--admin-500), var(--admin-400)); }
.stat-card-3::after { background: var(--admin-400); }
.stat-card-3 { background: linear-gradient(145deg, #ffffff 55%, #fffbeb 100%); }

.stat-card-4 { border-color: #ddd6fe; }
.stat-card-4::before { background: linear-gradient(180deg, var(--purple-500), var(--purple-400)); }
.stat-card-4::after { background: var(--purple-400); }
.stat-card-4 { background: linear-gradient(145deg, #ffffff 55%, #f5f3ff 100%); }

.stat-card-icon {
    width: 52px;
    height: 52px;
    border-radius: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    top: 1.1rem;
    right: 1.2rem;
    overflow: hidden;
    box-shadow: 0 4px 14px rgba(0,0,0,0.12);
    font-size: 0;
    line-height: 0;
}
.stat-card-icon img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    object-position: center;
    border-radius: 14px;
    display: block;
}
.stat-card-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-secondary);
    margin-bottom: 2px;
}
.stat-card-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: var(--text-primary);
    line-height: 1;
    margin-top: 0.6rem;
    letter-spacing: -0.03em;
}

/* ── Medical Banner Strip ──────────────────────────────────────────────── */
.medical-banner-wrap {
    width: 100%;
    border-radius: 18px;
    overflow: hidden;
    margin-bottom: 1.4rem;
    box-shadow: 0 8px 32px rgba(3,105,161,0.14), 0 2px 8px rgba(0,0,0,0.06);
    animation: fadeSlideIn 0.7s cubic-bezier(0.22, 1, 0.36, 1);
    border: 1.5px solid rgba(14,165,233,0.2);
    position: relative;
}
.medical-banner-wrap img {
    width: 100%;
    height: 160px;
    object-fit: cover;
    object-position: center;
    display: block;
    filter: brightness(1.02) saturate(1.1);
}
.medical-banner-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(90deg,
        rgba(3,105,161,0.22) 0%,
        rgba(5,150,105,0.08) 50%,
        rgba(139,92,246,0.12) 100%);
    border-radius: 18px;
    pointer-events: none;
}

/* ── Content card ─────────────────────────────────────────────────────── */
.content-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.6rem;
    margin-bottom: 1.4rem;
    animation: fadeSlideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    position: relative;
    overflow: hidden;
}
.content-card-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 1.2rem;
    padding-bottom: 0.7rem;
    border-bottom: 2px solid var(--border-light);
    display: flex;
    align-items: center;
    gap: 8px;
}

/* ── Prescription / Medical Record Cards ──────────────────────────────── */
.prescription-card {
    background: #ffffff;
    border: 1.5px solid #bfdbfe;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 10px rgba(3, 105, 161, 0.07);
    position: relative;
    overflow: hidden;
}
.prescription-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, var(--patient-500), var(--purple-400));
    border-radius: 14px 0 0 14px;
}
.prescription-card * {
    color: var(--text-primary) !important;
}
.prescription-header {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1rem;
    font-weight: 700;
    color: var(--patient-500) !important;
    margin-bottom: 0.6rem;
}
.prescription-body {
    font-size: 0.9rem;
    color: var(--text-secondary) !important;
    line-height: 1.7;
}
.prescription-med-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 0.6rem 0.8rem;
    background: var(--patient-50);
    border-radius: 8px;
    margin-bottom: 0.5rem;
    border-left: 3px solid var(--patient-400);
}
.prescription-med-item .med-name {
    font-weight: 600;
    color: var(--text-primary) !important;
    font-size: 0.9rem;
}
.prescription-med-item .med-dose {
    font-size: 0.82rem;
    color: var(--patient-500) !important;
    font-weight: 500;
}
.prescription-med-item .med-notes {
    font-size: 0.8rem;
    color: var(--text-secondary) !important;
}

/* ── Doctor / specialty grid cards ───────────────────────────────────── */
.doc-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.4rem;
    transition: all 0.25s ease;
    cursor: pointer;
    height: 100%;
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.doc-card:hover {
    border-color: var(--patient-400);
    background: var(--patient-50);
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(3, 105, 161, 0.14);
}
.doc-card::before {
    content: '';
    position: absolute; top: 0; left: 0;
    width: 100%; height: 3px;
    background: linear-gradient(90deg, var(--patient-500), var(--doctor-400));
    transform: scaleX(0);
    transition: transform 0.3s ease;
}
.doc-card:hover::before { transform: scaleX(1); }
.doc-card-icon { font-size: 2.2rem; margin-bottom: 0.7rem; }
.doc-card-specialty {
    font-size: 0.72rem; font-weight: 700;
    color: var(--patient-500);
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 0.4rem;
}
.doc-card-name {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem; font-weight: 700;
    color: var(--text-primary); margin-bottom: 0.5rem;
}
.doc-card-desc { font-size: 0.82rem; color: var(--text-secondary); line-height: 1.5; }

/* ── Weekly Calendar ─────────────────────────────────────────────────── */
.cal-event {
    background: var(--patient-50);
    border: 1.5px solid #bfdbfe;
    border-left: 4px solid var(--patient-500);
    border-radius: 8px;
    padding: 6px 10px;
    font-size: 0.75rem;
    color: var(--text-primary);
    margin-bottom: 5px;
    line-height: 1.4;
    transition: all 0.2s;
    animation: fadeSlideIn 0.4s ease forwards;
}
.cal-event:hover {
    transform: translateX(3px);
    box-shadow: 0 4px 12px rgba(3, 105, 161, 0.15);
    background: #dbeafe;
}

/* ── Status Badges ───────────────────────────────────────────────────── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border: 1.5px solid transparent;
}
.badge-green {
    background: var(--doctor-100);
    color: #065f46;
    border-color: var(--doctor-400);
}
.badge-blue {
    background: var(--patient-100);
    color: var(--patient-500);
    border-color: var(--patient-400);
}
.badge-yellow {
    background: var(--admin-100);
    color: #78350f;
    border-color: var(--admin-400);
}
.badge-red {
    background: #fee2e2;
    color: #7f1d1d;
    border-color: #f87171;
}
.badge-gray {
    background: #f1f5f9;
    color: #475569;
    border-color: #cbd5e1;
}
.badge-purple {
    background: var(--purple-100);
    color: #4c1d95;
    border-color: var(--purple-400);
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--bg-surface) !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 6px !important;
    gap: 4px !important;
    margin-bottom: 1.5rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-secondary) !important;
    font-weight: 600 !important;
    font-size: 0.88rem !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.1rem !important;
    transition: all 0.2s ease !important;
    border: none !important;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: var(--patient-500) !important;
    box-shadow: 0 2px 8px rgba(3, 105, 161, 0.12) !important;
    border: 1px solid #bfdbfe !important;
}
.stTabs [data-baseweb="tab"]:hover {
    background: #ffffff !important;
    color: var(--text-primary) !important;
}

/* ── Inputs ──────────────────────────────────────────────────────────── */
div[data-baseweb="input"], div[data-baseweb="textarea"] {
    background: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    transition: all 0.2s ease !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: var(--patient-500) !important;
    box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.12) !important;
    background: #ffffff !important;
}
div[data-baseweb="textarea"]:focus-within {
    border-color: var(--patient-500) !important;
    box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.12) !important;
}
input, textarea {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
}
input::placeholder, textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ── Selectbox & Dropdown Menu Styling (Fix Dark Dropdowns & Invisible Text) ── */

/* Closed Selectbox Container */
div[data-baseweb="select"],
div[data-baseweb="select"] > div,
div[data-baseweb="select"] > div > div {
    background-color: #ffffff !important;
    border-color: #cbd5e1 !important;
    color: #0f172a !important;
    border-radius: 10px !important;
}

/* Selectbox input text & value containers */
div[data-baseweb="select"] *,
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="value-container"],
div[data-baseweb="value-container"] * {
    color: #0f172a !important;
    fill: #0f172a !important;
    background-color: transparent !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
}

/* Dropdown Arrow / SVG Icon */
div[data-baseweb="select"] svg {
    fill: #0f172a !important;
    color: #0f172a !important;
}

/* Focus State for Selectbox */
div[data-baseweb="select"] > div:focus-within {
    border-color: #0369a1 !important;
    box-shadow: 0 0 0 3px rgba(3, 105, 161, 0.15) !important;
}

/* ── Streamlit Popover Dropdown Menu (Open State) ── */
ul[data-baseweb="menu"],
div[data-baseweb="popover"],
div[data-baseweb="popover"] > div,
div[data-baseweb="popover"] ul,
ul[role="listbox"],
[data-baseweb="popover"] [role="listbox"] {
    background-color: #ffffff !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 12px !important;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15) !important;
}

/* Dropdown Options (Items inside the open menu) */
li[role="option"],
div[role="option"],
[data-baseweb="popover"] li,
[data-baseweb="popover"] div,
[data-baseweb="menu"] li,
[data-baseweb="menu"] div,
ul[data-baseweb="menu"] * {
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.92rem !important;
    font-weight: 500 !important;
}

/* Selected / Hovered Dropdown Option */
li[role="option"]:hover,
div[role="option"]:hover,
li[role="option"][aria-selected="true"],
div[role="option"][aria-selected="true"],
[data-baseweb="menu"] li:hover,
[data-baseweb="menu"] [aria-selected="true"] {
    background-color: #e0f2fe !important;
    color: #0369a1 !important;
    font-weight: 600 !important;
}

/* Widget labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] * {
    color: var(--text-primary) !important;
    font-weight: 500 !important;
}

/* ── Primary button ──────────────────────────────────────────────────── */
button[kind="primary"], .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--patient-500) 0%, var(--patient-400) 100%) !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    box-shadow: 0 2px 10px rgba(3, 105, 161, 0.25) !important;
    transition: all 0.25s ease !important;
}
button[kind="primary"]:hover, .stButton > button[kind="primary"]:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(3, 105, 161, 0.4) !important;
}

/* ── Secondary button ────────────────────────────────────────────────── */
button[kind="secondary"], .stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: var(--text-primary) !important;
    border: 1.5px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}
button[kind="secondary"]:hover, .stButton > button[kind="secondary"]:hover {
    background: var(--patient-50) !important;
    border-color: var(--patient-400) !important;
    color: var(--patient-500) !important;
    transform: translateY(-1px) !important;
}

/* ── AI Chat bubbles ─────────────────────────────────────────────────── */
.chat-user-bubble {
    background: var(--patient-50);
    border: 1.5px solid #bfdbfe;
    border-radius: 18px 18px 4px 18px;
    padding: 1rem 1.3rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.6;
    max-width: 78%;
    margin-left: auto;
    box-shadow: 0 2px 8px rgba(3, 105, 161, 0.08);
}
.chat-ai-bubble {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 18px 18px 18px 4px;
    padding: 1rem 1.3rem;
    color: var(--text-primary);
    font-size: 0.95rem;
    line-height: 1.6;
    max-width: 82%;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}
@keyframes chatSlideRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes chatSlideLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ── Metrics ─────────────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-secondary) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
}
[data-testid="stMetricDelta"] {
    font-weight: 600 !important;
}

/* ── Animations ──────────────────────────────────────────────────────── */
@keyframes fadeSlideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeSlideIn {
    from { opacity: 0; transform: translateX(-15px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-10px); }
    to { opacity: 1; transform: none; }
}
@keyframes slideUp {
    from { opacity: 0; transform: translateY(30px); }
    to { opacity: 1; transform: translateY(0); }
}

.animate-on-scroll {
    opacity: 0; transform: translateY(30px);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.animate-on-scroll.visible { opacity: 1; transform: translateY(0); }

/* ── Dividers ────────────────────────────────────────────────────────── */
hr { border-color: #e2e8f0 !important; }

/* ── Expander ────────────────────────────────────────────────────────── */
details summary {
    background: var(--bg-surface) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 0.7rem 1.1rem !important;
    transition: all 0.25s ease !important;
    border: 1.5px solid #e2e8f0 !important;
    font-weight: 500 !important;
}
details summary:hover {
    background: var(--patient-50) !important;
    border-color: var(--patient-400) !important;
    color: var(--patient-500) !important;
}

/* ── Dataframe ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06) !important;
    border: 1.5px solid #e2e8f0 !important;
}

/* ── Health Vitals ───────────────────────────────────────────────────── */
.vital-card {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.2rem;
    transition: all 0.3s ease;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
.vital-card:hover {
    transform: scale(1.02);
    box-shadow: 0 6px 20px rgba(3, 105, 161, 0.12);
    border-color: var(--patient-400);
}
.vital-icon { font-size: 1.8rem; margin-bottom: 0.5rem; display: block; }
.vital-label {
    font-size: 0.72rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--text-secondary);
}
.vital-value {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.6rem; font-weight: 700;
    color: var(--text-primary); margin-top: 0.3rem;
}
.vital-unit { font-size: 0.8rem; color: var(--text-secondary); }

/* ── Notification Toast ──────────────────────────────────────────────── */
.notification-toast {
    background: var(--doctor-50);
    border: 1.5px solid var(--doctor-400);
    border-radius: 10px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.85rem;
    color: #065f46;
    font-weight: 500;
    box-shadow: 0 2px 8px rgba(5, 150, 105, 0.12);
}

/* ── Glow effects ────────────────────────────────────────────────────── */
.glow-blue   { box-shadow: 0 0 16px rgba(3, 105, 161, 0.25); }
.glow-green  { box-shadow: 0 0 16px rgba(5, 150, 105, 0.25); }
.glow-purple { box-shadow: 0 0 16px rgba(124, 58, 237, 0.25); }
.glow-amber  { box-shadow: 0 0 16px rgba(217, 119, 6, 0.25); }

/* ── Custom scrollbar ────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 7px; height: 7px; }
::-webkit-scrollbar-track { background: #f1f5f9; border-radius: 4px; }
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, var(--patient-400), var(--doctor-400));
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover { background: var(--patient-500); }

/* ── AI Chat Header ──────────────────────────────────────────────────── */
.ai-chat-header {
    background: linear-gradient(135deg, var(--purple-50), var(--patient-50));
    border: 1.5px solid var(--purple-100);
    border-radius: 16px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    display: flex; align-items: center; justify-content: space-between;
    box-shadow: 0 4px 16px rgba(124, 58, 237, 0.1);
    animation: fadeSlideIn 0.5s ease;
}
.ai-chat-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.4rem; font-weight: 700;
    color: var(--text-primary);
}
.ai-chat-badge {
    background: linear-gradient(135deg, var(--purple-500), var(--purple-400));
    border-radius: 20px; padding: 6px 16px;
    font-size: 0.78rem; font-weight: 700;
    color: #ffffff; letter-spacing: 0.05em;
    box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3);
    animation: pulseGlow 2s infinite;
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3); }
    50% { box-shadow: 0 4px 20px rgba(124, 58, 237, 0.5); }
}

/* ── Quick Action Buttons ────────────────────────────────────────────── */
.quick-action-btn {
    background: var(--bg-surface);
    border: 1.5px solid #e2e8f0;
    border-radius: 10px;
    padding: 0.6rem 1rem;
    color: var(--text-secondary);
    font-size: 0.85rem; font-weight: 500;
    transition: all 0.25s ease;
    cursor: pointer;
}
.quick-action-btn:hover {
    background: var(--patient-50);
    border-color: var(--patient-400);
    color: var(--patient-500);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(3, 105, 161, 0.12);
}

/* ── Role-specific section headers ──────────────────────────────────── */
.section-header-patient { border-left: 4px solid var(--patient-500); padding-left: 0.8rem; color: var(--text-primary); }
.section-header-doctor  { border-left: 4px solid var(--doctor-500);  padding-left: 0.8rem; color: var(--text-primary); }
.section-header-admin   { border-left: 4px solid var(--admin-500);   padding-left: 0.8rem; color: var(--text-primary); }

/* ── Info chips / pill tags ──────────────────────────────────────────── */
.chip-blue   { display:inline-flex; align-items:center; gap:4px; background:var(--patient-100); color:var(--patient-500); border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.chip-green  { display:inline-flex; align-items:center; gap:4px; background:var(--doctor-100);  color:var(--doctor-500);  border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.chip-amber  { display:inline-flex; align-items:center; gap:4px; background:var(--admin-100);   color:var(--admin-500);   border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
.chip-purple { display:inline-flex; align-items:center; gap:4px; background:var(--purple-100);  color:var(--purple-500);  border-radius:20px; padding:2px 10px; font-size:0.78rem; font-weight:600; }
</style>
"""

# ── Plotly light theme config ─────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(255,255,255,0)",
    plot_bgcolor="rgba(248, 250, 252, 0.6)",
    font=dict(family="Plus Jakarta Sans", color="#0f172a", size=11),
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0.08)"),
    yaxis=dict(gridcolor="rgba(0,0,0,0.06)", zerolinecolor="rgba(0,0,0,0.08)"),
)

def inject_css():
    # Use static asset URL as primary background to avoid high memory overhead
    css_with_bg = DASHBOARD_CSS.replace("{BG_IMAGE_URI}", "app/static/background.png")
    st.markdown(css_with_bg, unsafe_allow_html=True)

    bg_uri = _get_bg_image_b64()
    if bg_uri:
        st.markdown(f"<style>.stApp, [data-testid='stAppViewContainer'] {{ background-image: url('{bg_uri}') !important; }}</style>", unsafe_allow_html=True)

    # Add floating particles animation
    st.markdown("""
    <script>
    document.addEventListener('DOMContentLoaded', function() {
        if (!document.querySelector('.particles-container')) {
            const container = document.createElement('div');
            container.className = 'particles-container';
            for (let i = 0; i < 7; i++) {
                const particle = document.createElement('div');
                particle.className = 'particle';
                particle.style.left = Math.random() * 100 + '%';
                particle.style.animationDelay = (Math.random() * 10) + 's';
                container.appendChild(particle);
            }
            document.body.appendChild(container);
        }
    });
    </script>
    """, unsafe_allow_html=True)

    if not st.session_state.get("authenticated", False):
        st.markdown("""
        <style>
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="collapsedControl"] { display: none !important; }
        </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: none !important;
            width: 260px !important;
            min-width: 230px !important;
            max-width: 260px !important;
            position: relative !important;
            flex-shrink: 0 !important;
            pointer-events: auto !important;
        }
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] { display: none !important; }
        section[data-testid="stSidebar"] > div {
            display: flex !important;
            visibility: visible !important;
        }
        </style>
        """, unsafe_allow_html=True)

    # ── Inject floating voice chatbot (authenticated users only) ──────────────
    if st.session_state.get("authenticated", False):
        try:
            from voice_chatbot import inject_voice_chatbot
            inject_voice_chatbot()
        except Exception:
            pass  # Silently skip if voice_chatbot module not found


# ── Sidebar logo & user info block ───────────────────────────────────────────
def sidebar_header(role: str, name: str):
    role_cfg = {
        "Admin":   {"color": "#d97706", "bg": "#fffbeb", "border": "#fde68a", "icon": "🔑"},
        "Doctor":  {"color": "#059669", "bg": "#ecfdf5", "border": "#a7f3d0", "icon": "🩺"},
        "Patient": {"color": "#0369a1", "bg": "#f0f9ff", "border": "#bae6fd", "icon": "👤"},
    }
    cfg = role_cfg.get(role, role_cfg["Patient"])
    color  = cfg["color"]
    bg     = cfg["bg"]
    border = cfg["border"]
    icon   = cfg["icon"]

    logo_uri = _get_logo_b64()
    logo_img_html = f'<img src="{logo_uri}" style="width:100%;height:100%;object-fit:contain;padding:3px;border-radius:10px;background:#ffffff;" alt="PCMHS Logo" />' if logo_uri else '🏥'

    st.sidebar.markdown(f"""
    <div style="padding:1.4rem 1rem 0.9rem; border-bottom:1px solid #e2e8f0; background:#ffffff;">
        <!-- PCMHS Logo row -->
        <div style="display:flex;align-items:center;gap:0.75rem;margin-bottom:1.1rem;">
            <div style="width:44px;height:44px;border-radius:12px;
                        background:#ffffff;
                        display:flex;align-items:center;justify-content:center;
                        flex-shrink:0;overflow:hidden;
                        border:1.5px solid #e2e8f0;
                        box-shadow:0 4px 14px rgba(13,148,136,0.2);">{logo_img_html}</div>
            <div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.15rem;
                            font-weight:800;color:#0369a1;line-height:1.1;letter-spacing:0.01em;">PCMHS</div>
                <div style="font-size:0.58rem;color:#64748b;font-weight:500;
                            line-height:1.35;margin-top:2px;">Patient Care Management<br>System for Healthcare Services</div>
            </div>
        </div>
        <!-- User info chip -->
        <div style="background:{bg};
                    border:1.5px solid {border};
                    border-radius:12px;padding:0.75rem 1rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.06);">
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;">{icon} {name}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                             background:{color};box-shadow:0 0 6px {color};
                             animation:pulse-dot 2s infinite;"></span>
                <span style="font-size:0.72rem;color:{color};font-weight:700;
                             letter-spacing:0.05em;">{role.upper()}</span>
            </div>
        </div>
    </div>
    <style>
    @keyframes pulse-dot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}
    </style>
    <div style="padding:0.8rem 0.7rem 0;">
    """, unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)


# ── Page header ───────────────────────────────────────────────────────────────
def page_header(title: str, subtitle: str, btn_label: str = "PCMHS"):
    logo_uri = _get_logo_b64()
    logo_html = (
        f'<img src="{logo_uri}" style="width:28px;height:28px;object-fit:contain;border-radius:8px;background:#ffffff;padding:2px;box-shadow:0 2px 6px rgba(0,0,0,0.15);" />'
        if logo_uri
        else ""
    )
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-header-title">{title}</div>
            <div class="page-header-sub">{subtitle}</div>
        </div>
        <div class="page-header-btn" style="display:flex;align-items:center;gap:8px;padding:6px 14px;border-radius:12px;overflow:hidden;">
            {logo_html}&nbsp;{btn_label}
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Medical banner strip (replaces emoji header row) ────────────────────────
def medical_banner(role: str = "Patient"):
    """Renders the user's medical banner image as a premium strip header."""
    banner_uri = _get_medical_banner_b64()
    logo_uri = _get_logo_b64()
    if not banner_uri:
        return  # Silently skip if image not found

    role_accent = {
        "Patient": "rgba(3,105,161,0.22), rgba(14,165,233,0.10)",
        "Doctor":  "rgba(5,150,105,0.22), rgba(16,185,129,0.10)",
        "Admin":   "rgba(217,119,6,0.22), rgba(245,158,11,0.10)",
    }.get(role, "rgba(3,105,161,0.22), rgba(14,165,233,0.10)")

    role_tag = {
        "Patient": ("#0369a1", "#e0f2fe", "Patient Portal"),
        "Doctor":  ("#059669", "#d1fae5", "Doctor Portal"),
        "Admin":   ("#d97706", "#fef3c7", "Admin Console"),
    }.get(role, ("#0369a1", "#e0f2fe", "Portal"))
    tag_color, tag_bg, tag_label = role_tag

    logo_badge_html = f'<img src="{logo_uri}" style="width:24px;height:24px;object-fit:contain;background:#fff;border-radius:6px;padding:2px;" />' if logo_uri else ''

    st.markdown(f"""
    <div class="medical-banner-wrap" style="position:relative;">
        <img src="{banner_uri}" alt="Medical Care Management System" />
        <div class="medical-banner-overlay" style="background:linear-gradient(90deg,{role_accent},rgba(0,0,0,0.08) 100%);"></div>
        <div style="position:absolute;bottom:12px;left:18px;display:flex;align-items:center;gap:10px;">
            {logo_badge_html}
            <span style="background:{tag_bg};color:{tag_color};border:1.5px solid {tag_color}33;
                         padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:800;
                         letter-spacing:0.08em;text-transform:uppercase;
                         box-shadow:0 2px 8px rgba(0,0,0,0.12);backdrop-filter:blur(4px);
                         -webkit-backdrop-filter:blur(4px);">● {tag_label}</span>
            <span style="background:rgba(255,255,255,0.92);color:#0f172a;
                         padding:3px 12px;border-radius:20px;font-size:0.72rem;font-weight:700;
                         letter-spacing:0.04em;
                         box-shadow:0 2px 8px rgba(0,0,0,0.10);backdrop-filter:blur(4px);
                         -webkit-backdrop-filter:blur(4px);">Patient Care Management System for Healthcare Services</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── 4-variant gradient stat cards ────────────────────────────────────────────
CARD_VARIANTS = ["stat-card-1", "stat-card-2", "stat-card-3", "stat-card-4"]

# Stat card icon accent colors per variant
_CARD_ICON_BG = [
    "linear-gradient(135deg,#0369a1,#0ea5e9)",  # blue
    "linear-gradient(135deg,#059669,#10b981)",  # green
    "linear-gradient(135deg,#d97706,#f59e0b)",  # amber
    "linear-gradient(135deg,#7c3aed,#8b5cf6)",  # purple
]

def _get_card_img_b64(index: int) -> str:
    """Return the base64 URI of the card image to be injected via CSS."""
    try:
        img_path = os.path.join(os.path.dirname(__file__), "..", "static", f"card_img_{index}.png")
        img_path = os.path.abspath(img_path)
        if not os.path.exists(img_path): return ""
        with open(img_path, "rb") as f:
            data = base64.b64encode(f.read()).decode()
        return f"data:image/png;base64,{data}"
    except Exception:
        return ""


def stat_cards(items: list):
    """Renders premium stat cards using dynamic CSS background images.
    This bypasses Streamlit's <img> src sanitizer and perfectly positions images."""
    
    # Pre-generate dynamic CSS for the images
    css = "<style>"
    for i in range(1, 5):
        b64 = _get_card_img_b64(i)
        if b64:
            css += f".dynamic-card-img-{i} {{ background-image: url('{b64}'); }}\n"
    css += "</style>"
    st.markdown(css, unsafe_allow_html=True)
    
    cols = st.columns(len(items))
    for i, (col, (icon, label, value)) in enumerate(zip(cols, items)):
        variant = CARD_VARIANTS[i % 4]
        icon_bg = _CARD_ICON_BG[i % 4]
        img_class = f"dynamic-card-img-{i+1}"
        
        # We use a div with background-image instead of an img tag
        # The background-size: cover simulates object-fit: cover
        icon_html = f'<div class="stat-card-icon" style="background:{icon_bg};overflow:hidden;border-radius:14px;"><div class="{img_class}" style="width:100%;height:100%;background-size:cover;background-position:center;border-radius:14px;transition:transform 0.3s ease;" onmouseover="this.style.transform=\\\'scale(1.08)\\\'" onmouseout="this.style.transform=\\\'scale(1)\\\'"></div></div>'
        
        with col:
            st.markdown(f'<div class="stat-card {variant}">{icon_html}<div><div class="stat-card-label">{label}</div><div class="stat-card-value">{value}</div></div></div>', unsafe_allow_html=True)


def status_badge(status: str) -> str:
    mapping = {
        "confirmed":  ("badge-green",  "✓ Confirmed"),
        "pending":    ("badge-yellow", "⏳ Pending"),
        "cancelled":  ("badge-red",    "✕ Cancelled"),
        "completed":  ("badge-blue",   "✔ Completed"),
        "active":     ("badge-green",  "● Active"),
        "inactive":   ("badge-gray",   "○ Inactive"),
        "booked":     ("badge-blue",   "● Booked"),
    }
    cls, lbl = mapping.get((status or "").lower(), ("badge-gray", (status or "Unknown").title()))
    return f'<span class="badge {cls}">{lbl}</span>'


def sidebar_footer():
    try:
        import db
    except ImportError:
        import sys, os
        sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
        import db
    try:
        _db_type = db.current_db_type
        _db_color = "#059669" if "MySQL" in _db_type else "#d97706"
        _db_bg    = "#ecfdf5" if "MySQL" in _db_type else "#fffbeb"
        _db_label = "MySQL Connected" if "MySQL" in _db_type else "SQLite Active"
    except:
        _db_color = "#64748b"
        _db_bg    = "#f1f5f9"
        _db_label = "DB Initializing"

    st.sidebar.markdown(f"""
    <div style="margin-top:auto;padding:12px 14px;
                background:{_db_bg};
                border-radius:12px;
                border:1.5px solid rgba(0,0,0,0.08);
                margin:20px 10px 14px;
                box-shadow:0 2px 8px rgba(0,0,0,0.05);">
        <div style="font-size:0.68rem;text-transform:uppercase;color:#059669;
                    font-weight:800;letter-spacing:0.08em;
                    display:flex;align-items:center;gap:5px;">
            <span style="display:inline-block;width:6px;height:6px;background:#059669;
                         border-radius:50%;box-shadow:0 0 6px #059669;
                         animation:pulse-dot 2s infinite;"></span>
            HIPAA COMPLIANT
        </div>
        <div style="font-size:0.8rem;font-weight:700;color:#0f172a;margin-top:4px;">
            Secure PCMHS Connection
        </div>
        <div style="font-size:0.7rem;color:#64748b;margin-top:3px;line-height:1.3;">
            End-to-end encrypted logs.
        </div>
        <div style="display:flex;align-items:center;gap:5px;margin-top:8px;
                    padding-top:6px;border-top:1px solid rgba(0,0,0,0.08);">
            <span style="display:inline-block;width:6px;height:6px;
                         background:{_db_color};border-radius:50%;
                         box-shadow:0 0 5px {_db_color};
                         animation:pulse-dot 2s infinite;"></span>
            <span style="font-size:0.68rem;color:{_db_color};font-weight:700;">{_db_label}</span>
        </div>
    </div>
    <style>
    @keyframes pulse-dot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}
    </style>
    """, unsafe_allow_html=True)