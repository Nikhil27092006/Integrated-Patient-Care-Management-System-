"""Cleanup script to remove duplicate function definitions in voice_chatbot.py"""
import sys

with open('voice_chatbot.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the first render_inline_voice_assistant
marker = '\ndef render_inline_voice_assistant('
first = content.find(marker)
second = content.find(marker, first + 1)

print(f'First render_inline at char: {first}')
print(f'Second render_inline at char: {second}')
print(f'Total length: {len(content)}')

if second == -1:
    print('No duplicate found - file already clean!')
    sys.exit(0)

# Truncate at first occurrence, then append clean version
clean = content[:first]
clean += '''

def render_inline_voice_assistant(height: int = 540):
    """
    Renders an inline Voice Assistant card inside Streamlit page content.
    Uses components.html() which creates a sandboxed iframe.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    groq_key   = os.getenv("GROQ_API_KEY", "").strip()

    html = _build_inline_chatbot_html(gemini_key, groq_key)
    components.html(html, height=height, scrolling=False)
'''

with open('voice_chatbot.py', 'w', encoding='utf-8') as f:
    f.write(clean)

print(f'Done. New line count: {clean.count(chr(10))}')
