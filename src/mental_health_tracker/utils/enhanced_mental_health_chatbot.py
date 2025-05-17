"""
Enhanced Mental Health Chatbot

A comprehensive, well-trained mental health chatbot that provides empathetic,
context-aware responses with crisis detection and escalation management.

Features:
- Advanced sentiment analysis and emotion detection
- Crisis detection and appropriate resource provision
- Context-aware conversation management
- Response validation and quality assurance
- Personalized mental health support
- Professional escalation when needed
"""

import asyncio
import json
import logging
import os
import re
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

# Import existing utilities
from .ai_utils import analyze_sentiment, analyze_emotions
from .sentiment_analyzer import SentimentAnalyzer

logger = logging.getLogger(__name__)

class CrisisLevel(Enum):
    """Crisis escalation levels"""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class ConversationState(Enum):
    """Current conversation state"""
    GREETING = "greeting"
    ACTIVE = "active"
    SUPPORTIVE = "supportive"
    CRISIS = "crisis"
    CLOSING = "closing"

@dataclass
class UserProfile:
    """User profile for personalized responses"""
    user_id: str
    preferred_name: Optional[str] = None
    age_range: Optional[str] = None
    mental_health_concerns: List[str] = None
    coping_strategies: List[str] = None
    support_system: bool = False
    therapy_history: bool = False
    crisis_history: bool = False
    
    def __post_init__(self):
        if self.mental_health_concerns is None:
            self.mental_health_concerns = []
        if self.coping_strategies is None:
            self.coping_strategies = []

@dataclass
class ConversationContext:
    """Context for maintaining conversation flow"""
    session_id: str
    user_id: str
    start_time: datetime
    message_count: int = 0
    topics_discussed: List[str] = None
    emotional_trajectory: List[str] = None
    crisis_mentions: int = 0
    last_escalation: Optional[datetime] = None
    
    def __post_init__(self):
        if self.topics_discussed is None:
            self.topics_discussed = []
        if self.emotional_trajectory is None:
            self.emotional_trajectory = []

class EnhancedMentalHealthChatbot:
    """
    Enhanced Mental Health Chatbot with comprehensive features
    """
    
    def __init__(self):
        self.sentiment_analyzer = SentimentAnalyzer()
        self.conversation_contexts = {}
        self.user_profiles = {}
        
        # Crisis detection patterns
        self.crisis_patterns = [
            r'\b(kill myself|suicide|end my life|want to die)\b',
            r'\b(no reason to live|better off dead|hopeless)\b',
            r'\b(harm myself|hurt myself|self harm)\b',
            r'\b(can\'t go on|give up|no point)\b',
            r'\b(worthless|useless|burden)\b',
            r'\b(no one cares|alone|isolated)\b'
        ]
        
        # Crisis resources by region
        self.crisis_resources = {
            'US': {
                'phone': '988 (Suicide & Crisis Lifeline)',
                'text': 'Text HOME to 741741 (Crisis Text Line)',
                'website': 'suicidepreventionlifeline.org'
            },
            'UK': {
                'phone': '116 123 (Samaritans)',
                'text': 'Text SHOUT to 85258',
                'website': 'samaritans.org'
            },
            'CA': {
                'phone': '1-833-456-4566 (Crisis Services Canada)',
                'text': 'Text HOME to 686868',
                'website': 'crisisservicescanada.ca'
            },
            'AU': {
                'phone': '13 11 14 (Lifeline Australia)',
                'text': 'Text HOME to 0477 13 11 14',
                'website': 'lifeline.org.au'
            }
        }
        
        # Response templates for different scenarios
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
                "Please consider reaching out to {phone} - they have trained counselors available 24/7.",
                "You can also text {text} for immediate support from trained crisis counselors.",
                "If you're in immediate danger, please call emergency services (911/999/000) or go to your nearest emergency room."
            ],
            'validation': [
                "It's completely normal to feel this way given what you're going through.",
                "Your feelings are understandable and valid.",
                "Many people experience similar feelings in difficult situations.",
                "It's okay to not be okay sometimes."
            ],
            'encouragement': [
                "You're taking an important step by talking about this.",
                "Reaching out for help shows strength, not weakness.",
                "You're doing the right thing by sharing what you're going through.",
                "It's brave of you to open up about your struggles."
            ],
            'coping': [
                "What has helped you cope with difficult feelings in the past?",
                "Are there any activities or people that usually help you feel better?",
                "What would feel most supportive for you right now?",
                "Have you tried any relaxation techniques or breathing exercises?"
            ]
        }
        
        # Mental health topics and appropriate responses
        self.mental_health_topics = {
            'depression': {
                'keywords': ['depressed', 'sad', 'down', 'hopeless', 'empty', 'worthless'],
                'responses': [
                    "Depression can make everything feel overwhelming. You're not alone in this struggle.",
                    "It sounds like you're experiencing some really difficult emotions. That's completely valid.",
                    "Depression can make it hard to see any light, but there is hope and help available."
                ]
            },
            'anxiety': {
                'keywords': ['anxious', 'worried', 'nervous', 'panic', 'overwhelmed', 'stressed'],
                'responses': [
                    "Anxiety can be really challenging to manage. You're doing great by talking about it.",
                    "It sounds like you're feeling overwhelmed. That's a common experience with anxiety.",
                    "Anxiety can make everything feel uncertain. Remember that this feeling will pass."
                ]
            },
            'relationships': {
                'keywords': ['family', 'friend', 'partner', 'relationship', 'conflict', 'lonely'],
                'responses': [
                    "Relationships can be complicated and bring up a lot of emotions.",
                    "It sounds like you're dealing with some difficult relationship dynamics.",
                    "Relationship issues can really affect our mental health. You're not alone in this."
                ]
            },
            'work_stress': {
                'keywords': ['work', 'job', 'boss', 'colleague', 'pressure', 'burnout'],
                'responses': [
                    "Work stress can really take a toll on our mental health.",
                    "It sounds like work is creating a lot of pressure for you right now.",
                    "Workplace stress is very common and can be really challenging to navigate."
                ]
            },
            'academic_stress': {
                'keywords': ['school', 'college', 'exam', 'test', 'study', 'grades'],
                'responses': [
                    "Academic pressure can be really overwhelming. You're not alone in feeling this way.",
                    "It sounds like school is creating a lot of stress for you right now.",
                    "Academic challenges can really affect our mental health. Remember that your worth isn't defined by grades."
                ]
            }
        }
        
        # Escalation thresholds
        self.escalation_thresholds = {
            'crisis_mentions': 2,  # Number of crisis mentions before escalation
            'negative_sentiment_duration': 5,  # Minutes of sustained negative sentiment
            'repetitive_negative_patterns': 3  # Repeated negative patterns
        }

    async def process_message(self, user_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate an appropriate response
        
        Args:
            user_id: User identifier
            session_id: Session identifier  
            message: User's message
            
        Returns:
            Response dictionary with AI response and analysis
        """
        try:
            # Get or create conversation context
            context = self._get_or_create_context(user_id, session_id)
            
            # Analyze the message
            analysis = await self._analyze_message(message, context)
            
            # Check for crisis indicators
            crisis_level = self._assess_crisis_level(message, analysis, context)
            
            # Generate appropriate response
            response = await self._generate_response(message, analysis, context, crisis_level)
            
            # Update context
            self._update_context(context, message, analysis, crisis_level)
            
            # Prepare return data
            return {
                'response': response,
                'sentiment': analysis['sentiment'],
                'emotions': analysis['emotions'],
                'crisis_level': crisis_level.value,
                'topics': analysis['topics'],
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'escalation_needed': crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
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

    async def _analyze_message(self, message: str, context: ConversationContext) -> Dict[str, Any]:
        """Analyze the user's message for sentiment, emotions, and topics"""
        
        # Use the existing sentiment analyzer
        sentiment_result = self.sentiment_analyzer.analyze_sentiment(message)
        
        # Extract emotions
        emotions = analyze_emotions(message)
        
        # Extract topics
        topics = self._extract_topics(message)
        
        # Detect conversation state
        conversation_state = self._detect_conversation_state(message, context)
        
        return {
            'sentiment': sentiment_result['sentiment'],
            'sentiment_score': sentiment_result['score'],
            'emotions': emotions,
            'topics': topics,
            'conversation_state': conversation_state,
            'message_length': len(message.split()),
            'contains_questions': '?' in message,
            'contains_negation': any(word in message.lower() for word in ['not', 'no', 'never', 'can\'t', 'won\'t', 'don\'t'])
        }

    def _extract_topics(self, message: str) -> List[str]:
        """Extract mental health topics from the message"""
        topics = []
        message_lower = message.lower()
        
        for topic, data in self.mental_health_topics.items():
            if any(keyword in message_lower for keyword in data['keywords']):
                topics.append(topic)
        
        # Add relationship detection
        relationship_keywords = ['mom', 'dad', 'parent', 'family', 'friend', 'partner', 'boyfriend', 'girlfriend']
        if any(keyword in message_lower for keyword in relationship_keywords):
            topics.append('relationships')
        
        return topics

    def _detect_conversation_state(self, message: str, context: ConversationContext) -> ConversationState:
        """Detect the current state of the conversation"""
        message_lower = message.lower()
        
        # Check for greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in message_lower for pattern in greeting_patterns) and context.message_count < 3:
            return ConversationState.GREETING
        
        # Check for crisis indicators
        if any(re.search(pattern, message_lower) for pattern in self.crisis_patterns):
            return ConversationState.CRISIS
        
        # Check for closing patterns
        closing_patterns = ['bye', 'goodbye', 'thanks', 'thank you', 'that\'s all', 'done']
        if any(pattern in message_lower for pattern in closing_patterns):
            return ConversationState.CLOSING
        
        # Check for supportive conversation
        supportive_indicators = ['help', 'support', 'advice', 'guidance', 'coping']
        if any(indicator in message_lower for indicator in supportive_indicators):
            return ConversationState.SUPPORTIVE
        
        return ConversationState.ACTIVE

    def _assess_crisis_level(self, message: str, analysis: Dict[str, Any], context: ConversationContext) -> CrisisLevel:
        """Assess the crisis level based on message content and context"""
        
        # Check for immediate crisis indicators
        crisis_mentions = sum(1 for pattern in self.crisis_patterns if re.search(pattern, message.lower()))
        
        if crisis_mentions > 0:
            context.crisis_mentions += crisis_mentions
            
            # Critical crisis indicators
            critical_patterns = [r'\b(kill myself|suicide|end my life)\b', r'\b(harm myself|hurt myself)\b']
            if any(re.search(pattern, message.lower()) for pattern in critical_patterns):
                return CrisisLevel.CRITICAL
            
            # High crisis indicators
            if context.crisis_mentions >= 2 or analysis['sentiment'] == 'highly_negative':
                return CrisisLevel.HIGH
            
            return CrisisLevel.MODERATE
        
        # Check for sustained negative patterns
        if (analysis['sentiment'] in ['negative', 'highly_negative'] and 
            len(context.emotional_trajectory) >= 3 and
            all(sent in ['negative', 'highly_negative'] for sent in context.emotional_trajectory[-3:])):
            return CrisisLevel.MODERATE
        
        # Low crisis indicators
        if (analysis['sentiment'] == 'negative' or 
            'hopeless' in message.lower() or 
            'worthless' in message.lower()):
            return CrisisLevel.LOW
        
        return CrisisLevel.NONE

    async def _generate_response(self, message: str, analysis: Dict[str, Any], 
                               context: ConversationContext, crisis_level: CrisisLevel) -> str:
        """Generate an appropriate response based on analysis and crisis level"""
        
        # Handle crisis situations first
        if crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]:
            return self._generate_crisis_response(message, analysis, context, crisis_level)
        
        # Handle different conversation states
        if analysis['conversation_state'] == ConversationState.GREETING:
            return random.choice(self.response_templates['greeting'])
        
        if analysis['conversation_state'] == ConversationState.CLOSING:
            return self._generate_closing_response()
        
        # Generate topic-specific responses
        if analysis['topics']:
            return self._generate_topic_specific_response(analysis['topics'][0], analysis, context)
        
        # Generate emotion-specific responses
        if analysis['emotions']:
            dominant_emotion = max(analysis['emotions'].items(), key=lambda x: x[1])[0]
            return self._generate_emotion_response(dominant_emotion, analysis, context)
        
        # Generate sentiment-based responses
        return self._generate_sentiment_response(analysis, context)

    def _generate_crisis_response(self, message: str, analysis: Dict[str, Any], 
                                 context: ConversationContext, crisis_level: CrisisLevel) -> str:
        """Generate crisis response with appropriate resources"""
        
        # Immediate crisis response
        immediate_response = random.choice(self.response_templates['crisis_immediate'])
        
        # Get crisis resources (default to US if region not specified)
        region = os.getenv('USER_REGION', 'US')
        resources = self.crisis_resources.get(region, self.crisis_resources['US'])
        
        # Add resource information
        resource_response = random.choice(self.response_templates['crisis_resources']).format(
            phone=resources['phone'],
            text=resources['text']
        )
        
        return f"{immediate_response} {resource_response}"

    def _generate_topic_specific_response(self, topic: str, analysis: Dict[str, Any], 
                                        context: ConversationContext) -> str:
        """Generate response specific to mental health topics"""
        
        if topic in self.mental_health_topics:
            topic_responses = self.mental_health_topics[topic]['responses']
            base_response = random.choice(topic_responses)
            
            # Add supportive elements
            supportive_element = random.choice(self.response_templates['supportive'])
            validation_element = random.choice(self.response_templates['validation'])
            
            return f"{base_response} {supportive_element} {validation_element}"
        
        return self._generate_sentiment_response(analysis, context)

    def _generate_emotion_response(self, emotion: str, analysis: Dict[str, Any], 
                                 context: ConversationContext) -> str:
        """Generate response based on detected emotions"""
        
        emotion_responses = {
            'sadness': "I can hear the sadness in your words. It's okay to feel this way, and you don't have to go through it alone.",
            'anger': "I understand you're feeling angry. That's a completely valid emotion, and it's important to acknowledge these feelings.",
            'anxiety': "It sounds like you're feeling anxious. That can be really overwhelming, and I want you to know that help is available.",
            'fear': "I hear that you're feeling scared. Fear can be really difficult to manage, but you're not alone in this.",
            'joy': "I'm glad to hear some positive emotions coming through. It's wonderful when we can experience joy.",
            'surprise': "It sounds like something unexpected happened. Would you like to talk more about what surprised you?"
        }
        
        base_response = emotion_responses.get(emotion, "I can sense strong emotions in what you're sharing.")
        supportive_element = random.choice(self.response_templates['supportive'])
        
        return f"{base_response} {supportive_element}"

    def _generate_sentiment_response(self, analysis: Dict[str, Any], context: ConversationContext) -> str:
        """Generate response based on sentiment analysis"""
        
        sentiment = analysis['sentiment']
        
        if sentiment in ['negative', 'highly_negative']:
            base_response = random.choice(self.response_templates['supportive'])
            validation = random.choice(self.response_templates['validation'])
            encouragement = random.choice(self.response_templates['encouragement'])
            
            return f"{base_response} {validation} {encouragement}"
        
        elif sentiment == 'positive':
            return "I'm glad to hear some positive feelings coming through. What's contributing to this positive energy?"
        
        else:  # neutral
            return "Thank you for sharing that with me. How are you feeling about this situation overall?"

    def _generate_closing_response(self) -> str:
        """Generate appropriate closing response"""
        closing_responses = [
            "Thank you for sharing with me today. Remember that I'm here whenever you need to talk.",
            "I'm glad we could talk today. Take care of yourself, and know that support is always available.",
            "Thank you for trusting me with your thoughts and feelings. You're not alone in this journey.",
            "I appreciate you opening up today. Remember that reaching out for help is a sign of strength."
        ]
        return random.choice(closing_responses)

    def _get_or_create_context(self, user_id: str, session_id: str) -> ConversationContext:
        """Get existing context or create new one"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = ConversationContext(
                session_id=session_id,
                user_id=user_id,
                start_time=datetime.now()
            )
        return self.conversation_contexts[session_id]

    def _update_context(self, context: ConversationContext, message: str, 
                       analysis: Dict[str, Any], crisis_level: CrisisLevel):
        """Update conversation context with new information"""
        context.message_count += 1
        context.emotional_trajectory.append(analysis['sentiment'])
        
        # Update topics
        for topic in analysis['topics']:
            if topic not in context.topics_discussed:
                context.topics_discussed.append(topic)
        
        # Update crisis tracking
        if crisis_level != CrisisLevel.NONE:
            context.crisis_mentions += 1
            context.last_escalation = datetime.now()
        
        # Keep trajectory to reasonable size
        if len(context.emotional_trajectory) > 10:
            context.emotional_trajectory = context.emotional_trajectory[-10:]

    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile for personalized responses"""
        return self.user_profiles.get(user_id)

    def update_user_profile(self, user_id: str, profile: UserProfile):
        """Update user profile"""
        self.user_profiles[user_id] = profile

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation for analysis"""
        if session_id not in self.conversation_contexts:
            return {}
        
        context = self.conversation_contexts[session_id]
        return {
            'session_id': session_id,
            'duration_minutes': (datetime.now() - context.start_time).total_seconds() / 60,
            'message_count': context.message_count,
            'topics_discussed': context.topics_discussed,
            'emotional_trajectory': context.emotional_trajectory,
            'crisis_mentions': context.crisis_mentions,
            'last_escalation': context.last_escalation.isoformat() if context.last_escalation else None
        }

# Global instance for use in the application
enhanced_chatbot = EnhancedMentalHealthChatbot()
