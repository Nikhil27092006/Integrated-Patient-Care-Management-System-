# Simple update script
import sys
sys.path.insert(0, '.')

try:
    # Read the file
    with open('pages/admin_dashboard.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the line with "elif page == "ai_care":"
    target = 'elif page == "ai_care":'
    idx = content.find(target)

    if idx > 0:
        print(f"Found target at index {idx}")
        # Find what's before it
        before = content[idx-100:idx]
        print(f"Content before: {repr(before[-50:])}")
    else:
        print("Target not found!")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
