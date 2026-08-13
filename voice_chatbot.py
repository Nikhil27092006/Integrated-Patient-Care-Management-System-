"""
IPCMS Voice Chatbot — Floating Widget
──────────────────────────────────────────────────────────────────────────────
A fully voice-enabled floating AI assistant powered by Google Gemini.
- Floating button fixed to bottom-right on every page
- Click to open/close a glassmorphism chat panel
- Mic button → Web Speech Recognition for voice input
- Text input as keyboard fallback
- Gemini API generates healthcare-aware responses
- All responses spoken aloud via Web SpeechSynthesis
- Falls back to Groq API if Gemini key not configured
──────────────────────────────────────────────────────────────────────────────
"""

import os
import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv

load_dotenv(os.path.abspath(os.path.join(os.path.dirname(__file__), ".env")))


def _build_chatbot_html(gemini_api_key: str, groq_api_key: str) -> str:
    """Build the complete self-contained HTML/CSS/JS for the floating voice chatbot."""
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', 'Segoe UI', sans-serif; overflow: hidden; background: transparent; }}

  /* ── Floating toggle button ─────────────────────────── */
  #ipcms-fab {{
    position: fixed;
    bottom: 28px;
    right: 28px;
    width: 62px;
    height: 62px;
    border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #14b8a6 100%);
    border: none;
    cursor: pointer;
    box-shadow: 0 6px 28px rgba(14,165,233,0.55), 0 2px 8px rgba(0,0,0,0.18);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2147483647;
    transition: transform 0.3s cubic-bezier(0.34,1.56,0.64,1),
                box-shadow 0.3s ease;
    animation: fabPulse 3s ease-in-out infinite;
  }}
  #ipcms-fab:hover {{
    transform: scale(1.12);
    box-shadow: 0 10px 40px rgba(14,165,233,0.65), 0 4px 16px rgba(0,0,0,0.22);
  }}
  #ipcms-fab:active {{ transform: scale(0.96); }}

  @keyframes fabPulse {{
    0%, 100% {{ box-shadow: 0 6px 28px rgba(14,165,233,0.55), 0 0 0 0 rgba(14,165,233,0.35); }}
    50% {{ box-shadow: 0 6px 28px rgba(14,165,233,0.55), 0 0 0 12px rgba(14,165,233,0); }}
  }}
  #ipcms-fab svg {{ width: 28px; height: 28px; fill: white; transition: transform 0.3s ease; }}

  /* ── Chat Panel ─────────────────────────────────────── */
  #ipcms-panel {{
    position: fixed;
    bottom: 104px;
    right: 28px;
    width: 380px;
    height: 560px;
    border-radius: 24px;
    background: linear-gradient(145deg, rgba(255,255,255,0.98), rgba(248,250,252,0.98));
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    border: 1.5px solid rgba(14,165,233,0.2);
    box-shadow: 0 24px 80px rgba(0,0,0,0.18), 0 8px 32px rgba(14,165,233,0.12);
    z-index: 2147483646;
    display: flex;
    flex-direction: column;
    overflow: hidden;
    transform: scale(0.85) translateY(30px);
    opacity: 0;
    pointer-events: none;
    transition: all 0.35s cubic-bezier(0.34,1.56,0.64,1);
  }}
  #ipcms-panel.open {{
    transform: scale(1) translateY(0);
    opacity: 1;
    pointer-events: all;
  }}

  /* ── Panel Header ───────────────────────────────────── */
  #ipcms-header {{
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 55%, #14b8a6 100%);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }}
  .hdr-avatar {{
    width: 42px; height: 42px;
    background: rgba(255,255,255,0.22);
    border: 2px solid rgba(255,255,255,0.5);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px; flex-shrink: 0;
  }}
  .hdr-info {{ flex: 1; }}
  .hdr-name {{ color: #fff; font-size: 15px; font-weight: 700; letter-spacing: -0.2px; }}
  .hdr-status {{
    display: flex; align-items: center; gap: 5px;
    color: rgba(255,255,255,0.85); font-size: 11.5px; margin-top: 2px;
  }}
  .status-dot {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #4ade80;
    box-shadow: 0 0 6px #4ade80;
    animation: blink 2s infinite;
  }}
  @keyframes blink {{
    0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }}
  }}
  .hdr-close {{
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    color: white; border-radius: 50%;
    width: 30px; height: 30px; cursor: pointer;
    font-size: 16px; display: flex; align-items: center; justify-content: center;
    transition: background 0.2s;
  }}
  .hdr-close:hover {{ background: rgba(255,255,255,0.3); }}

  /* ── Mode buttons ───────────────────────────────────── */
  #mode-bar {{
    display: flex;
    background: #f8fafc;
    border-bottom: 1px solid #e2e8f0;
    padding: 8px 12px;
    gap: 6px;
    flex-shrink: 0;
  }}
  .mode-btn {{
    flex: 1;
    padding: 6px;
    border: 1.5px solid #e2e8f0;
    border-radius: 8px;
    background: white;
    cursor: pointer;
    font-size: 11.5px;
    font-weight: 600;
    color: #64748b;
    transition: all 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 4px;
  }}
  .mode-btn.active {{
    background: linear-gradient(135deg, #0ea5e9, #14b8a6);
    color: white;
    border-color: transparent;
    box-shadow: 0 2px 8px rgba(14,165,233,0.3);
  }}

  /* ── Messages ───────────────────────────────────────── */
  #ipcms-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    scroll-behavior: smooth;
  }}
  #ipcms-messages::-webkit-scrollbar {{ width: 4px; }}
  #ipcms-messages::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}

  .msg-row {{
    display: flex;
    gap: 8px;
    align-items: flex-end;
    animation: msgIn 0.3s cubic-bezier(0.34,1.56,0.64,1);
  }}
  @keyframes msgIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
  }}
  .msg-row.user {{ flex-direction: row-reverse; }}
  .msg-avatar {{
    width: 30px; height: 30px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; flex-shrink: 0;
  }}
  .msg-avatar.ai-av {{
    background: linear-gradient(135deg,#0ea5e9,#14b8a6);
    color: white;
  }}
  .msg-avatar.user-av {{
    background: linear-gradient(135deg,#6366f1,#8b5cf6);
    color: white;
  }}
  .bubble {{
    max-width: 78%;
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 13.5px;
    line-height: 1.55;
    position: relative;
  }}
  .bubble.ai {{
    background: white;
    border: 1.5px solid #e2e8f0;
    border-bottom-left-radius: 4px;
    color: #1e293b;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }}
  .bubble.user {{
    background: linear-gradient(135deg,#0ea5e9,#0284c7);
    border-bottom-right-radius: 4px;
    color: white;
    box-shadow: 0 2px 10px rgba(14,165,233,0.3);
  }}
  .bubble-meta {{
    font-size: 10px;
    margin-top: 4px;
    opacity: 0.6;
    display: flex;
    align-items: center;
    gap: 4px;
  }}
  .user .bubble-meta {{ justify-content: flex-end; }}

  /* ── Speaking indicator ─────────────────────────────── */
  .speaking-bars {{
    display: inline-flex; gap: 2px; align-items: flex-end; height: 14px;
  }}
  .speaking-bars span {{
    width: 3px; border-radius: 2px;
    background: #0ea5e9;
    animation: barBounce 0.8s ease-in-out infinite;
  }}
  .speaking-bars span:nth-child(2) {{ animation-delay: 0.1s; height: 10px; }}
  .speaking-bars span:nth-child(3) {{ animation-delay: 0.2s; height: 14px; }}
  .speaking-bars span:nth-child(4) {{ animation-delay: 0.1s; height: 10px; }}
  .speaking-bars span:nth-child(1),
  .speaking-bars span:nth-child(5) {{ height: 7px; }}
  @keyframes barBounce {{
    0%, 100% {{ transform: scaleY(0.5); opacity: 0.6; }}
    50% {{ transform: scaleY(1.2); opacity: 1; }}
  }}

  /* ── Typing dots ────────────────────────────────────── */
  #typing-indicator {{
    display: none;
    padding: 10px 14px;
    background: white;
    border: 1.5px solid #e2e8f0;
    border-radius: 16px;
    border-bottom-left-radius: 4px;
    width: fit-content;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    animation: msgIn 0.3s ease;
  }}
  .typing-dots {{ display: flex; gap: 4px; align-items: center; }}
  .typing-dots span {{
    width: 7px; height: 7px; border-radius: 50%;
    background: #0ea5e9; opacity: 0.5;
    animation: dot 1.2s ease-in-out infinite;
  }}
  .typing-dots span:nth-child(2) {{ animation-delay: 0.2s; }}
  .typing-dots span:nth-child(3) {{ animation-delay: 0.4s; }}
  @keyframes dot {{
    0%, 80%, 100% {{ transform: scale(1); opacity: 0.5; }}
    40% {{ transform: scale(1.3); opacity: 1; }}
  }}

  /* ── Input area ─────────────────────────────────────── */
  #ipcms-input-area {{
    border-top: 1px solid #e2e8f0;
    padding: 12px 14px;
    background: #f8fafc;
    flex-shrink: 0;
  }}

  /* ── Voice recording animation ──────────────────────── */
  #voice-panel {{
    display: none;
    flex-direction: column;
    align-items: center;
    gap: 10px;
    padding: 8px 0;
  }}
  #voice-ripple {{
    width: 64px; height: 64px; border-radius: 50%;
    background: linear-gradient(135deg, #ef4444, #dc2626);
    display: flex; align-items: center; justify-content: center;
    box-shadow: 0 0 0 0 rgba(239,68,68,0.5);
    animation: ripple 1.2s ease-in-out infinite;
    font-size: 24px;
    cursor: pointer;
  }}
  @keyframes ripple {{
    0% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }}
    70% {{ box-shadow: 0 0 0 20px rgba(239,68,68,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0); }}
  }}
  #voice-label {{
    font-size: 12px; color: #ef4444; font-weight: 600;
    letter-spacing: 0.5px; text-align: center;
  }}
  #voice-transcript {{
    font-size: 12px; color: #64748b; font-style: italic;
    text-align: center; min-height: 16px;
  }}

  /* ── Text input panel ───────────────────────────────── */
  #text-panel {{
    display: flex;
    gap: 8px;
    align-items: flex-end;
  }}
  #chat-input {{
    flex: 1;
    padding: 10px 14px;
    border: 1.5px solid #e2e8f0;
    border-radius: 12px;
    font-size: 13.5px;
    resize: none;
    outline: none;
    font-family: inherit;
    background: white;
    color: #1e293b;
    max-height: 80px;
    transition: border-color 0.2s, box-shadow 0.2s;
    line-height: 1.4;
  }}
  #chat-input:focus {{
    border-color: #0ea5e9;
    box-shadow: 0 0 0 3px rgba(14,165,233,0.12);
  }}
  #chat-input::placeholder {{ color: #94a3b8; }}
  .action-btn {{
    width: 40px; height: 40px;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
    flex-shrink: 0;
    transition: all 0.2s;
  }}
  #send-btn {{
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    box-shadow: 0 2px 8px rgba(14,165,233,0.35);
  }}
  #send-btn:hover {{ transform: scale(1.08); box-shadow: 0 4px 14px rgba(14,165,233,0.5); }}
  #mic-btn {{
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    box-shadow: 0 2px 8px rgba(99,102,241,0.3);
  }}
  #mic-btn.listening {{
    background: linear-gradient(135deg, #ef4444, #dc2626);
    animation: ripple 1.2s infinite;
  }}
  #mic-btn:hover {{ transform: scale(1.08); }}

  /* ── Quick prompts ──────────────────────────────────── */
  #quick-prompts {{
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 8px;
  }}
  .qp-chip {{
    padding: 4px 10px;
    border: 1px solid #e2e8f0;
    border-radius: 20px;
    font-size: 11px;
    color: #0284c7;
    background: white;
    cursor: pointer;
    transition: all 0.2s;
    font-weight: 500;
  }}
  .qp-chip:hover {{
    background: #eff6ff;
    border-color: #0ea5e9;
    transform: scale(1.04);
  }}

  /* ── Notification badge ─────────────────────────────── */
  #ipcms-badge {{
    position: absolute;
    top: -2px; right: -2px;
    background: #ef4444;
    color: white;
    border-radius: 50%;
    width: 20px; height: 20px;
    font-size: 11px;
    font-weight: 700;
    display: none;
    align-items: center;
    justify-content: center;
    border: 2px solid white;
    box-shadow: 0 2px 6px rgba(239,68,68,0.4);
  }}
</style>
</head>
<body>

<!-- Floating Action Button -->
<div style="position:fixed;bottom:28px;right:28px;z-index:2147483647;">
  <button id="ipcms-fab" onclick="togglePanel()" title="IPCMS Voice Assistant">
    <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 1.93c-3.94-.49-7-3.85-7-7.93h2c0 3.31 2.69 6 6 6s6-2.69 6-6h2c0 4.08-3.06 7.44-7 7.93V21h-2v-5.07z" id="fab-icon-path"/>
    </svg>
    <div id="ipcms-badge">1</div>
  </button>
</div>

<!-- Chat Panel -->
<div id="ipcms-panel">

  <!-- Header -->
  <div id="ipcms-header">
    <div class="hdr-avatar">🏥</div>
    <div class="hdr-info">
      <div class="hdr-name">IPCMS Health Assistant</div>
      <div class="hdr-status">
        <div class="status-dot"></div>
        <span>AI Voice Ready · Online</span>
      </div>
    </div>
    <button class="hdr-close" onclick="togglePanel()">✕</button>
  </div>

  <!-- Mode Bar -->
  <div id="mode-bar">
    <button class="mode-btn active" id="mode-voice-btn" onclick="setMode('voice')">🎤 Voice</button>
    <button class="mode-btn" id="mode-text-btn" onclick="setMode('text')">⌨️ Text</button>
    <button class="mode-btn" id="mode-clear-btn" onclick="clearChat()" style="flex:0.5;color:#ef4444;border-color:#fecaca;">🗑️</button>
  </div>

  <!-- Messages -->
  <div id="ipcms-messages">
    <div class="msg-row">
      <div class="msg-avatar ai-av">🤖</div>
      <div>
        <div class="bubble ai">
          👋 Hello! I'm your IPCMS Voice AI Assistant.<br><br>
          🎤 Press the mic button to speak, or type your question in text.<br>
          I will answer and read responses aloud to you!
        </div>
        <div class="bubble-meta ai">Now · IPCMS AI</div>
      </div>
    </div>
    <div id="typing-indicator">
      <div class="typing-dots">
        <span></span><span></span><span></span>
      </div>
    </div>
  </div>

  <!-- Input Area -->
  <div id="ipcms-input-area">

    <!-- Quick Prompts -->
    <div id="quick-prompts">
      <span class="qp-chip" onclick="sendQuick('What are symptoms of diabetes?')">🩺 Diabetes symptoms</span>
      <span class="qp-chip" onclick="sendQuick('How do I book an appointment?')">📅 Book appointment</span>
      <span class="qp-chip" onclick="sendQuick('What medicines should I avoid with blood pressure?')">💊 BP medicines</span>
      <span class="qp-chip" onclick="sendQuick('Tips for a healthy heart')">❤️ Heart health</span>
    </div>

    <!-- Voice Panel -->
    <div id="voice-panel">
      <div id="voice-ripple" onclick="stopRecording()" title="Click to stop">🎤</div>
      <div id="voice-label">LISTENING… click to stop</div>
      <div id="voice-transcript">Start speaking…</div>
    </div>

    <!-- Text Panel -->
    <div id="text-panel">
      <textarea id="chat-input" placeholder="Type your health question…" rows="1"
        onkeydown="handleKey(event)" oninput="autoResize(this)"></textarea>
      <button class="action-btn" id="mic-btn" onclick="toggleRecording()" title="Voice input">🎤</button>
      <button class="action-btn" id="send-btn" onclick="sendText()" title="Send">
        <svg viewBox="0 0 24 24" width="18" height="18" fill="white">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/>
        </svg>
      </button>
    </div>

  </div>
</div>

<script>
// ── Configuration ───────────────────────────────────────────────────────────
const GEMINI_API_KEY = "{gemini_api_key}";
const GROQ_API_KEY   = "{groq_api_key}";

const SYSTEM_PROMPT = `You are IPCMS Health Assistant, an AI medical assistant for the Integrated Patient Care Management System.
You help patients and healthcare professionals with medical questions, appointment guidance, medicine information, and health tips.
Keep responses concise, warm, empathetic, and clear (max 75-90 words) — optimized for voice output.
Never provide a definitive medical diagnosis. Always suggest consulting a physician for severe symptoms.`;

// ── Local Medical KB Fallback Engine ──────────────────────────────────────────
function getLocalMedicalKnowledge(query) {{
  const q = query.toLowerCase();
  if (q.includes('diabetes') || q.includes('sugar') || q.includes('glucose')) {{
    return "Common diabetes symptoms include increased thirst, frequent urination, fatigue, and blurred vision. Maintain a balanced low-sugar diet, exercise daily, and monitor your blood glucose level regularly.";
  }}
  if (q.includes('appointment') || q.includes('book') || q.includes('doctor') || q.includes('schedule')) {{
    return "To book an appointment in IPCMS: sign in to your Patient Portal, click 'Appointments' in the sidebar menu, choose a doctor and available date/time slot, then click 'Confirm Booking'.";
  }}
  if (q.includes('bp') || q.includes('blood pressure') || q.includes('hypertension')) {{
    return "Normal blood pressure is under 120/80 mmHg. Reduce sodium intake, manage stress, stay physically active, and consult your doctor for proper anti-hypertensive medication.";
  }}
  if (q.includes('heart') || q.includes('cardio') || q.includes('chest')) {{
    return "For heart health: consume omega-3 rich foods, exercise at least 30 minutes daily, and avoid smoking. If you experience severe chest pressure or shortness of breath, seek emergency medical care immediately.";
  }}
  if (q.includes('medicine') || q.includes('prescription') || q.includes('drug')) {{
    return "You can check your active prescriptions and medicine schedules under 'Prescriptions' in the IPCMS Patient Portal. Always consult your doctor before modifying medication dosages.";
  }}
  if (q.includes('flu') || q.includes('fever') || q.includes('cough') || q.includes('cold')) {{
    return "For mild flu or fever: rest well, drink plenty of water, and monitor your temperature. If fever exceeds 102°F (38.9°C) or lasts over 3 days, consult a physician promptly.";
  }}
  return "Thank you for asking IPCMS Health Assistant. I am here to help with symptom information, appointment booking, prescription details, and general wellness. Please consult a qualified doctor for medical diagnoses.";
}}

// ── State ────────────────────────────────────────────────────────────────────
let chatHistory = [];
let panelOpen   = false;
let currentMode = 'voice';
let isListening = false;
let isSpeaking  = false;
let recognition = null;
let currentUtterance = null;
let msgCount = 0;
let accumulatedText = '';

// ── Panel toggle ─────────────────────────────────────────────────────────────
function togglePanel() {{
  panelOpen = !panelOpen;
  const panel = document.getElementById('ipcms-panel');
  const badge = document.getElementById('ipcms-badge');
  const fabPath = document.getElementById('fab-icon-path');
  if (panelOpen) {{
    panel.classList.add('open');
    badge.style.display = 'none';
    fabPath.setAttribute('d', 'M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z');
  }} else {{
    panel.classList.remove('open');
    fabPath.setAttribute('d', 'M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3zm-1 1.93c-3.94-.49-7-3.85-7-7.93h2c0 3.31 2.69 6 6 6s6-2.69 6-6h2c0 4.08-3.06 7.44-7 7.93V21h-2v-5.07z');
  }}
}}

// ── Mode switching ────────────────────────────────────────────────────────────
function setMode(mode) {{
  currentMode = mode;
  document.getElementById('mode-voice-btn').classList.toggle('active', mode === 'voice');
  document.getElementById('mode-text-btn').classList.toggle('active', mode === 'text');
  document.getElementById('voice-panel').style.display = 'none';
  document.getElementById('text-panel').style.display = 'flex';
  document.getElementById('quick-prompts').style.display = 'flex';
  if (mode === 'voice') {{
    document.getElementById('chat-input').placeholder = 'Click mic to speak, or type here…';
  }} else {{
    document.getElementById('chat-input').placeholder = 'Type your health question…';
  }}
}}

// ── Scroll to bottom ─────────────────────────────────────────────────────────
function scrollBottom() {{
  const msgs = document.getElementById('ipcms-messages');
  msgs.scrollTop = msgs.scrollHeight;
}}

// ── Add message ──────────────────────────────────────────────────────────────
function addMessage(text, role, extraHTML = '') {{
  const msgs  = document.getElementById('ipcms-messages');
  const typing = document.getElementById('typing-indicator');
  const time   = new Date().toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}});

  const row = document.createElement('div');
  row.className = `msg-row ${{role === 'user' ? 'user' : ''}}`;

  const avatarDiv = `<div class="msg-avatar ${{role === 'user' ? 'user-av' : 'ai-av'}}">${{role === 'user' ? '👤' : '🤖'}}</div>`;
  const metaDiv   = `<div class="bubble-meta ${{role === 'user' ? 'user' : ''}}">${{time}} · ${{role === 'user' ? 'You' : 'IPCMS AI'}} ${{extraHTML}}</div>`;
  const bubbleDiv = `<div class="bubble ${{role === 'user' ? 'user' : 'ai'}}">${{text}}</div>`;

  row.innerHTML = role === 'user'
    ? `<div>${{bubbleDiv}}${{metaDiv}}</div>${{avatarDiv}}`
    : `${{avatarDiv}}<div>${{bubbleDiv}}${{metaDiv}}</div>`;

  msgs.insertBefore(row, typing);
  scrollBottom();
  msgCount++;
}}

// ── Typing indicator ─────────────────────────────────────────────────────────
function showTyping(show) {{
  const el = document.getElementById('typing-indicator');
  el.style.display = show ? 'block' : 'none';
  if (show) scrollBottom();
}}

// ── Voice output (TTS) ───────────────────────────────────────────────────────
function speak(text) {{
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();

  const clean = text.replace(/[*_`#>]/g, '').replace(/\\n+/g, ' ').trim();
  const utterance = new SpeechSynthesisUtterance(clean);
  utterance.lang  = 'en-US';
  utterance.rate  = 0.94;
  utterance.pitch = 1.02;

  const voices = window.speechSynthesis.getVoices();
  const preferred = voices.find(v =>
    v.lang === 'en-US' && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Zira') || v.name.includes('Samantha'))
  ) || voices.find(v => v.lang === 'en-US') || voices[0];

  if (preferred) utterance.voice = preferred;
  utterance.onstart = () => {{ isSpeaking = true; }};
  utterance.onend   = () => {{ isSpeaking = false; }};

  currentUtterance = utterance;
  window.speechSynthesis.speak(utterance);
}}

// ── Multi-tiered Robust AI Cascade ───────────────────────────────────────────
async function fetchAIResponse(userText) {{
  // 1. Gemini API (if key starts with AIza)
  if (GEMINI_API_KEY && GEMINI_API_KEY.startsWith("AIza")) {{
    try {{
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${{GEMINI_API_KEY}}`;
      const body = {{
        contents: chatHistory,
        systemInstruction: {{ parts: [{{ text: SYSTEM_PROMPT }}] }},
        generationConfig: {{ maxOutputTokens: 220, temperature: 0.5 }}
      }};
      const resp = await fetch(endpoint, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify(body)
      }});
      if (resp.ok) {{
        const data = await resp.json();
        const text = data.candidates?.[0]?.content?.parts?.[0]?.text;
        if (text && text.trim()) return text.trim();
      }}
    }} catch(e) {{
      console.warn("Gemini API error, attempting Groq fallback:", e);
    }}
  }}

  // 2. Groq API Fallback
  if (GROQ_API_KEY && GROQ_API_KEY.length > 10) {{
    try {{
      const messages = [
        {{ role: 'system', content: SYSTEM_PROMPT }},
        ...chatHistory.map(m => ({{ role: m.role === 'model' ? 'assistant' : 'user', content: m.parts[0].text }})),
        {{ role: 'user', content: userText }}
      ];
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {{
        method: 'POST',
        headers: {{
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${{GROQ_API_KEY}}`
        }},
        body: JSON.stringify({{
          model: 'llama-3.1-8b-instant',
          messages: messages,
          max_tokens: 220,
          temperature: 0.5
        }})
      }});
      if (resp.ok) {{
        const data = await resp.json();
        const text = data.choices?.[0]?.message?.content;
        if (text && text.trim()) return text.trim();
      }}
    }} catch(e) {{
      console.warn("Groq API error, using local medical KB:", e);
    }}
  }}

  // 3. Smart Local Medical Knowledge Base Fallback
  return getLocalMedicalKnowledge(userText);
}}

// ── Send message (core) ───────────────────────────────────────────────────────
async function send(userText) {{
  if (!userText.trim()) return;

  addMessage(userText, 'user');
  chatHistory.push({{ role: 'user', parts: [{{ text: userText }}] }});
  showTyping(true);
  document.getElementById('quick-prompts').style.display = 'none';

  try {{
    const reply = await fetchAIResponse(userText);
    chatHistory.push({{ role: 'model', parts: [{{ text: reply }}] }});

    showTyping(false);
    const speakMeta = `<span class="speaking-bars" style="display:inline-flex"><span></span><span></span><span></span><span></span><span></span></span>`;
    addMessage(reply, 'ai', speakMeta);
    speak(reply);

  }} catch(err) {{
    showTyping(false);
    const fallback = getLocalMedicalKnowledge(userText);
    addMessage(fallback, 'ai');
    speak(fallback);
  }}
}}

// ── Text send ─────────────────────────────────────────────────────────────────
function sendText() {{
  const input = document.getElementById('chat-input');
  const text  = input.value.trim();
  if (!text) return;
  input.value = '';
  input.style.height = 'auto';
  send(text);
}}

function sendQuick(text) {{
  send(text);
}}

function handleKey(e) {{
  if (e.key === 'Enter' && !e.shiftKey) {{
    e.preventDefault();
    sendText();
  }}
}}

function autoResize(el) {{
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 80) + 'px';
}}

// ── Voice Recognition (Cross-Frame & Continuous) ──────────────────────────────
function getSRClass() {{
  try {{
    var p = (window.parent && window.parent !== window) ? window.parent : window;
    return p.SpeechRecognition || p.webkitSpeechRecognition || window.SpeechRecognition || window.webkitSpeechRecognition;
  }} catch(e) {{
    return window.SpeechRecognition || window.webkitSpeechRecognition;
  }}
}}

function toggleRecording() {{
  if (isListening) {{
    stopRecording();
  }} else {{
    startRecording();
  }}
}}

function startRecording() {{
  if (isSpeaking) {{ window.speechSynthesis.cancel(); }}

  const SR = getSRClass();
  if (!SR) {{
    alert('Voice recognition is not supported in this browser. Please use Chrome or Edge.');
    return;
  }}

  document.getElementById('voice-panel').style.display = 'flex';
  document.getElementById('text-panel').style.display = 'none';
  document.getElementById('quick-prompts').style.display = 'none';
  document.getElementById('voice-transcript').textContent = 'Requesting microphone…';

  /* getUserMedia triggers browser mic permission dialog — required inside iframes */
  navigator.mediaDevices.getUserMedia({{ audio: true }})
    .then(function(stream) {{
      stream.getTracks().forEach(t => t.stop()); // release raw stream immediately

      try {{
        recognition = new SR();
      }} catch(e) {{
        console.error('SpeechRecognition init error:', e);
        document.getElementById('voice-transcript').textContent = 'SR init failed';
        return;
      }}

      recognition.lang = 'en-US';
      recognition.interimResults = true;
      recognition.continuous = false;
      recognition.maxAlternatives = 1;
      accumulatedText = '';

      let silenceTimer = null;

      document.getElementById('mic-btn').classList.add('listening');
      document.getElementById('voice-transcript').textContent = 'Listening… speak now';
      isListening = true;

      recognition.onresult = function(e) {{
        let interim = '';
        let final   = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {{
          if (e.results[i].isFinal) final += e.results[i][0].transcript + ' ';
          else interim += e.results[i][0].transcript;
        }}
        if (final) accumulatedText += final;
        const current = (accumulatedText + interim).trim();
        document.getElementById('voice-transcript').textContent = current || 'Listening…';
        document.getElementById('chat-input').value = current;

        /* Auto-submit 1.2s after user pauses speaking */
        if (silenceTimer) clearTimeout(silenceTimer);
        if (current.length > 0) {{
          silenceTimer = setTimeout(function() {{
            if (isListening && recognition) {{
              try {{ recognition.stop(); }} catch(err) {{}}
            }}
          }}, 1200);
        }}
      }};

      recognition.onerror = function(e) {{
        console.warn('SpeechRecognition error:', e.error);
        if (silenceTimer) clearTimeout(silenceTimer);
        if (e.error === 'no-speech') {{
          document.getElementById('voice-transcript').textContent = 'No speech detected';
          stopRecording();
          return;
        }}
        stopRecording();
        if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {{
          document.getElementById('voice-transcript').textContent = 'Mic blocked';
        }} else if (e.error !== 'aborted') {{
          addMessage('Voice error: ' + e.error + '. Try typing instead.', 'ai');
        }}
      }};

      recognition.onend = function() {{
        if (silenceTimer) clearTimeout(silenceTimer);
        const captured = (accumulatedText || document.getElementById('chat-input').value).trim();
        stopRecording();
        if (captured && captured !== 'Listening…' && captured.length > 1) {{
          send(captured);
        }}
      }};

      try {{
        recognition.start();
      }} catch(e) {{
        console.error('Failed to start SpeechRecognition:', e);
        stopRecording();
      }}
    }})
    .catch(function(err) {{
      console.error('getUserMedia denied:', err);
      document.getElementById('voice-transcript').textContent = 'Mic denied';
      stopRecording();
      alert('Microphone access was denied.\\n\\nTo fix:\\n1. Click the 🔒 lock icon in your browser address bar\\n2. Set Microphone to Allow\\n3. Refresh the page');
    }});
}}

function stopRecording() {{
  isListening = false;
  document.getElementById('mic-btn').classList.remove('listening');
  if (recognition) {{
    try {{ recognition.stop(); }} catch(e) {{}}
    recognition = null;
  }}
  document.getElementById('voice-panel').style.display = 'none';
  document.getElementById('text-panel').style.display = 'flex';
  document.getElementById('quick-prompts').style.display = 'flex';
}}

// ── Clear chat ────────────────────────────────────────────────────────────────
function clearChat() {{
  chatHistory = [];
  const msgs = document.getElementById('ipcms-messages');
  const typing = document.getElementById('typing-indicator');
  while (msgs.firstChild && msgs.firstChild !== typing) {{
    msgs.removeChild(msgs.firstChild);
  }}
  addMessage('Chat cleared. How can I help you today?', 'ai');
  document.getElementById('quick-prompts').style.display = 'flex';
}}

// ── Init ───────────────────────────────────────────────────────────────────────
if (window.speechSynthesis) {{ window.speechSynthesis.getVoices(); }}
setTimeout(() => {{
  if (window.speechSynthesis) {{ window.speechSynthesis.getVoices(); }}
  const badge = document.getElementById('ipcms-badge');
  if (badge) {{ badge.style.display = 'flex'; badge.textContent = '1'; }}
}}, 2000);
</script>
</body>
</html>
"""


def inject_voice_chatbot():
    """
    Injects the floating voice chatbot widget into the current Streamlit page.

    Strategy: components.html() creates an iframe. When height=0, `position:fixed`
    elements inside the iframe are clipped to its zero-height viewport and become
    invisible. To work around this, we use components.html() but have the script
    inside inject all CSS and HTML directly into window.parent.document (the real
    Streamlit host page), then run the logic there. The iframe stays tiny (height=1)
    with no visual impact.
    """
    import re
    import json

    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    groq_key   = os.getenv("GROQ_API_KEY", "").strip()

    full_html = _build_chatbot_html(gemini_key, groq_key)

    style_match = re.search(r'<style>(.*?)</style>', full_html, re.DOTALL)
    css_text = style_match.group(1) if style_match else ''

    body_match = re.search(r'<body>(.*?)</body>', full_html, re.DOTALL)
    body_html  = body_match.group(1) if body_match else ''

    script_match = re.search(r'<script>(.*?)</script>', full_html, re.DOTALL)
    js_text = script_match.group(1) if script_match else ''

    css_json  = json.dumps(css_text)
    body_json = json.dumps(body_html)
    js_json   = json.dumps(js_text)

    injector = """<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"/></head>
<body>
<script>
(function() {
    var parentDoc = window.parent.document;
    if (parentDoc.getElementById('ipcms-fab')) return;
    var styleEl = parentDoc.createElement('style');
    styleEl.id = 'ipcms-chatbot-styles';
    styleEl.textContent = """ + css_json + """;
    parentDoc.head.appendChild(styleEl);
    var container = parentDoc.createElement('div');
    container.id = 'ipcms-chatbot-root';
    container.innerHTML = """ + body_json + """;
    parentDoc.body.appendChild(container);
    var scriptEl = parentDoc.createElement('script');
    scriptEl.textContent = """ + js_json + """;
    parentDoc.body.appendChild(scriptEl);
})();
</script>
</body>
</html>"""
    components.html(injector, height=1, scrolling=False)


def _build_inline_chatbot_html(gemini_api_key: str, groq_api_key: str) -> str:
    """Build self-contained HTML/CSS/JS for an INLINE voice chatbot panel embedded inside page layout."""
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8"/>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
    background: transparent;
    padding: 2px;
  }}

  /* ── Main Container ──────────────────────────────────── */
  #inline-panel {{
    width: 100%;
    height: 520px;
    border-radius: 20px;
    background: linear-gradient(145deg, #ffffff, #f8fafc);
    border: 1.5px solid rgba(14,165,233,0.25);
    box-shadow: 0 12px 36px rgba(14,165,233,0.12), 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }}

  /* ── Header ─────────────────────────────────────────── */
  #inline-header {{
    background: linear-gradient(135deg, #0ea5e9 0%, #0284c7 50%, #14b8a6 100%);
    padding: 14px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    color: white;
  }}
  .hdr-left {{ display: flex; align-items: center; gap: 12px; }}
  .hdr-icon {{
    width: 40px; height: 40px; border-radius: 50%;
    background: rgba(255,255,255,0.22);
    border: 2px solid rgba(255,255,255,0.4);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
  }}
  .hdr-title {{ font-size: 16px; font-weight: 700; letter-spacing: -0.2px; }}
  .hdr-sub {{ font-size: 11px; opacity: 0.9; margin-top: 1px; display: flex; align-items: center; gap: 6px; }}
  .online-dot {{
    width: 7px; height: 7px; border-radius: 50%; background: #4ade80;
    box-shadow: 0 0 6px #4ade80; animation: pulseDot 2s infinite;
  }}
  @keyframes pulseDot {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.4; }} }}

  .voice-only-badge {{
    background: rgba(255,255,255,0.2);
    border: 1px solid rgba(255,255,255,0.4);
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.3px;
    display: flex; align-items: center; gap: 5px;
  }}

  /* ── Controls Bar ───────────────────────────────────── */
  #controls-bar {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 16px;
    background: #f1f5f9;
    border-bottom: 1px solid #e2e8f0;
  }}
  .mode-switch {{ display: flex; gap: 6px; }}
  .tab-btn {{
    padding: 5px 12px; border-radius: 8px; border: 1px solid #cbd5e1;
    background: white; color: #475569; font-size: 11.5px; font-weight: 600;
    cursor: pointer; transition: all 0.2s;
  }}
  .tab-btn.active {{
    background: linear-gradient(135deg, #0ea5e9, #14b8a6);
    color: white; border-color: transparent;
    box-shadow: 0 2px 6px rgba(14,165,233,0.3);
  }}
  .clear-btn {{
    background: #fef2f2; color: #ef4444; border: 1px solid #fecaca;
    padding: 4px 10px; border-radius: 8px; font-size: 11px; font-weight: 600;
    cursor: pointer; transition: background 0.2s;
  }}
  .clear-btn:hover {{ background: #fee2e2; }}

  /* ── Messages Box ───────────────────────────────────── */
  #inline-messages {{
    flex: 1;
    overflow-y: auto;
    padding: 16px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    background: #fafafa;
  }}
  #inline-messages::-webkit-scrollbar {{ width: 5px; }}
  #inline-messages::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}

  .msg-row {{
    display: flex; gap: 10px; align-items: flex-end;
    animation: msgFade 0.3s ease;
  }}
  @keyframes msgFade {{ from {{ opacity: 0; transform: translateY(8px); }} to {{ opacity: 1; transform: translateY(0); }} }}
  .msg-row.user {{ flex-direction: row-reverse; }}
  .avatar {{
    width: 32px; height: 32px; border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; flex-shrink: 0;
  }}
  .avatar.ai {{ background: linear-gradient(135deg,#0ea5e9,#14b8a6); color: white; }}
  .avatar.user {{ background: linear-gradient(135deg,#6366f1,#8b5cf6); color: white; }}

  .bubble {{
    max-width: 80%; padding: 10px 14px; border-radius: 16px;
    font-size: 13.5px; line-height: 1.5;
  }}
  .bubble.ai {{
    background: white; border: 1.5px solid #e2e8f0;
    border-bottom-left-radius: 4px; color: #1e293b;
    box-shadow: 0 2px 6px rgba(0,0,0,0.04);
  }}
  .bubble.user {{
    background: linear-gradient(135deg,#0ea5e9,#0284c7);
    border-bottom-right-radius: 4px; color: white;
    box-shadow: 0 2px 8px rgba(14,165,233,0.25);
  }}
  .time-stamp {{ font-size: 10px; opacity: 0.6; margin-top: 3px; display: flex; align-items: center; gap: 4px; }}
  .user .time-stamp {{ justify-content: flex-end; }}

  /* ── Speaking bars visualizer ───────────────────────── */
  .wave-bars {{ display: inline-flex; gap: 2px; align-items: flex-end; height: 12px; }}
  .wave-bars span {{
    width: 3px; background: #0ea5e9; border-radius: 2px;
    animation: waveBounce 0.8s ease-in-out infinite;
  }}
  .wave-bars span:nth-child(2) {{ animation-delay: 0.15s; height: 10px; }}
  .wave-bars span:nth-child(3) {{ animation-delay: 0.3s; height: 12px; }}
  .wave-bars span:nth-child(4) {{ animation-delay: 0.15s; height: 8px; }}
  @keyframes waveBounce {{ 0%, 100% {{ transform: scaleY(0.4); }} 50% {{ transform: scaleY(1.2); }} }}

  /* ── Big Voice Action Center ────────────────────────── */
  #inline-input-area {{
    background: white;
    border-top: 1px solid #e2e8f0;
    padding: 12px 16px;
    display: flex;
    flex-direction: column;
    gap: 8px;
  }}

  /* Quick chips */
  #quick-chips {{ display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; }}
  .q-chip {{
    padding: 4px 10px; border: 1px solid #e2e8f0; border-radius: 16px;
    font-size: 11px; color: #0284c7; background: #f0f9ff; cursor: pointer;
    white-space: nowrap; font-weight: 500; transition: all 0.2s;
  }}
  .q-chip:hover {{ background: #e0f2fe; border-color: #0ea5e9; transform: translateY(-1px); }}

  /* Voice Center */
  #voice-center {{
    display: flex;
    align-items: center;
    gap: 12px;
    background: #f8fafc;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 8px 12px;
  }}

  #big-mic-btn {{
    width: 46px; height: 46px; border-radius: 50%;
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    border: none; color: white; font-size: 20px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    box-shadow: 0 4px 14px rgba(14,165,233,0.4);
    transition: transform 0.2s, box-shadow 0.2s;
    flex-shrink: 0;
  }}
  #big-mic-btn:hover {{ transform: scale(1.08); box-shadow: 0 6px 18px rgba(14,165,233,0.5); }}
  #big-mic-btn.listening {{
    background: linear-gradient(135deg, #ef4444, #dc2626);
    box-shadow: 0 0 0 8px rgba(239,68,68,0.25);
    animation: recPulse 1.2s infinite;
  }}
  @keyframes recPulse {{ 0%, 100% {{ box-shadow: 0 0 0 0 rgba(239,68,68,0.4); }} 50% {{ box-shadow: 0 0 0 10px rgba(239,68,68,0); }} }}

  #input-field {{
    flex: 1; border: none; background: transparent;
    outline: none; font-size: 13.5px; color: #1e293b;
    font-family: inherit;
  }}
  #input-field::placeholder {{ color: #94a3b8; }}

  #send-icon-btn {{
    width: 38px; height: 38px; border-radius: 10px;
    background: linear-gradient(135deg, #0ea5e9, #0284c7);
    border: none; color: white; font-size: 16px;
    cursor: pointer; display: flex; align-items: center; justify-content: center;
    flex-shrink: 0; transition: transform 0.2s;
  }}
  #send-icon-btn:hover {{ transform: scale(1.06); }}

  #status-txt {{ font-size: 11.5px; color: #64748b; font-style: italic; }}
</style>
</head>
<body>

<div id="inline-panel">
  <!-- Header -->
  <div id="inline-header">
    <div class="hdr-left">
      <div class="hdr-icon">🎙️</div>
      <div>
        <div class="hdr-title">IPCMS Voice Assistant</div>
        <div class="hdr-sub">
          <span class="online-dot"></span>
          <span>Interactive AI Voice Console · 100% Voice Response Output</span>
        </div>
      </div>
    </div>
    <div class="voice-only-badge">
      <span>🔊 Voice Format Output</span>
    </div>
  </div>

  <!-- Controls Bar -->
  <div id="controls-bar">
    <div class="mode-switch">
      <button class="tab-btn active" id="btn-voice" onclick="setInlineMode('voice')">🎤 Voice Mode</button>
      <button class="tab-btn" id="btn-text" onclick="setInlineMode('text')">⌨️ Text Mode</button>
    </div>
    <span id="status-txt">Ready to listen</span>
    <button class="clear-btn" onclick="clearInlineChat()">🗑️ Clear</button>
  </div>

  <!-- Messages Container -->
  <div id="inline-messages">
    <div class="msg-row">
      <div class="avatar ai">🤖</div>
      <div>
        <div class="bubble ai">
          👋 Welcome to the <b>IPCMS Voice AI Assistant</b>!<br>
          Press the <b>🎤 Mic Button</b> below to ask any medical, appointment, or health question.<br>
          I will answer and read the full response to you in <b>voice audio format</b>!
        </div>
        <div class="time-stamp">Now · Voice AI</div>
      </div>
    </div>
  </div>

  <!-- Input Area -->
  <div id="inline-input-area">
    <div id="quick-chips">
      <span class="q-chip" onclick="quickSend('What are common symptoms of flu?')">🌡️ Flu Symptoms</span>
      <span class="q-chip" onclick="quickSend('How to book an appointment with doctor?')">📅 Book Doctor</span>
      <span class="q-chip" onclick="quickSend('What is healthy blood pressure range?')">💓 Healthy BP</span>
      <span class="q-chip" onclick="quickSend('Tips for diabetes prevention')">🥗 Diabetes Prevention</span>
    </div>

    <div id="voice-center">
      <button id="big-mic-btn" onclick="toggleMic()" title="Click to speak">🎤</button>
      <input type="text" id="input-field" placeholder="Click mic to speak, or type your question here…" onkeydown="if(event.key==='Enter') sendInlineText()"/>
      <button id="send-icon-btn" onclick="sendInlineText()" title="Send">➤</button>
    </div>
  </div>
</div>

<script>
const GEMINI_KEY = "{gemini_api_key}";
const GROQ_KEY   = "{groq_api_key}";

const SYSTEM_PROMPT_VOICE = `You are IPCMS Voice AI Assistant.
Your output will be read ALOUD to the user as voice audio.
Keep responses clear, empathetic, direct, and concise (max 75-90 words).
Never use markdown asterisks or complex code blocks.
Format your answer so it sounds natural when spoken aloud.`;

function getInlineLocalFallback(query) {{
  const q = query.toLowerCase();
  if (q.includes('symptom') || q.includes('flu') || q.includes('fever') || q.includes('cough')) {{
    return "Common flu symptoms include fever, body aches, fatigue, and cough. Stay well hydrated, rest, and consult a doctor if your fever exceeds 102°F or lasts longer than 3 days.";
  }}
  if (q.includes('book') || q.includes('appointment') || q.includes('doctor') || q.includes('schedule')) {{
    return "To book an appointment in IPCMS: sign in to your Patient Portal, click 'Appointments' in the sidebar menu, choose your preferred doctor, select an available date and time, and click 'Confirm Booking'.";
  }}
  if (q.includes('bp') || q.includes('blood pressure') || q.includes('hypertension')) {{
    return "Normal blood pressure is generally under 120/80 mmHg. Avoid high sodium foods, exercise regularly, and consult your doctor for proper medical evaluation.";
  }}
  if (q.includes('diabetes') || q.includes('sugar') || q.includes('glucose')) {{
    return "Diabetes symptoms include frequent urination, increased thirst, and fatigue. Maintain a low-sugar diet, stay active, and monitor blood glucose levels regularly.";
  }}
  if (q.includes('medicine') || q.includes('prescription')) {{
    return "You can check active prescriptions and medicine schedules under 'Prescriptions' in your IPCMS Patient Dashboard. Always check with your doctor before altering medications.";
  }}
  return "Hello! I am your IPCMS Voice Assistant. I can help answer health questions, guide you through appointment booking, and explain prescriptions. Please consult a physician for individual medical advice.";
}}

let history = [];
let isRec = false;
let recInst = null;
let inlineAccumulated = '';

function scrollInlineBottom() {{
  const el = document.getElementById('inline-messages');
  if (el) el.scrollTop = el.scrollHeight;
}}

function addInlineMsg(text, role, extra = '') {{
  const container = document.getElementById('inline-messages');
  if (!container) return;
  const time = new Date().toLocaleTimeString([], {{hour:'2-digit', minute:'2-digit'}});
  const row = document.createElement('div');
  row.className = `msg-row ${{role === 'user' ? 'user' : ''}}`;

  const avatar = `<div class="avatar ${{role === 'user' ? 'user' : 'ai'}}">${{role === 'user' ? '👤' : '🤖'}}</div>`;
  const meta   = `<div class="time-stamp">${{time}} · ${{role === 'user' ? 'You' : 'Voice AI'}} ${{extra}}</div>`;
  const bubble = `<div class="bubble ${{role === 'user' ? 'user' : 'ai'}}">${{text}}</div>`;

  row.innerHTML = role === 'user' ? `<div>${{bubble}}${{meta}}</div>${{avatar}}` : `${{avatar}}<div>${{bubble}}${{meta}}</div>`;
  container.appendChild(row);
  scrollInlineBottom();
}}

function speakAloud(text) {{
  if (!window.speechSynthesis) return;
  window.speechSynthesis.cancel();
  const cleanText = text.replace(/[*_`#]/g, '').trim();
  const utt = new SpeechSynthesisUtterance(cleanText);
  utt.rate = 0.94;
  utt.pitch = 1.02;
  const voices = window.speechSynthesis.getVoices();
  const voice = voices.find(v => v.lang === 'en-US' && (v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Zira'))) || voices[0];
  if (voice) utt.voice = voice;
  window.speechSynthesis.speak(utt);
}}

async function processInlineQuery(text) {{
  if (!text.trim()) return;
  addInlineMsg(text, 'user');
  const statusEl = document.getElementById('status-txt');
  if (statusEl) statusEl.textContent = 'AI thinking…';
  history.push({{ role: 'user', parts: [{{ text: text }}] }});

  let replyText = '';

  // 1. Gemini
  if (GEMINI_KEY && GEMINI_KEY.startsWith("AIza")) {{
    try {{
      const endpoint = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${{GEMINI_KEY}}`;
      const resp = await fetch(endpoint, {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json' }},
        body: JSON.stringify({{
          contents: history,
          systemInstruction: {{ parts: [{{ text: SYSTEM_PROMPT_VOICE }}] }},
          generationConfig: {{ maxOutputTokens: 220, temperature: 0.5 }}
        }})
      }});
      if (resp.ok) {{
        const data = await resp.json();
        replyText = data.candidates?.[0]?.content?.parts?.[0]?.text || '';
      }}
    }} catch(e) {{
      console.warn("Gemini error:", e);
    }}
  }}

  // 2. Groq Fallback
  if (!replyText && GROQ_KEY && GROQ_KEY.length > 10) {{
    try {{
      const resp = await fetch('https://api.groq.com/openai/v1/chat/completions', {{
        method: 'POST',
        headers: {{ 'Content-Type': 'application/json', 'Authorization': `Bearer ${{GROQ_KEY}}` }},
        body: JSON.stringify({{
          model: 'llama-3.1-8b-instant',
          messages: [{{ role: 'system', content: SYSTEM_PROMPT_VOICE }}, ...history.map(h => ({{ role: h.role==='model'?'assistant':'user', content: h.parts[0].text }}))]
        }})
      }});
      if (resp.ok) {{
        const data = await resp.json();
        replyText = data.choices?.[0]?.message?.content || '';
      }}
    }} catch(e) {{
      console.warn("Groq error:", e);
    }}
  }}

  // 3. KB Fallback
  if (!replyText) {{
    replyText = getInlineLocalFallback(text);
  }}

  history.push({{ role: 'model', parts: [{{ text: replyText }}] }});
  if (statusEl) statusEl.textContent = 'Speaking response…';

  const waveTag = `<span class="wave-bars"><span></span><span></span><span></span><span></span></span>`;
  addInlineMsg(replyText, 'ai', waveTag);
  speakAloud(replyText);
}}

function sendInlineText() {{
  const inp = document.getElementById('input-field');
  if (!inp) return;
  const val = inp.value.trim();
  if (!val) return;
  inp.value = '';
  processInlineQuery(val);
}}

function quickSend(txt) {{
  processInlineQuery(txt);
}}

function toggleMic() {{
  if (isRec) stopMic();
  else startMic();
}}

function getInlineSRClass() {{
  try {{
    var p = (window.parent && window.parent !== window) ? window.parent : window;
    return p.SpeechRecognition || p.webkitSpeechRecognition || window.SpeechRecognition || window.webkitSpeechRecognition;
  }} catch(e) {{
    return window.SpeechRecognition || window.webkitSpeechRecognition;
  }}
}}

function startMic() {{
  const SR = getInlineSRClass();
  if (!SR) {{
    alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
    return;
  }}

  if (isRec) {{ stopMic(); return; }}

  const btn = document.getElementById('big-mic-btn');
  const statusEl = document.getElementById('status-txt');
  if (statusEl) statusEl.textContent = 'Requesting microphone…';

  /* ── KEY FIX: getUserMedia triggers mic permission dialog inside iframe ── */
  navigator.mediaDevices.getUserMedia({{ audio: true }})
    .then(function(stream) {{
      /* Permission granted — stop the raw stream and hand off to SpeechRecognition */
      stream.getTracks().forEach(t => t.stop());

      try {{
        recInst = new SR();
      }} catch(e) {{
        console.error('Inline SR init error:', e);
        if (statusEl) statusEl.textContent = 'SR init failed';
        return;
      }}

      recInst.lang = 'en-US';
      recInst.continuous = false;
      recInst.interimResults = true;
      recInst.maxAlternatives = 1;
      inlineAccumulated = '';

      let inlineSilenceTimer = null;

      if (btn) btn.classList.add('listening');
      if (statusEl) statusEl.textContent = 'Listening… speak now';
      isRec = true;

      recInst.onresult = (e) => {{
        let interim = '';
        let final   = '';
        for (let i = e.resultIndex; i < e.results.length; i++) {{
          if (e.results[i].isFinal) final += e.results[i][0].transcript + ' ';
          else interim += e.results[i][0].transcript;
        }}
        if (final) inlineAccumulated += final;
        const current = (inlineAccumulated + interim).trim();
        const field = document.getElementById('input-field');
        if (field) field.value = current;

        /* Auto-submit 1.2s after user pauses speaking */
        if (inlineSilenceTimer) clearTimeout(inlineSilenceTimer);
        if (current.length > 0) {{
          inlineSilenceTimer = setTimeout(function() {{
            if (isRec && recInst) {{
              try {{ recInst.stop(); }} catch(err) {{}}
            }}
          }}, 1200);
        }}
      }};

      recInst.onerror = (e) => {{
        console.warn('Inline SR error:', e.error);
        if (inlineSilenceTimer) clearTimeout(inlineSilenceTimer);
        if (e.error === 'no-speech') {{
          if (statusEl) statusEl.textContent = 'No speech detected';
          stopMic();
          return;
        }}
        stopMic();
        if (e.error === 'not-allowed' || e.error === 'service-not-allowed') {{
          if (statusEl) statusEl.textContent = 'Mic blocked — allow access in browser';
        }} else if (statusEl && e.error !== 'aborted') {{
          statusEl.textContent = 'Mic error: ' + e.error;
        }}
      }};

      recInst.onend = () => {{
        if (inlineSilenceTimer) clearTimeout(inlineSilenceTimer);
        const field = document.getElementById('input-field');
        const captured = (inlineAccumulated || (field ? field.value : '')).trim();
        stopMic();
        if (captured && captured.length > 1) {{
          processInlineQuery(captured);
        }}
      }};

      try {{
        recInst.start();
      }} catch(e) {{
        console.error('Failed to start inline SR:', e);
        if (statusEl) statusEl.textContent = 'Failed to start mic';
        stopMic();
      }}
    }})
    .catch(function(err) {{
      console.error('getUserMedia denied:', err);
      if (statusEl) statusEl.textContent = 'Mic denied — click the 🔒 icon in browser bar';
      if (btn) btn.classList.remove('listening');
      alert('Microphone access was denied.\\n\\nPlease:\\n1. Click the lock/camera icon in the browser address bar\\n2. Set Microphone to Allow\\n3. Refresh the page');
    }});
}}

function stopMic() {{
  isRec = false;
  const btn = document.getElementById('big-mic-btn');
  if (btn) btn.classList.remove('listening');
  const statusEl = document.getElementById('status-txt');
  if (statusEl) statusEl.textContent = 'Ready';
  if (recInst) {{
    try {{ recInst.stop(); }} catch(e) {{}}
    recInst = null;
  }}
}}

function setInlineMode(m) {{
  document.getElementById('btn-voice').classList.toggle('active', m === 'voice');
  document.getElementById('btn-text').classList.toggle('active', m === 'text');
  if (m === 'voice') startMic();
}}

function clearInlineChat() {{
  history = [];
  const el = document.getElementById('inline-messages');
  if (el) el.innerHTML = '';
  addInlineMsg('Chat cleared. Click the mic to speak to IPCMS Voice Assistant.', 'ai');
}}

if (window.speechSynthesis) {{ window.speechSynthesis.getVoices(); }}
</script>
</body>
</html>
"""



def render_inline_voice_assistant(height: int = 540):
    """
    Renders an inline Voice Assistant card inside Streamlit page content.
    Uses components.html() which creates a sandboxed iframe.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    groq_key   = os.getenv("GROQ_API_KEY", "").strip()

    html = _build_inline_chatbot_html(gemini_key, groq_key)
    components.html(html, height=height, scrolling=False)
