"""
Test Crisis Detection
Quick script to verify crisis detection patterns are working
"""

import re

# Crisis patterns from robust_enhanced_chatbot.py (UPDATED)
crisis_patterns = [
    r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end my life|want to die|wanna die)\b',
    r'\b(no reason to live|better off dead|hopeless|dont want to live)\b',
    r'\b(harm myself|hurt myself|self harm|cut myself|cutting)\b',
    r'\b(can\'t go on|cant go on|give up|no point|cant take it)\b',
    r'\b(worthless|useless|burden|waste of space)\b',
    r'\b(no one cares|alone|isolated|nobody cares)\b'
]

# Test messages
test_messages = [
    "i feel sucidal",  # Common misspelling
    "i feel suicidal",  # Correct spelling
    "I want to die",
    "I feel hopeless",
    "I'm thinking about ending my life",
    "I'm feeling happy today",  # Should not trigger
    "just having a normal day",  # Should not trigger
    "i feel suicidel",  # Another misspelling variant
]

print("=" * 60)
print("CRISIS DETECTION TEST")
print("=" * 60)

for message in test_messages:
    message_lower = message.lower()
    crisis_detected = False
    
    for pattern in crisis_patterns:
        if re.search(pattern, message_lower):
            crisis_detected = True
            break
    
    status = "🚨 CRISIS DETECTED" if crisis_detected else "✅ Normal"
    print(f"\n{status}")
    print(f"Message: '{message}'")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
