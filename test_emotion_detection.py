"""
Test Enhanced Emotion Detection
Verify that emotions are properly detected from messages
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from mental_health_tracker.utils.robust_enhanced_chatbot import RobustEnhancedChatbot

# Create chatbot instance
chatbot = RobustEnhancedChatbot()

# Test messages
test_messages = [
    ("i feel sucidal", "Should detect: despair"),
    ("I'm feeling really happy today!", "Should detect: joy"),
    ("I'm so worried and anxious about everything", "Should detect: anxiety"),
    ("I feel so alone and isolated", "Should detect: loneliness"),
    ("I'm angry and frustrated with everything", "Should detect: anger"),
    ("I feel so guilty about what I did", "Should detect: guilt"),
    ("I'm confused and don't know what to do", "Should detect: confusion"),
    ("I'm sad and depressed", "Should detect: sadness"),
    ("There's hope things will get better", "Should detect: hope"),
    ("hello", "Should detect: neutral (no strong emotions)"),
]

print("=" * 70)
print("EMOTION DETECTION TEST")
print("=" * 70)

for message, expected in test_messages:
    emotions = chatbot._extect_emotions_simple(message)
    
    print(f"\n📝 Message: '{message}'")
    print(f"💭 Expected: {expected}")
    print(f"✅ Detected emotions:")
    
    if emotions:
        for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
            percentage = int(score * 100)
            bar = "█" * (percentage // 5)
            print(f"   {emotion.capitalize():15} {percentage:3}% {bar}")
    else:
        print("   (No emotions detected)")
    
    print("-" * 70)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
