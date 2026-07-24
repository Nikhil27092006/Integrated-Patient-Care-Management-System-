"""
Shared CSS theme — Enhanced Deep obsidian + neon cyan/teal medical theme.
With health animations, multi-color UI, and GSAP-like effects.
"""
import streamlit as st
import base64
import os

def _get_bg_image_b64() -> str:
    """Load the background image and return as a base64 data URI."""
    img_path = os.path.join(os.path.dirname(__file__), "..", "background",
                            "WhatsApp Image 2026-07-21 at 9.26.52 PM.jpeg")
    img_path = os.path.abspath(img_path)
    with open(img_path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return f"data:image/jpeg;base64,{data}"

DASHBOARD_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&display=swap');

/* ── Global Reset ─────────────────────────────────────────────────────── */
html, body, .stApp {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #f3f4f6 !important;
}
.stApp {
    background-image: url('{BG_IMAGE_URI}') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* Target the actual rendered container in Streamlit */
[data-testid="stAppViewContainer"] {
    background-image: url('{BG_IMAGE_URI}') !important;
    background-size: cover !important;
    background-position: center center !important;
    background-repeat: no-repeat !important;
    background-attachment: fixed !important;
}

/* Make inner containers transparent so the image shows through */
[data-testid="stHeader"],
[data-testid="stSidebar"] > div:first-child,
section.main > div {
    background: transparent !important;
}

/* Dark overlay to make content readable */
[data-testid="stAppViewContainer"]::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(3, 7, 18, 0.82) !important;
    z-index: 0;
    pointer-events: none;
}

/* Ensure content sits above the overlay */
[data-testid="stAppViewContainer"] > * {
    position: relative;
    z-index: 1;
}

/* Keep old overlay as fallback */
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
header[data-testid="stHeader"],
[data-testid="stDecoration"],
footer { visibility: hidden !important; height: 0 !important; }

/* ── Prevent Top Text Clipping ────────────────────────────────────────── */
.block-container,
[data-testid="stMainBlockContainer"],
[data-testid="stAppViewContainer"] section.main > div {
    padding-top: 2.5rem !important;
    padding-bottom: 2.5rem !important;
}

/* ── Alert / Notification Boxes — high contrast visible non-clipped text ─────────── */
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

/* Target all text elements inside alerts to ensure proper line-height & visibility */
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

/* Error box — vivid red bg, crisp white text */
[data-testid="stAlert"][data-baseweb="notification"][kind="negative"],
div[data-baseweb="notification"][kind="negative"],
div[class*="stError"],
div[class*="Alert"][class*="error"] {
    background: rgba(220, 38, 38, 0.35) !important;
    border: 1px solid rgba(239, 68, 68, 0.7) !important;
    border-left: 6px solid #ef4444 !important;
    color: #ffffff !important;
}

/* Warning box — amber bg, bright text */
[data-testid="stAlert"][data-baseweb="notification"][kind="warning"],
div[data-baseweb="notification"][kind="warning"],
div[class*="stWarning"],
div[class*="Alert"][class*="warning"] {
    background: rgba(217, 119, 6, 0.3) !important;
    border: 1px solid rgba(251, 191, 36, 0.7) !important;
    border-left: 6px solid #fbbf24 !important;
    color: #ffffff !important;
}

/* Info box — cyan bg, bright text */
[data-testid="stAlert"][data-baseweb="notification"][kind="info"],
div[data-baseweb="notification"][kind="info"],
div[class*="stInfo"],
div[class*="Alert"][class*="info"] {
    background: rgba(14, 165, 233, 0.25) !important;
    border: 1px solid rgba(56, 189, 248, 0.7) !important;
    border-left: 6px solid #38bdf8 !important;
    color: #ffffff !important;
}

/* Success box — green bg, bright text */
[data-testid="stAlert"][data-baseweb="notification"][kind="positive"],
div[data-baseweb="notification"][kind="positive"],
div[class*="stSuccess"],
div[class*="Alert"][class*="success"] {
    background: rgba(16, 185, 129, 0.25) !important;
    border: 1px solid rgba(52, 211, 153, 0.7) !important;
    border-left: 6px solid #34d399 !important;
    color: #ffffff !important;
}

/* Streamlit 1.x modern selectors for alert boxes */
[data-testid="stNotification"],
.st-emotion-cache-1wqrzgl,
.element-container [data-testid="stAlert"] {
    backdrop-filter: blur(8px) !important;
}

/* Also fix st.spinner text color */
[data-testid="stSpinner"] * {
    color: #e2e8f0 !important;
}

/* ── Streamlit Audio Input & Media Recorder Premium Styling ─────────── */
[data-testid="stAudioInput"],
div[class*="stAudioInput"] {
    background: linear-gradient(135deg, rgba(10, 20, 38, 0.95), rgba(18, 30, 58, 0.9)) !important;
    border: 1.5px solid rgba(14, 165, 233, 0.45) !important;
    border-radius: 20px !important;
    padding: 1rem 1.2rem !important;
    margin-top: 1rem !important;
    margin-bottom: 1.2rem !important;
    box-shadow: 0 12px 36px rgba(0, 0, 0, 0.55) !important;
}

[data-testid="stAudioInput"] label,
[data-testid="stAudioInput"] [data-testid="stWidgetLabel"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    margin-bottom: 0.8rem !important;
}

/* Sound Wave animation bars */
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
    background: linear-gradient(180deg, #0ea5e9, #8b5cf6);
    border-radius: 4px;
    animation: wave-bounce 1.2s ease-in-out infinite;
}
.voice-wave-container span:nth-child(2) { animation-delay: 0.15s; }
.voice-wave-container span:nth-child(3) { animation-delay: 0.3s; }
.voice-wave-container span:nth-child(4) { animation-delay: 0.45s; }
.voice-wave-container span:nth-child(5) { animation-delay: 0.6s; }

@keyframes wave-bounce {
    0%, 100% { height: 6px; opacity: 0.4; }
    50% { height: 20px; opacity: 1; filter: drop-shadow(0 0 6px #0ea5e9); }
}

/* Voice Instructions Box */
.voice-instructions {
    font-family: 'Segoe UI', system-ui, sans-serif;
    font-size: 0.85rem;
    color: #94a3b8;
    line-height: 1.6;
    margin-top: 0.8rem;
    padding: 1rem;
    background: rgba(99, 102, 241, 0.08);
    border-radius: 10px;
    border-left: 3px solid #6366f1;
}

/* Microphone visual container styling */
.mic-button-container {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    margin: 1.5rem 0 1rem 0 !important;
}

.mic-outer-ring {
    width: 80px;
    height: 80px;
    background: linear-gradient(145deg, #1e293b, #0f172a);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 2px solid #334155;
    box-shadow: 0 8px 32px rgba(0,0,0,0.5);
    transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
    animation: micGlowPulse 2.5s ease-in-out infinite;
}

.mic-outer-ring:hover {
    transform: scale(1.06);
    border-color: #6366f1;
    box-shadow: 0 12px 40px rgba(99, 102, 241, 0.4);
}

.mic-inner-circle {
    width: 50px;
    height: 50px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.5);
}

@keyframes micGlowPulse {
    0%, 100% {
        box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 0 rgba(99, 102, 241, 0.3);
    }
    50% {
        box-shadow: 0 8px 32px rgba(0,0,0,0.5), 0 0 0 14px rgba(99, 102, 241, 0);
    }
}



/* ── Floating Particles Background ────────────────────────────────────── */
.particles-container {
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: -1;
    overflow: hidden;
}
.particle {
    position: absolute;
    width: 4px; height: 4px;
    background: rgba(14,165,233,0.4);
    border-radius: 50%;
    animation: float-particle 15s infinite ease-in-out;
}
.particle:nth-child(2) { left: 20%; animation-delay: -2s; background: rgba(20,184,166,0.4); }
.particle:nth-child(3) { left: 40%; animation-delay: -4s; background: rgba(168,85,247,0.3); }
.particle:nth-child(4) { left: 60%; animation-delay: -6s; background: rgba(14,165,233,0.4); }
.particle:nth-child(5) { left: 80%; animation-delay: -8s; background: rgba(20,184,166,0.4); }
.particle:nth-child(6) { left: 10%; animation-delay: -10s; width: 6px; height: 6px; }
.particle:nth-child(7) { left: 70%; animation-delay: -12s; width: 5px; height: 5px; background: rgba(251,191,36,0.3); }

@keyframes float-particle {
    0%, 100% { transform: translateY(100vh) scale(0); opacity: 0; }
    10% { opacity: 1; transform: scale(1); }
    90% { opacity: 1; }
    100% { transform: translateY(-10vh) scale(0.5); opacity: 0; }
}

/* ── Heart Pulse Animation ─────────────────────────────────────────────── */
.heart-pulse {
    position: relative;
    display: inline-block;
}
.heart-pulse::before {
    content: '❤️';
    display: block;
    animation: heartbeat 1.2s ease-in-out infinite;
}
@keyframes heartbeat {
    0%, 100% { transform: scale(1); }
    15% { transform: scale(1.15); }
    30% { transform: scale(1); }
    45% { transform: scale(1.1); }
    60% { transform: scale(1); }
}

/* ── Animated ECG Line ─────────────────────────────────────────────────── */
.ecg-line {
    position: relative;
    height: 40px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(16,185,129,0.1) 20%,
        rgba(16,185,129,0.3) 40%,
        rgba(16,185,129,0.1) 60%,
        transparent 100%
    );
    border-radius: 4px;
    overflow: hidden;
    margin: 10px 0;
}
.ecg-line::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 200%;
    height: 100%;
    background: linear-gradient(90deg,
        transparent,
        rgba(16,185,129,0.8) 45%,
        rgba(16,185,129,0.8) 50%,
        rgba(16,185,129,0.8) 55%,
        transparent
    );
    animation: ecg-scan 2s linear infinite;
}
@keyframes ecg-scan {
    0% { left: -100%; }
    100% { left: 100%; }
}

/* ── SpO2 Ring Animation ─────────────────────────────────────────────── */
.spo2-ring {
    position: relative;
    width: 50px; height: 50px;
}
.spo2-ring::before {
    content: '';
    position: absolute;
    inset: 0;
    border: 3px solid transparent;
    border-top-color: #0ea5e9;
    border-right-color: #14b8a6;
    border-radius: 50%;
    animation: spin-ring 1.5s linear infinite;
}
.spo2-ring::after {
    content: '💨';
    position: absolute;
    top: 50%; left: 50%;
    transform: translate(-50%, -50%);
    font-size: 1.2rem;
}
@keyframes spin-ring {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ── BP Monitor Animation ─────────────────────────────────────────────── */
.bp-monitor {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 6px 12px;
    background: rgba(239,68,68,0.1);
    border-radius: 20px;
    border: 1px solid rgba(239,68,68,0.3);
}
.bp-monitor::before {
    content: '🩸';
    animation: bp-pulse 1s ease-in-out infinite;
}
@keyframes bp-pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}

/* ── Medical Cross Pulse ─────────────────────────────────────────────── */
.medical-cross {
    position: relative;
    display: inline-block;
    animation: cross-pulse 2s ease-in-out infinite;
}
@keyframes cross-pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 5px rgba(14,165,233,0.5)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 15px rgba(14,165,233,0.8)); }
}

/* ── Heart Rate Wave Animation ────────────────────────────────────────── */
.heart-wave {
    position: relative;
    height: 50px;
    background: rgba(239,68,68,0.05);
    border-radius: 8px;
    overflow: hidden;
}
.heart-wave::before {
    content: '';
    position: absolute;
    top: 50%;
    left: -100%;
    width: 300%;
    height: 60px;
    background: repeating-linear-gradient(90deg,
        transparent 0%,
        transparent 10%,
        rgba(239,68,68,0.8) 10%,
        rgba(239,68,68,0.8) 12%,
        transparent 12%,
        transparent 15%,
        rgba(239,68,68,0.6) 15%,
        rgba(239,68,68,0.9) 17%,
        rgba(239,68,68,0.8) 20%,
        transparent 20%,
        transparent 100%
    );
    animation: wave-move 3s linear infinite;
    transform: translateY(-50%);
}
@keyframes wave-move {
    0% { left: -50%; }
    100% { left: 0%; }
}

/* ── Stethoscope Animation ────────────────────────────────────────────── */
.stethoscope-icon {
    display: inline-block;
    animation: stetho-bounce 2s ease-in-out infinite;
}
@keyframes stetho-bounce {
    0%, 100% { transform: translateY(0) rotate(-5deg); }
    50% { transform: translateY(-5px) rotate(5deg); }
}

/* ── Thermometer Animation ────────────────────────────────────────────── */
.thermometer {
    position: relative;
    display: inline-flex;
    align-items: flex-end;
    gap: 4px;
}
.thermometer::before {
    content: '🌡️';
    font-size: 1.5rem;
    animation: temp-shake 2s ease-in-out infinite;
}
@keyframes temp-shake {
    0%, 100% { transform: rotate(-3deg); }
    25% { transform: rotate(3deg); }
    50% { transform: rotate(-3deg); }
    75% { transform: rotate(3deg); }
}

/* ── ECG PQRST Wave ──────────────────────────────────────────────────── */
.ecg-pqrst {
    position: relative;
    height: 60px;
    background: linear-gradient(180deg, rgba(16,185,129,0.05) 0%, rgba(3,7,18,0.8) 100%);
    border: 1px solid rgba(16,185,129,0.3);
    border-radius: 8px;
    overflow: hidden;
}
.ecg-pqrst::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(90deg,
        transparent 0%,
        rgba(16,185,129,0.3) 5%,
        rgba(16,185,129,0.6) 10%,
        rgba(16,185,129,1) 15%,
        rgba(239,68,68,1) 20%,
        rgba(239,68,68,1) 25%,
        rgba(16,185,129,0.8) 30%,
        rgba(16,185,129,0.3) 40%,
        transparent 45%,
        rgba(16,185,129,0.3) 50%,
        rgba(16,185,129,0.6) 55%,
        rgba(16,185,129,1) 60%,
        rgba(239,68,68,1) 65%,
        rgba(16,185,129,0.8) 70%,
        rgba(16,185,129,0.3) 80%,
        transparent 85%,
        transparent 100%
    );
    transform: translateY(-50%);
}
.ecg-pqrst::after {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(16,185,129,0.4), transparent);
    animation: ecg-scan 2s linear infinite;
}

/* ── Oxygen Bubble Animation ─────────────────────────────────────────── */
.oxygen-bubble {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 6px;
}
.oxygen-bubble::before {
    content: '💨';
    animation: bubble-float 2s ease-in-out infinite;
}
.oxygen-bubble::after {
    content: '';
    position: absolute;
    width: 8px;
    height: 8px;
    background: rgba(14,165,233,0.6);
    border-radius: 50%;
    animation: bubble-rise 1.5s ease-in-out infinite;
    left: 8px;
    top: -5px;
}
@keyframes bubble-rise {
    0% { transform: translateY(0); opacity: 1; }
    100% { transform: translateY(-15px); opacity: 0; }
}
@keyframes bubble-float {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
}

/* ── Defibrillator Flash ─────────────────────────────────────────────── */
.defib-flash {
    position: relative;
    display: inline-block;
    animation: defib-zap 2s ease-in-out infinite;
}
@keyframes defib-zap {
    0%, 90%, 100% { opacity: 1; filter: brightness(1); }
    92% { opacity: 0.8; filter: brightness(2); }
    94% { opacity: 1; filter: brightness(1.5); }
    96% { opacity: 0.7; filter: brightness(3); }
}

/* ── Medical Kit Shake ───────────────────────────────────────────────── */
.medical-kit {
    display: inline-block;
    animation: kit-shake 3s ease-in-out infinite;
}
@keyframes kit-shake {
    0%, 100% { transform: rotate(0deg); }
    5% { transform: rotate(-10deg); }
    10% { transform: rotate(10deg); }
    15% { transform: rotate(-10deg); }
    20% { transform: rotate(0deg); }
}

/* ── Pulse Line Animation ────────────────────────────────────────────── */
.pulse-line {
    position: relative;
    height: 40px;
    background: rgba(3,7,18,0.6);
    border-radius: 6px;
    overflow: hidden;
}
.pulse-line::before {
    content: '';
    position: absolute;
    top: 50%;
    left: 0;
    width: 100%;
    height: 2px;
    background: repeating-linear-gradient(90deg,
        transparent 0%,
        rgba(14,165,233,0.4) 5%,
        rgba(14,165,233,0.8) 10%,
        rgba(20,184,166,1) 15%,
        transparent 20%,
        transparent 30%,
        rgba(14,165,233,0.6) 35%,
        transparent 40%,
        transparent 100%
    );
    transform: translateY(-50%);
}
.pulse-line::after {
    content: '';
    position: absolute;
    top: 0;
    left: -50%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(14,165,233,0.3), transparent);
    animation: pulse-scan 2s linear infinite;
}
@keyframes pulse-scan {
    0% { left: -50%; }
    100% { left: 100%; }
}

/* ── Heart Monitor Dot ────────────────────────────────────────────────── */
.heart-monitor {
    position: relative;
    display: inline-flex;
    align-items: center;
    gap: 8px;
}
.heart-monitor::before {
    content: '';
    width: 12px;
    height: 12px;
    background: #10b981;
    border-radius: 50%;
    animation: monitor-blink 1s ease-in-out infinite;
    box-shadow: 0 0 10px #10b981;
}
@keyframes monitor-blink {
    0%, 100% { opacity: 1; box-shadow: 0 0 10px #10b981; }
    50% { opacity: 0.5; box-shadow: 0 0 5px #10b981; }
}

/* ── Pills Animation ─────────────────────────────────────────────────── */
.pills-container {
    display: inline-flex;
    gap: 4px;
}
.pills-container::before, .pills-container::after {
    content: '💊';
    font-size: 1.2rem;
    animation: pill-float 2s ease-in-out infinite;
}
.pills-container::after {
    animation-delay: 0.5s;
}
@keyframes pill-float {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-4px) rotate(10deg); }
}

/* ── Syringe Animation ───────────────────────────────────────────────── */
.syringe {
    display: inline-block;
    animation: syringe-tilt 2.5s ease-in-out infinite;
}
@keyframes syringe-tilt {
    0%, 100% { transform: rotate(-15deg); }
    50% { transform: rotate(15deg); }
}

/* ── Bandage Animation ───────────────────────────────────────────────── */
.bandage {
    display: inline-block;
    animation: bandage-wiggle 2s ease-in-out infinite;
}
@keyframes bandage-wiggle {
    0%, 100% { transform: rotate(0deg) scale(1); }
    25% { transform: rotate(-5deg) scale(1.02); }
    75% { transform: rotate(5deg) scale(1.02); }
}

/* ── First Aid Kit ───────────────────────────────────────────────────── */
.first-aid {
    display: inline-block;
    animation: aid-pulse 2s ease-in-out infinite;
}
@keyframes aid-pulse {
    0%, 100% { transform: scale(1); filter: drop-shadow(0 0 3px rgba(239,68,68,0.5)); }
    50% { transform: scale(1.05); filter: drop-shadow(0 0 8px rgba(239,68,68,0.8)); }
}

/* ── Skull/Bone Animation ────────────────────────────────────────────── */
.bone-icon {
    display: inline-block;
    animation: bone-rattle 3s ease-in-out infinite;
}
@keyframes bone-rattle {
    0%, 100% { transform: rotate(0deg); }
    25% { transform: rotate(-3deg); }
    75% { transform: rotate(3deg); }
}

/* ── DNA Helix Animation ─────────────────────────────────────────────── */
.dna-animation {
    position: relative;
    display: inline-flex;
    gap: 3px;
    height: 40px;
    align-items: center;
}
.dna-animation span {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #8b5cf6;
    animation: dna-wave 1.5s ease-in-out infinite;
}
.dna-animation span:nth-child(odd) { animation-delay: 0.2s; }
.dna-animation span:nth-child(even) { animation-delay: 0s; background: #0ea5e9; }
@keyframes dna-wave {
    0%, 100% { transform: translateY(0); opacity: 0.5; }
    50% { transform: translateY(-8px); opacity: 1; }
}

/* ── IV Drip Animation ───────────────────────────────────────────────── */
.iv-drip {
    display: inline-block;
    animation: iv-swing 3s ease-in-out infinite;
}
@keyframes iv-swing {
    0%, 100% { transform: rotate(-3deg); }
    50% { transform: rotate(3deg); }
}

/* ── Wheelchair Animation ─────────────────────────────────────────────── */
.wheelchair {
    display: inline-block;
    animation: wheel-spin 4s linear infinite;
}
@keyframes wheel-spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

/* ── Hospital Icon Glow ──────────────────────────────────────────────── */
.hospital-glow {
    display: inline-block;
    animation: hospital-pulse 2s ease-in-out infinite;
}
@keyframes hospital-pulse {
    0%, 100% { filter: drop-shadow(0 0 5px rgba(14,165,233,0.5)); }
    50% { filter: drop-shadow(0 0 15px rgba(14,165,233,0.9)); }
}
    animation: bp-pulse 1s ease-in-out infinite;
}
@keyframes bp-pulse {
    0%, 100% { opacity: 0.6; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.1); }
}

/* ── Permanent Sidebar (Disable collapsing) ──────────────────────────── */
[data-testid="collapsedControl"],
button[title="Collapse sidebar"],
button[title="Expand sidebar"] {
    display: none !important;
}

/* ── Sidebar — deep navy matching login page ─────────────────────────── */
[data-testid="stSidebar"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    transform: none !important;
    background: linear-gradient(180deg,
        #060d1f 0%,
        #0a1628 40%,
        #071322 75%,
        #040e1a 100%) !important;
    border-right: 1px solid rgba(14,165,233,0.2) !important;
    min-width: 230px !important;
    max-width: 255px !important;
    width: 255px !important;
    position: relative !important;
    flex-shrink: 0 !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* Sidebar nav buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(14, 165, 233, 0.05) !important;
    border: 1px solid rgba(14, 165, 233, 0.15) !important;
    color: #8b9ab5 !important;
    text-align: left !important;
    justify-content: flex-start !important;
    align-items: center !important;
    padding: 0.65rem 1.1rem !important;
    border-radius: 12px !important;
    width: 100% !important;
    font-size: 0.87rem !important;
    font-weight: 500 !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    margin-bottom: 6px !important;
    display: flex !important;
    gap: 8px !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stSidebar"] .stButton > button::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: left 0.5s;
}
[data-testid="stSidebar"] .stButton > button:hover::before {
    left: 100%;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(14, 165, 233, 0.12) !important;
    border-color: rgba(14, 165, 233, 0.4) !important;
    color: #ffffff !important;
    transform: translateX(4px) !important;
    box-shadow: 0 0 20px rgba(14,165,233,0.25) !important;
}

/* Active sidebar button */
[data-testid="stSidebar"] .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, rgba(14,165,233,0.3), rgba(20,184,166,0.25)) !important;
    color: #ffffff !important;
    border: 1px solid rgba(14,165,233,0.6) !important;
    font-weight: 600 !important;
    box-shadow: 0 0 24px rgba(14,165,233,0.3) !important;
}
[data-testid="stSidebar"] .stButton > button[kind="primary"]::after {
    content: '';
    position: absolute;
    right: 0; top: 50%;
    transform: translateY(-50%);
    width: 3px; height: 60%;
    background: linear-gradient(180deg, #0ea5e9, #14b8a6);
    border-radius: 2px;
}

/* ── Page header card ─────────────────────────────────────────────────── */
.page-header {
    background: linear-gradient(135deg, rgba(10,22,40,0.9), rgba(15,30,60,0.85));
    border: 1px solid rgba(14,165,233,0.2);
    border-radius: 20px;
    padding: 1.6rem 2rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 1.8rem;
    backdrop-filter: blur(16px);
    box-shadow:
        0 8px 32px rgba(0,0,0,0.4),
        inset 0 1px 0 rgba(255,255,255,0.05);
    animation: fadeSlideIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    position: relative;
    overflow: hidden;
}
.page-header::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(circle, rgba(14,165,233,0.1) 0%, transparent 60%);
    animation: shimmer 3s infinite;
}
@keyframes shimmer {
    0%, 100% { transform: translate(-30%, -30%); }
    50% { transform: translate(30%, 30%); }
}
.page-header-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1.2;
    position: relative;
    z-index: 1;
}
.page-header-sub {
    font-size: 0.85rem;
    color: #0ea5e9;
    margin-top: 4px;
    font-weight: 400;
    position: relative;
    z-index: 1;
}
.page-header-btn {
    background: linear-gradient(135deg, #0ea5e9, #14b8a6);
    border: none;
    border-radius: 12px;
    padding: 0 18px;
    height: 40px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.78rem; color: #fff; cursor: pointer;
    box-shadow: 0 6px 20px rgba(14,165,233,0.45);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    flex-shrink: 0;
    font-weight: 700;
    letter-spacing: 0.05em;
    gap: 6px;
    position: relative;
    z-index: 1;
}
.page-header-btn:hover {
    transform: translateY(-2px) scale(1.02);
    box-shadow: 0 10px 30px rgba(14,165,233,0.5);
}

/* ── Gradient Stat Cards ─────────────────────────────────────────────── */
.stat-card {
    border-radius: 20px;
    padding: 1.5rem 1.6rem;
    position: relative;
    overflow: hidden;
    min-height: 120px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    animation: fadeSlideUp 0.6s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.stat-card:nth-child(1) { animation-delay: 0.1s; }
.stat-card:nth-child(2) { animation-delay: 0.2s; }
.stat-card:nth-child(3) { animation-delay: 0.3s; }
.stat-card:nth-child(4) { animation-delay: 0.4s; }

.stat-card:hover {
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, transparent 50%);
    pointer-events: none;
}
.stat-card-1 {
    background: linear-gradient(135deg, #0369a1, #0ea5e9);
    box-shadow: 0 8px 24px rgba(14,165,233,0.3);
}
.stat-card-2 {
    background: linear-gradient(135deg, #0f766e, #14b8a6);
    box-shadow: 0 8px 24px rgba(20,184,166,0.3);
}
.stat-card-3 {
    background: linear-gradient(135deg, #581c87, #8b5cf6);
    box-shadow: 0 8px 24px rgba(139,92,246,0.3);
}
.stat-card-4 {
    background: linear-gradient(135deg, #7c2d12, #f97316);
    box-shadow: 0 8px 24px rgba(249,115,22,0.3);
}
.stat-card-icon {
    font-size: 1.6rem;
    opacity: 0.9;
    position: absolute;
    top: 1.2rem; right: 1.2rem;
    animation: float-icon 3s ease-in-out infinite;
}
@keyframes float-icon {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-5px); }
}
.stat-card-label {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: rgba(255,255,255,0.8);
}
.stat-card-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 2.4rem;
    font-weight: 700;
    color: #ffffff;
    line-height: 1;
    margin-top: 0.6rem;
    position: relative;
    z-index: 1;
}

/* ── Dark glass content card ──────────────────────────────────────────── */
.content-card {
    background: linear-gradient(135deg, rgba(10,22,40,0.75), rgba(15,30,60,0.65));
    border: 1px solid rgba(14,165,233,0.15);
    border-radius: 18px;
    padding: 1.6rem;
    backdrop-filter: blur(14px);
    margin-bottom: 1.4rem;
    animation: fadeSlideUp 0.5s cubic-bezier(0.4, 0, 0.2, 1);
    box-shadow: 0 4px 24px rgba(0,0,0,0.3);
    position: relative;
    overflow: hidden;
}
.content-card::after {
    content: '';
    position: absolute;
    top: 0; right: 0;
    width: 100px; height: 100px;
    background: radial-gradient(circle, rgba(14,165,233,0.1) 0%, transparent 70%);
}
.content-card-title {
    font-size: 1rem;
    font-weight: 700;
    color: #e2e8f0;
    margin-bottom: 1.2rem;
    border-bottom: 2px solid;
    border-image: linear-gradient(90deg, #0ea5e9, #14b8a6, #8b5cf6) 1;
    padding-bottom: 0.6rem;
    display: inline-block;
}

/* ── Doctor / specialty grid cards ───────────────────────────────────── */
.doc-card {
    background: linear-gradient(135deg, rgba(10,22,40,0.75), rgba(15,30,60,0.65));
    border: 1px solid rgba(14,165,233,0.15);
    border-radius: 16px;
    padding: 1.4rem;
    transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
    cursor: pointer;
    height: 100%;
    position: relative;
    overflow: hidden;
}
.doc-card::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(14,165,233,0.1), transparent);
    transition: left 0.6s;
}
.doc-card:hover::before {
    left: 100%;
}
.doc-card:hover {
    border-color: rgba(14,165,233,0.5);
    background: linear-gradient(135deg, rgba(14,165,233,0.1), rgba(20,184,166,0.08));
    transform: translateY(-4px);
    box-shadow: 0 12px 32px rgba(14,165,233,0.2);
}
.doc-card-icon {
    font-size: 2.2rem;
    margin-bottom: 0.7rem;
    animation: icon-bounce 2s ease-in-out infinite;
}
@keyframes icon-bounce {
    0%, 100% { transform: translateY(0) scale(1); }
    50% { transform: translateY(-3px) scale(1.05); }
}
.doc-card-specialty {
    font-size: 0.74rem; font-weight: 700;
    background: linear-gradient(90deg, #0ea5e9, #14b8a6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 0.4rem;
}
.doc-card-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: #fff;
    margin-bottom: 0.5rem;
    font-family: 'Space Grotesk', sans-serif;
}
.doc-card-desc {
    font-size: 0.82rem;
    color: #9ca3af;
    line-height: 1.5;
}

/* ── Weekly Calendar ─────────────────────────────────────────────────── */
.cal-event {
    background: linear-gradient(135deg, rgba(14,165,233,0.3), rgba(20,184,166,0.25));
    border-left: 4px solid #0ea5e9;
    border-radius: 8px;
    padding: 6px 8px;
    font-size: 0.72rem;
    color: #bae6fd;
    margin-bottom: 5px;
    line-height: 1.4;
    transition: all 0.2s;
    animation: fadeSlideIn 0.4s ease forwards;
}
.cal-event:hover {
    transform: translateX(3px);
    box-shadow: 0 4px 12px rgba(14,165,233,0.2);
}

/* ── Status Badges ───────────────────────────────────────────────────── */
.badge {
    display:inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    position: relative;
    overflow: hidden;
}
.badge::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    right: 0; bottom: 0;
    background: linear-gradient(135deg, rgba(255,255,255,0.15) 0%, transparent 50%);
}
.badge-green  {
    background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(16,185,129,0.15));
    color: #10b981;
    border: 1px solid rgba(16,185,129,0.4);
    box-shadow: 0 2px 8px rgba(16,185,129,0.2);
}
.badge-blue   {
    background: linear-gradient(135deg, rgba(14,165,233,0.25), rgba(14,165,233,0.15));
    color: #0ea5e9;
    border: 1px solid rgba(14,165,233,0.4);
    box-shadow: 0 2px 8px rgba(14,165,233,0.2);
}
.badge-yellow {
    background: linear-gradient(135deg, rgba(245,158,11,0.25), rgba(245,158,11,0.15));
    color: #f59e0b;
    border: 1px solid rgba(245,158,11,0.4);
    box-shadow: 0 2px 8px rgba(245,158,11,0.2);
}
.badge-red    {
    background: linear-gradient(135deg, rgba(239,68,68,0.25), rgba(239,68,68,0.15));
    color: #ef4444;
    border: 1px solid rgba(239,68,68,0.4);
    box-shadow: 0 2px 8px rgba(239,68,68,0.2);
}
.badge-gray   {
    background: linear-gradient(135deg, rgba(107,114,128,0.25), rgba(107,114,128,0.15));
    color: #9ca3af;
    border: 1px solid rgba(107,114,128,0.4);
}

/* ── Tabs ────────────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid rgba(14,165,233,0.15) !important;
    gap: 0.6rem;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #6b7280 !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    border-bottom: 2px solid transparent !important;
    padding: 0.6rem 1.2rem !important;
    transition: all 0.3s ease !important;
    position: relative;
}
.stTabs [aria-selected="true"] {
    color: #0ea5e9 !important;
    border-bottom: 2px solid #0ea5e9 !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: #14b8a6 !important;
    background: rgba(20,184,166,0.1) !important;
}

/* ── Inputs — dark theme ─────────────────────────────────────────────── */
div[data-baseweb="input"], div[data-baseweb="textarea"] {
    background: rgba(3,7,18,0.7) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}
div[data-baseweb="input"]:focus-within {
    border-color: #14b8a6 !important;
    box-shadow: 0 0 0 3px rgba(20,184,166,0.25) !important;
}
input, textarea {
    color: #f3f4f6 !important;
}
div[data-baseweb="select"] > div {
    background: rgba(3,7,18,0.7) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 12px !important;
    color: #f3f4f6 !important;
    transition: all 0.3s ease !important;
}
[data-baseweb="select"] div { color: #f3f4f6 !important; }

/* ── Primary button — cyan/teal theme ───────────────────────────────── */
button[kind="primary"], .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #0ea5e9, #14b8a6) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(14,165,233,0.35) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}
button[kind="primary"]::before {
    content: '';
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: left 0.5s;
}
button[kind="primary"]:hover::before {
    left: 100%;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #14b8a6, #0ea5e9) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(20,184,166,0.45) !important;
}

/* ── Secondary button — purple/violet theme ─────────────────────────── */
button[kind="secondary"], .stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, #8b5cf6, #a855f7) !important;
    color: #ffffff !important;
    border: 1px solid rgba(168,85,247,0.5) !important;
    border-radius: 12px !important;
    font-weight: 700 !important;
    box-shadow: 0 6px 20px rgba(139,92,246,0.4) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative;
    overflow: hidden;
}
button[kind="secondary"]:hover {
    background: linear-gradient(135deg, #a855f7, #8b5cf6) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(168,85,247,0.55) !important;
}


/* ── Metrics ─────────────────────────────────────────────────────────── */
[data-testid="stMetricValue"] {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 2rem !important;
    color: #ffffff !important;
    background: linear-gradient(135deg, #ffffff, #e2e8f0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
[data-testid="stMetricLabel"] {
    color: #9ca3af !important;
    font-size: 0.82rem !important;
    font-weight: 600 !important;
}

/* ── Animations ──────────────────────────────────────────────────────── */
@keyframes fadeSlideUp {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
@keyframes fadeSlideIn {
    from {
        opacity: 0;
        transform: translateX(-15px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
@keyframes fadeDown {
    from{opacity:0;transform:translateY(-10px)} to{opacity:1;transform:none}
}

/* ── Scroll-trigger style animation class ────────────────────────────── */
.animate-on-scroll {
    opacity: 0;
    transform: translateY(30px);
    transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
}
.animate-on-scroll.visible {
    opacity: 1;
    transform: translateY(0);
}

/* ── Dividers ────────────────────────────────────────────────────────── */
hr { border-color: rgba(255,255,255,0.07) !important; }

/* ── Expander ────────────────────────────────────────────────────────── */
details summary {
    background: linear-gradient(135deg, rgba(10,22,40,0.7), rgba(15,30,60,0.6)) !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    padding: 0.7rem 1.1rem !important;
    transition: all 0.3s ease !important;
    border: 1px solid rgba(14,165,233,0.1) !important;
}
details summary:hover {
    background: linear-gradient(135deg, rgba(14,165,233,0.1), rgba(20,184,166,0.08)) !important;
    border-color: rgba(14,165,233,0.25) !important;
}

/* ── Dataframe ───────────────────────────────────────────────────────── */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2) !important;
}

/* ── AI Chat bubbles ─────────────────────────────────────────────────── */
.chat-user-bubble {
    background: linear-gradient(135deg, rgba(14,165,233,0.35), rgba(20,184,166,0.25));
    border: 1px solid rgba(14,165,233,0.4);
    border-radius: 18px 18px 6px 18px;
    padding: 1rem 1.3rem;
    color: #f3f4f6;
    font-size: 0.92rem;
    line-height: 1.6;
    max-width: 78%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(14,165,233,0.2);
    animation: chatSlideRight 0.4s ease forwards;
}
.chat-ai-bubble {
    background: linear-gradient(135deg, rgba(10,22,40,0.8), rgba(15,30,60,0.7));
    border: 1px solid rgba(139,92,246,0.2);
    border-radius: 18px 18px 18px 6px;
    padding: 1rem 1.3rem;
    color: #e2e8f0;
    font-size: 0.92rem;
    line-height: 1.6;
    max-width: 82%;
    box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    animation: chatSlideLeft 0.4s ease forwards;
}

@keyframes chatSlideRight {
    from { opacity: 0; transform: translateX(20px); }
    to { opacity: 1; transform: translateX(0); }
}
@keyframes chatSlideLeft {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ── Health Vitals Display ──────────────────────────────────────────── */
.vital-card {
    background: linear-gradient(135deg, rgba(10,22,40,0.8), rgba(15,30,60,0.7));
    border-radius: 14px;
    padding: 1.2rem;
    border: 1px solid rgba(14,165,233,0.15);
    transition: all 0.3s ease;
    text-align: center;
}
.vital-card:hover {
    border-color: rgba(14,165,233,0.4);
    transform: scale(1.02);
    box-shadow: 0 8px 24px rgba(14,165,233,0.15);
}
.vital-icon {
    font-size: 1.8rem;
    margin-bottom: 0.5rem;
    display: block;
}
.vital-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9ca3af;
}
.vital-value {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #fff;
    margin-top: 0.3rem;
}
.vital-unit {
    font-size: 0.8rem;
    color: #6b7280;
}

/* ── Notification Toast ─────────────────────────────────────────────── */
.notification-toast {
    background: linear-gradient(135deg, rgba(20,184,166,0.15), rgba(14,165,233,0.1));
    border: 1px solid rgba(20,184,166,0.35);
    border-radius: 12px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.8rem;
    font-size: 0.82rem;
    color: #14b8a6;
    font-weight: 600;
    animation: notificationSlide 0.5s ease forwards;
    box-shadow: 0 4px 16px rgba(20,184,166,0.2);
}
@keyframes notificationSlide {
    from { opacity: 0; transform: translateX(-20px); }
    to { opacity: 1; transform: translateX(0); }
}

/* ── Glow effects ───────────────────────────────────────────────────── */
.glow-cyan {
    box-shadow: 0 0 20px rgba(14,165,233,0.3);
}
.glow-teal {
    box-shadow: 0 0 20px rgba(20,184,166,0.3);
}
.glow-purple {
    box-shadow: 0 0 20px rgba(139,92,246,0.3);
}

/* ── Custom scrollbar ───────────────────────────────────────────────── */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(3,7,18,0.5);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb {
    background: linear-gradient(180deg, #0ea5e9, #14b8a6);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(180deg, #14b8a6, #0ea5e9);
}

/* ── Loading Spinner ───────────────────────────────────────────────── */
.custom-spinner {
    width: 40px; height: 40px;
    border: 3px solid rgba(14,165,233,0.2);
    border-top-color: #0ea5e9;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    to { transform: rotate(360deg); }
}

/* ── AI Chat Header ─────────────────────────────────────────────────── */
.ai-chat-header {
    background: linear-gradient(135deg, rgba(10,22,40,0.9), rgba(88,28,135,0.15));
    border: 1px solid rgba(139,92,246,0.25);
    border-radius: 18px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1.4rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    backdrop-filter: blur(14px);
    box-shadow: 0 8px 32px rgba(0,0,0,0.3);
    animation: fadeSlideIn 0.5s ease;
}
.ai-chat-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff, #0ea5e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.ai-chat-badge {
    background: linear-gradient(135deg, #8b5cf6, #a855f7);
    border-radius: 12px;
    padding: 8px 16px;
    font-size: 0.8rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: 0.05em;
    box-shadow: 0 4px 16px rgba(139,92,246,0.4);
    animation: pulseGlow 2s infinite;
}
@keyframes pulseGlow {
    0%, 100% { box-shadow: 0 4px 16px rgba(139,92,246,0.4); }
    50% { box-shadow: 0 4px 24px rgba(139,92,246,0.6); }
}

/* ── Quick Action Buttons ────────────────────────────────────────────── */
.quick-action-btn {
    background: linear-gradient(135deg, rgba(14,165,233,0.15), rgba(20,184,166,0.1));
    border: 1px solid rgba(14,165,233,0.25);
    border-radius: 12px;
    padding: 0.6rem 1rem;
    color: #e2e8f0;
    font-size: 0.85rem;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
}
.quick-action-btn:hover {
    background: linear-gradient(135deg, rgba(14,165,233,0.25), rgba(20,184,166,0.2));
    border-color: rgba(14,165,233,0.5);
    transform: translateY(-2px);
    box-shadow: 0 6px 20px rgba(14,165,233,0.25);
}
</style>
"""

# ── Plotly dark theme config ─────────────────────────────────────────────────
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(10,22,40,0.4)",
    font=dict(family="Plus Jakarta Sans", color="#9ca3af", size=11),
    margin=dict(l=20, r=20, t=30, b=20),
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", zerolinecolor="rgba(255,255,255,0.05)"),
)

def inject_css():
    # Version stamp to force CSS refresh
    st.markdown("<!-- IPCMS v2.0 Enhanced -->")
    # Embed background image as base64 for reliable rendering across all pages
    bg_uri = _get_bg_image_b64()
    css_with_bg = DASHBOARD_CSS.replace("url('{BG_IMAGE_URI}')", f"url('{bg_uri}')")
    st.markdown(css_with_bg, unsafe_allow_html=True)

    # Add particles animation script
    st.markdown("""
    <script>
    // Add floating particles on load
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
        # Hide sidebar on login page only
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: none !important;
        }
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    else:
        # FORCE sidebar permanently visible after login for ALL user types
        st.markdown("""
        <style>
        [data-testid="stSidebar"] {
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
            transform: none !important;
            width: 255px !important;
            min-width: 230px !important;
            max-width: 255px !important;
            position: relative !important;
            flex-shrink: 0 !important;
            pointer-events: auto !important;
        }
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            display: none !important;
        }
        section[data-testid="stSidebar"] > div {
            display: flex !important;
            visibility: visible !important;
        }
        </style>
        """, unsafe_allow_html=True)

# ── Sidebar logo & user info block ───────────────────────────────────────────
def sidebar_header(role: str, name: str):
    role_colors = {"Admin": "#f59e0b", "Doctor": "#0ea5e9", "Patient": "#14b8a6"}
    color = role_colors.get(role, "#0ea5e9")

    # Animated gradient for logo
    st.sidebar.markdown(f"""
    <div style="padding:1.4rem 1rem 0.9rem; border-bottom:1px solid rgba(14,165,233,0.15);">
        <!-- IPCMS Logo row -->
        <div style="display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:1.1rem;">
            <div style="width:40px;height:40px;border-radius:10px;
                        background:linear-gradient(135deg,#0ea5e9,#14b8a6,#8b5cf6);
                        background-size: 200% 200%;
                        animation: gradient-shift 3s ease infinite;
                        display:flex;align-items:center;justify-content:center;
                        font-size:1.2rem;flex-shrink:0;
                        box-shadow:0 4px 16px rgba(14,165,233,0.45);">+</div>
            <div>
                <div style="font-family:'Space Grotesk',sans-serif;font-size:1.1rem;
                            font-weight:800;color:#ffffff;line-height:1.1;letter-spacing:0.01em;">IPCMS</div>
                <div style="font-size:0.58rem;color:rgba(255,255,255,0.5);font-weight:400;
                            line-height:1.35;margin-top:2px;">Integrated Patient Care<br>Management System</div>
            </div>
        </div>
        <!-- User info chip -->
        <div style="background:linear-gradient(135deg, rgba(14,165,233,0.1), rgba(20,184,166,0.08));
                    border:1px solid rgba(14,165,233,0.25);
                    border-radius:14px;padding:0.8rem 1rem;
                    box-shadow: 0 4px 12px rgba(14,165,233,0.15);">
            <div style="font-size:0.95rem;font-weight:700;color:#ffffff;">{name}</div>
            <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
                <span style="display:inline-block;width:7px;height:7px;border-radius:50%;
                             background:{color};box-shadow:0 0 8px {color};
                             animation: pulse-dot 2s infinite;"></span>
                <span style="font-size:0.72rem;color:{color};font-weight:600;
                             letter-spacing:0.05em;">{role}</span>
            </div>
        </div>
    </div>
    <style>
    @keyframes gradient-shift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    @keyframes pulse-dot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.2); opacity: 0.7; }}
    }}
    </style>
    <div style="padding:0.8rem 0.7rem 0;">
    """, unsafe_allow_html=True)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
def page_header(title: str, subtitle: str, btn_label: str = "IPCMS"):
    st.markdown(f"""
    <div class="page-header">
        <div>
            <div class="page-header-title">{title}</div>
            <div class="page-header-sub">{subtitle}</div>
        </div>
        <div class="page-header-btn">
            + &nbsp;{btn_label}
        </div>
    </div>
    """, unsafe_allow_html=True)

# ── 4-variant gradient stat cards ────────────────────────────────────────────
CARD_VARIANTS = ["stat-card-1", "stat-card-2", "stat-card-3", "stat-card-4"]

def stat_cards(items: list):
    """items: list of (icon, label, value) tuples — up to 4"""
    cols = st.columns(len(items))
    for i, (col, (icon, label, value)) in enumerate(zip(cols, items)):
        variant = CARD_VARIANTS[i % 4]
        with col:
            st.markdown(f"""
            <div class="stat-card {variant}">
                <span class="stat-card-icon">{icon}</span>
                <div class="stat-card-label">{label}</div>
                <div class="stat-card-value">{value}</div>
            </div>
            """, unsafe_allow_html=True)

def status_badge(status: str) -> str:
    mapping = {
        "confirmed":  ("badge-green",  "Confirmed"),
        "pending":    ("badge-yellow", "Pending"),
        "cancelled":  ("badge-red",    "Cancelled"),
        "completed":  ("badge-blue",   "Completed"),
        "active":     ("badge-green",  "Active"),
        "inactive":   ("badge-gray",   "Inactive"),
        "booked":     ("badge-blue",   "Booked"),
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
        _db_color = "#14b8a6" if "MySQL" in _db_type else "#f59e0b"
        _db_label = f"MySQL Connected" if "MySQL" in _db_type else "SQLite Active"
    except:
        _db_color = "#9ca3af"
        _db_label = "DB Initializing"

    st.sidebar.markdown(f"""
    <div style="margin-top: auto; padding: 12px 14px; background: linear-gradient(135deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.03)); border-radius: 14px; border: 1px solid rgba(14, 165, 233, 0.18); margin: 20px 14px 14px; box-shadow: 0 4px 16px rgba(0,0,0,0.2);">
        <div style="font-size: 0.7rem; text-transform: uppercase; color: #14b8a6; font-weight: 800; letter-spacing: 0.08em; display: flex; align-items: center; gap: 5px;">
            <span style="display:inline-block; width:6px; height:6px; background:#14b8a6; border-radius:50%; box-shadow: 0 0 6px #14b8a6; animation: pulse-dot 2s infinite;"></span>
            HIPAA COMPLIANT
        </div>
        <div style="font-size: 0.8rem; font-weight: 700; color: #ffffff; margin-top: 4px;">
            Secure IPCMS Connection
        </div>
        <div style="font-size: 0.7rem; color: #8b9ab5; margin-top: 3px; line-height: 1.3;">
            End-to-end encrypted logs.
        </div>
        <div style="display: flex; align-items: center; gap: 5px; margin-top: 8px; padding-top: 6px; border-top: 1px solid rgba(255,255,255,0.08);">
            <span style="display:inline-block; width:6px; height:6px; background:{_db_color}; border-radius:50%; box-shadow: 0 0 5px {_db_color}; animation: pulse-dot 2s infinite;"></span>
            <span style="font-size: 0.68rem; color: {_db_color}; font-weight: 700;">{_db_label}</span>
        </div>
    </div>
    <style>
    @keyframes pulse-dot {{
        0%, 100% {{ transform: scale(1); opacity: 1; }}
        50% {{ transform: scale(1.3); opacity: 0.6; }}
    }}
    </style>
    """, unsafe_allow_html=True)