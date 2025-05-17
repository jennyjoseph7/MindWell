"""
Simple Enhanced Chatbot Fallback

A simplified version of the enhanced chatbot that can be used as a fallback
if the full enhanced chatbot has import issues.
"""

import re
import random
from datetime import datetime
from typing import Dict, Any, List

class SimpleEnhancedChatbot:
    """
    Simple enhanced chatbot with basic mental health support
    """
    
    def __init__(self):
        # Crisis detection patterns
        self.crisis_patterns = [
            r'\b(kill myself|suicide|end my life|want to die)\b',
            r'\b(no reason to live|better off dead|hopeless)\b',
            r'\b(harm myself|hurt myself|self harm)\b',
            r'\b(can\'t go on|give up|no point)\b',
            r'\b(worthless|useless|burden)\b',
            r'\b(no one cares|alone|isolated)\b'
        ]
        
        # Response templates
        self.response_templates = {
            'greeting': [
                "Hello! I'm here to listen and support you. How are you feeling today?",
                "Hi there! I'm your mental health companion. What's on your mind?",
                "Hello! I'm here to provide a safe space for you to share. How can I help you today?"
            ],
            'supportive': [
                "I hear you, and I want you to know that your feelings are valid.",
                "Thank you for sharing that with me. It takes courage to open up.",
                "I'm here with you through this. You're not alone in feeling this way.",
                "That sounds really difficult. I'm glad you're reaching out for support."
            ],
            'crisis_immediate': [
                "I'm very concerned about what you're telling me. Your safety is the most important thing right now.",
                "I hear that you're in a lot of pain. Please know that help is available and you don't have to go through this alone.",
                "What you're experiencing sounds overwhelming. I want to make sure you get the support you need right now."
            ],
            'crisis_resources': [
                "Please consider reaching out to 988 (US Suicide & Crisis Lifeline) - they have trained counselors available 24/7.",
                "You can also text HOME to 741741 for immediate support from trained crisis counselors.",
                "If you're in immediate danger, please call emergency services (911/999/000) or go to your nearest emergency room."
            ]
        }
        
        # Mental health topics
        self.mental_health_topics = {
            'depression': ['depressed', 'sad', 'down', 'hopeless', 'empty', 'worthless'],
            'anxiety': ['anxious', 'worried', 'nervous', 'panic', 'overwhelmed', 'stressed'],
            'relationships': ['family', 'friend', 'partner', 'relationship', 'conflict', 'lonely'],
            'work_stress': ['work', 'job', 'boss', 'colleague', 'pressure', 'burnout'],
            'academic_stress': ['school', 'college', 'exam', 'test', 'study', 'grades']
        }

    async def process_message(self, user_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate an appropriate response
        """
        try:
            # Check for crisis indicators
            crisis_level = self._assess_crisis_level(message)
            
            # Generate response
            response = self._generate_response(message, crisis_level)
            
            # Analyze sentiment (simple)
            sentiment = self._analyze_sentiment_simple(message)
            
            # Extract topics
            topics = self._extract_topics(message)
            
            return {
                'response': response,
                'sentiment': sentiment,
                'emotions': {'neutral': 0.5},  # Simple fallback
                'crisis_level': crisis_level,
                'topics': topics,
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'escalation_needed': crisis_level in ['high', 'critical']
            }
            
        except Exception as e:
            return {
                'response': "I'm having trouble processing your message right now. Please try again, and know that I'm here to support you.",
                'sentiment': 'neutral',
                'emotions': {},
                'crisis_level': 'none',
                'topics': [],
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'escalation_needed': False,
                'error': str(e)
            }

    def _assess_crisis_level(self, message: str) -> str:
        """Assess crisis level based on message content"""
        message_lower = message.lower()
        
        # Check for crisis patterns
        for pattern in self.crisis_patterns:
            if re.search(pattern, message_lower):
                # Critical crisis indicators
                if any(phrase in message_lower for phrase in ['kill myself', 'suicide', 'end my life', 'harm myself']):
                    return 'critical'
                # High crisis indicators
                elif any(phrase in message_lower for phrase in ['no reason to live', 'better off dead', 'hopeless', 'worthless']):
                    return 'high'
                else:
                    return 'moderate'
        
        # Check for negative sentiment
        negative_words = ['sad', 'depressed', 'anxious', 'worried', 'stressed', 'overwhelmed', 'lonely']
        if any(word in message_lower for word in negative_words):
            return 'low'
        
        return 'none'

    def _generate_response(self, message: str, crisis_level: str) -> str:
        """Generate appropriate response based on crisis level"""
        
        if crisis_level in ['high', 'critical']:
            immediate = random.choice(self.response_templates['crisis_immediate'])
            resources = random.choice(self.response_templates['crisis_resources'])
            return f"{immediate} {resources}"
        
        elif crisis_level == 'moderate':
            supportive = random.choice(self.response_templates['supportive'])
            return f"{supportive} Would you like to talk more about what's troubling you?"
        
        elif crisis_level == 'low':
            supportive = random.choice(self.response_templates['supportive'])
            return f"{supportive} What would feel most supportive for you right now?"
        
        else:
            # Check for greeting
            greeting_words = ['hello', 'hi', 'hey', 'good morning', 'good afternoon']
            if any(word in message.lower() for word in greeting_words):
                return random.choice(self.response_templates['greeting'])
            
            # Default supportive response
            return random.choice(self.response_templates['supportive'])

    def _analyze_sentiment_simple(self, message: str) -> str:
        """Simple sentiment analysis"""
        message_lower = message.lower()
        
        positive_words = ['happy', 'good', 'great', 'wonderful', 'excited', 'joy', 'love']
        negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'angry', 'depressed']
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'

    def _extract_topics(self, message: str) -> List[str]:
        """Extract mental health topics from message"""
        topics = []
        message_lower = message.lower()
        
        for topic, keywords in self.mental_health_topics.items():
            if any(keyword in message_lower for keyword in keywords):
                topics.append(topic)
        
        return topics

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get conversation summary"""
        return {
            'session_id': session_id,
            'message_count': 0,
            'topics_discussed': [],
            'emotional_trajectory': [],
            'crisis_mentions': 0
        }

    def get_user_profile(self, user_id: str):
        """Get user profile"""
        return None

    def update_user_profile(self, user_id: str, profile):
        """Update user profile"""
        pass

# Global instance
simple_enhanced_chatbot = SimpleEnhancedChatbot()
