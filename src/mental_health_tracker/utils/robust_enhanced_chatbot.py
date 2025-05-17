"""
Robust Enhanced Mental Health Chatbot

A simplified but effective mental health chatbot that provides empathetic,
context-aware responses with crisis detection without complex dependencies.
"""

import re
import random
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class RobustEnhancedChatbot:
    """
    Robust enhanced chatbot with mental health focus
    """
    
    def __init__(self):
        # Crisis detection patterns (with flexible matching for common misspellings)
        self.crisis_patterns = [
            r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end(ing)? my life|want to die|wanna die)\b',
            r'\b(no reason to live|better off dead|hopeless|dont want to live)\b',
            r'\b(harm(ing)? myself|hurt(ing)? myself|self harm|cut(ting)? myself|cutting)\b',
            r'\b(can\'t go on|cant go on|give up|no point|cant take it)\b',
            r'\b(worthless|useless|burden|waste of space)\b',
            r'\b(no one cares|alone|isolated|nobody cares)\b'
        ]
        
        # Crisis resources by region
        self.crisis_resources = {
            'IN': {
                'phone': '1800-599-0019 (KIRAN Mental Health Helpline)',
                'text': 'WhatsApp: +91-9820466726 (iCall)',
                'website': 'icallhelpline.org',
                'emergency': '108 (Emergency Services)'
            },
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
                "Please consider reaching out to {phone} - they have trained counselors available 24/7.",
                "You can also contact {text} for immediate support from trained crisis counselors.",
                "If you're in immediate danger, please call emergency services (108/100) or go to your nearest emergency room in India.",
                "For immediate help, call {phone} or reach out to {text} for confidential support."
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
            ]
        }
        
        # Mental health topics
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
                'keywords': ['school', 'college', 'exam', 'test', 'study', 'grades', 'jee', 'neet', 'board', 'entrance'],
                'responses': [
                    "Academic pressure in India can be really overwhelming, especially with competitive exams. You're not alone in feeling this way.",
                    "It sounds like studies are creating a lot of stress for you right now. Many students in India face similar pressures.",
                    "Academic challenges can really affect our mental health. Remember that your worth isn't defined by exam results or grades."
                ]
            },
            'family_pressure': {
                'keywords': ['family', 'parents', 'expectations', 'marriage', 'career', 'tradition'],
                'responses': [
                    "Family expectations can create a lot of pressure. It's common to feel overwhelmed by family dynamics in Indian culture.",
                    "I understand that family pressure can be challenging. Your feelings about family expectations are completely valid.",
                    "Family relationships can be complex, especially with cultural expectations. It's okay to feel conflicted about family matters."
                ]
            },
            'work_life_balance': {
                'keywords': ['work', 'job', 'career', 'balance', 'stress', 'pressure', 'it', 'software'],
                'responses': [
                    "Work-life balance can be challenging, especially in India's competitive job market. Your stress is understandable.",
                    "It sounds like work is creating a lot of pressure for you right now. Many professionals in India face similar challenges.",
                    "Career stress is very common in India's fast-paced work environment. Remember to take care of your mental health."
                ]
            }
        }
        
        # Conversation contexts
        self.conversation_contexts = {}
        self.user_profiles = {}

    async def process_message(self, user_id: str, session_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user message and generate an appropriate response
        """
        try:
            # Get or create conversation context
            context = self._get_or_create_context(user_id, session_id)
            
            # Analyze the message
            analysis = self._analyze_message(message, context)
            
            # Check for crisis indicators
            crisis_level = self._assess_crisis_level(message, analysis, context)
            
            # Generate appropriate response
            response = self._generate_response(message, analysis, context, crisis_level)
            
            # Update context
            self._update_context(context, message, analysis, crisis_level)
            
            return {
                'response': response,
                'sentiment': analysis['sentiment'],
                'emotions': analysis['emotions'],
                'crisis_level': crisis_level,
                'topics': analysis['topics'],
                'session_id': session_id,
                'timestamp': datetime.now().isoformat(),
                'escalation_needed': crisis_level in ['high', 'critical']
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

    def _analyze_message(self, message: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the user's message for sentiment, emotions, and topics"""
        
        # Simple sentiment analysis
        sentiment = self._analyze_sentiment_simple(message)
        
        # Extract emotions
        emotions = self._extect_emotions_simple(message)
        
        # Extract topics
        topics = self._extract_topics(message)
        
        # Detect conversation state
        conversation_state = self._detect_conversation_state(message, context)
        
        return {
            'sentiment': sentiment,
            'emotions': emotions,
            'topics': topics,
            'conversation_state': conversation_state,
            'message_length': len(message.split()),
            'contains_questions': '?' in message,
            'contains_negation': any(word in message.lower() for word in ['not', 'no', 'never', 'can\'t', 'won\'t', 'don\'t'])
        }

    def _analyze_sentiment_simple(self, message: str) -> str:
        """Simple sentiment analysis"""
        message_lower = message.lower()
        
        positive_words = ['happy', 'good', 'great', 'wonderful', 'excited', 'joy', 'love', 'amazing', 'fantastic']
        negative_words = ['sad', 'bad', 'terrible', 'awful', 'hate', 'angry', 'depressed', 'horrible', 'miserable']
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if negative_count > positive_count:
            return 'negative'
        elif positive_count > negative_count:
            return 'positive'
        else:
            return 'neutral'

    def _extect_emotions_simple(self, message: str) -> Dict[str, float]:
        """Simple emotion detection with enhanced mental health vocabulary"""
        emotions = {}
        message_lower = message.lower()
        
        emotion_patterns = {
            'joy': ['happy', 'joy', 'joyful', 'excited', 'thrilled', 'elated', 'cheerful', 'delighted', 'content', 'pleased', 'glad'],
            'sadness': ['sad', 'depressed', 'down', 'blue', 'miserable', 'unhappy', 'gloomy', 'dejected', 'melancholy', 'sorrowful', 'heartbroken', 'crying', 'tears'],
            'anger': ['angry', 'mad', 'furious', 'rage', 'annoyed', 'irritated', 'frustrated', 'outraged', 'hostile', 'bitter', 'resentful', 'aggravated'],
            'fear': ['scared', 'afraid', 'terrified', 'frightened', 'fearful', 'panicked', 'alarmed', 'threatened', 'intimidated'],
            'anxiety': ['anxious', 'worried', 'nervous', 'stressed', 'overwhelmed', 'tense', 'uneasy', 'restless', 'on edge', 'frantic', 'panic'],
            'despair': ['hopeless', 'helpless', 'desperate', 'despairing', 'suicidal', 'sucidal', 'worthless', 'useless', 'pointless', 'meaningless', 'empty'],
            'love': ['love', 'adore', 'care', 'affection', 'romantic', 'loving', 'fond', 'devoted', 'tender'],
            'guilt': ['guilty', 'ashamed', 'regret', 'remorse', 'blame', 'fault', 'sorry'],
            'loneliness': ['lonely', 'alone', 'isolated', 'abandoned', 'rejected', 'disconnected', 'unwanted'],
            'confusion': ['confused', 'lost', 'uncertain', 'unclear', 'bewildered', 'puzzled', 'disoriented'],
            'hope': ['hope', 'hopeful', 'optimistic', 'encouraged', 'positive', 'confident', 'better']
        }
        
        for emotion, keywords in emotion_patterns.items():
            count = sum(1 for keyword in keywords if keyword in message_lower)
            if count > 0:
                # Higher scores for crisis-related emotions
                if emotion == 'despair' and count > 0:
                    emotions[emotion] = min(0.6 + count * 0.2, 0.95)
                else:
                    emotions[emotion] = min(0.3 + count * 0.2, 0.9)
        
        if not emotions:
            emotions['neutral'] = 0.5
        
        return emotions

    def _extract_topics(self, message: str) -> List[str]:
        """Extract mental health topics from the message"""
        topics = []
        message_lower = message.lower()
        
        for topic, data in self.mental_health_topics.items():
            if any(keyword in message_lower for keyword in data['keywords']):
                topics.append(topic)
        
        return topics

    def _detect_conversation_state(self, message: str, context: Dict[str, Any]) -> str:
        """Detect the current state of the conversation"""
        message_lower = message.lower()
        
        # Check for greeting patterns
        greeting_patterns = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening']
        if any(pattern in message_lower for pattern in greeting_patterns) and context.get('message_count', 0) < 3:
            return 'greeting'
        
        # Check for crisis indicators
        if any(re.search(pattern, message_lower) for pattern in self.crisis_patterns):
            return 'crisis'
        
        # Check for closing patterns
        closing_patterns = ['bye', 'goodbye', 'thanks', 'thank you', 'that\'s all', 'done']
        if any(pattern in message_lower for pattern in closing_patterns):
            return 'closing'
        
        return 'active'

    def _assess_crisis_level(self, message: str, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Assess the crisis level based on message content and context"""
        
        # Check for immediate crisis indicators
        crisis_mentions = sum(1 for pattern in self.crisis_patterns if re.search(pattern, message.lower()))
        
        if crisis_mentions > 0:
            context['crisis_mentions'] = context.get('crisis_mentions', 0) + crisis_mentions
            
            # Critical crisis indicators (with flexible matching)
            critical_patterns = [
                r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end(ing)? my life|want to die|wanna die)\b',
                r'\b(harm(ing)? myself|hurt(ing)? myself|cut(ting)? myself|cutting)\b'
            ]
            if any(re.search(pattern, message.lower()) for pattern in critical_patterns):
                return 'critical'
            
            # High crisis indicators
            if context['crisis_mentions'] >= 2 or analysis['sentiment'] == 'negative':
                return 'high'
            
            return 'moderate'
        
        # Check for sustained negative patterns
        if (analysis['sentiment'] == 'negative' and 
            len(context.get('emotional_trajectory', [])) >= 3 and
            all(sent in ['negative'] for sent in context.get('emotional_trajectory', [])[-3:])):
            return 'moderate'
        
        # Low crisis indicators
        if (analysis['sentiment'] == 'negative' or 
            'hopeless' in message.lower() or 
            'worthless' in message.lower()):
            return 'low'
        
        return 'none'

    def _generate_response(self, message: str, analysis: Dict[str, Any], 
                          context: Dict[str, Any], crisis_level: str) -> str:
        """Generate an appropriate response based on analysis and crisis level"""
        
        # Handle crisis situations first
        if crisis_level in ['high', 'critical']:
            return self._generate_crisis_response(message, analysis, context, crisis_level)
        
        # Handle different conversation states
        if analysis['conversation_state'] == 'greeting':
            return random.choice(self.response_templates['greeting'])
        
        if analysis['conversation_state'] == 'closing':
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
                                 context: Dict[str, Any], crisis_level: str) -> str:
        """Generate crisis response with appropriate resources"""
        
        # Immediate crisis response
        immediate_response = random.choice(self.response_templates['crisis_immediate'])
        
        # Get crisis resources (default to India if region not specified)
        region = 'IN'  # Default region - India
        resources = self.crisis_resources.get(region, self.crisis_resources['IN'])
        
        # Add resource information
        resource_response = random.choice(self.response_templates['crisis_resources']).format(
            phone=resources['phone'],
            text=resources['text']
        )
        
        return f"{immediate_response} {resource_response}"

    def _generate_topic_specific_response(self, topic: str, analysis: Dict[str, Any], 
                                        context: Dict[str, Any]) -> str:
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
                                 context: Dict[str, Any]) -> str:
        """Generate response based on detected emotions"""
        
        emotion_responses = {
            'sadness': "I can hear the sadness in your words. It's okay to feel this way, and you don't have to go through it alone.",
            'anger': "I understand you're feeling angry. That's a completely valid emotion, and it's important to acknowledge these feelings.",
            'anxiety': "It sounds like you're feeling anxious. That can be really overwhelming, and I want you to know that help is available.",
            'fear': "I hear that you're feeling scared. Fear can be really difficult to manage, but you're not alone in this.",
            'joy': "I'm glad to hear some positive emotions coming through. It's wonderful when we can experience joy.",
            'love': "It sounds like you're experiencing love or care. That's a beautiful emotion to share."
        }
        
        base_response = emotion_responses.get(emotion, "I can sense strong emotions in what you're sharing.")
        supportive_element = random.choice(self.response_templates['supportive'])
        
        return f"{base_response} {supportive_element}"

    def _generate_sentiment_response(self, analysis: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Generate response based on sentiment analysis"""
        
        sentiment = analysis['sentiment']
        
        if sentiment == 'negative':
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

    def _get_or_create_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """Get existing context or create new one"""
        if session_id not in self.conversation_contexts:
            self.conversation_contexts[session_id] = {
                'user_id': user_id,
                'session_id': session_id,
                'start_time': datetime.now(),
                'message_count': 0,
                'topics_discussed': [],
                'emotional_trajectory': [],
                'crisis_mentions': 0,
                'last_escalation': None
            }
        return self.conversation_contexts[session_id]

    def _update_context(self, context: Dict[str, Any], message: str, 
                       analysis: Dict[str, Any], crisis_level: str):
        """Update conversation context with new information"""
        context['message_count'] += 1
        context['emotional_trajectory'].append(analysis['sentiment'])
        
        # Update topics
        for topic in analysis['topics']:
            if topic not in context['topics_discussed']:
                context['topics_discussed'].append(topic)
        
        # Update crisis tracking
        if crisis_level != 'none':
            context['crisis_mentions'] += 1
            context['last_escalation'] = datetime.now()
        
        # Keep trajectory to reasonable size
        if len(context['emotional_trajectory']) > 10:
            context['emotional_trajectory'] = context['emotional_trajectory'][-10:]

    def get_conversation_summary(self, session_id: str) -> Dict[str, Any]:
        """Get summary of conversation for analysis"""
        if session_id not in self.conversation_contexts:
            return {}
        
        context = self.conversation_contexts[session_id]
        return {
            'session_id': session_id,
            'duration_minutes': (datetime.now() - context['start_time']).total_seconds() / 60,
            'message_count': context['message_count'],
            'topics_discussed': context['topics_discussed'],
            'emotional_trajectory': context['emotional_trajectory'],
            'crisis_mentions': context['crisis_mentions'],
            'last_escalation': context['last_escalation'].isoformat() if context['last_escalation'] else None
        }

    def get_user_profile(self, user_id: str):
        """Get user profile for personalized responses"""
        return self.user_profiles.get(user_id)

    def update_user_profile(self, user_id: str, profile):
        """Update user profile"""
        self.user_profiles[user_id] = profile

# Global instance for use in the application
robust_enhanced_chatbot = RobustEnhancedChatbot()
