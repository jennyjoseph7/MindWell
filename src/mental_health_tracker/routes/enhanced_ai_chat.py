"""
Enhanced AI Chat Routes

This module provides improved AI chat functionality with:
- Enhanced mental health chatbot
- Crisis detection and escalation
- Better response quality
- Context-aware conversations
"""

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_login import current_user, login_required
from ..models import db, ChatHistory, MoodEntry, JournalEntry
# Import will be done inside functions to avoid circular imports
from datetime import datetime
import json
import logging
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
enhanced_ai_chat_bp = Blueprint('enhanced_ai_chat', __name__, url_prefix='/enhanced-ai-chat')

@enhanced_ai_chat_bp.route('/')
@login_required
def index():
    """Display the enhanced AI chat interface."""
    # Get recent chat history and format it for the template
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(20).all()
    
    # Format chat history for the template
    formatted_messages = []
    for chat in reversed(chat_history):  # Reverse to get chronological order
        # Add user message
        if chat.message:
            formatted_messages.append({
                'content': chat.message,
                'is_user': True,
                'timestamp': chat.timestamp
            })
        # Add assistant response
        if chat.response:
            formatted_messages.append({
                'content': chat.response,
                'is_user': False,
                'timestamp': chat.timestamp
            })
    
    return render_template('ai/enhanced_chat.html', messages=formatted_messages)

def run_async(coro):
    """Run an async coroutine in a synchronous context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@enhanced_ai_chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    """Process an incoming message using the enhanced chatbot."""
    try:
        # Log the request 
        logger.info(f"Enhanced chatbot - Received message request from user {current_user.id}")
        logger.debug(f"Headers: {request.headers}")
        
        data = request.get_json()
        if not data:
            logger.error("No JSON data received in request")
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract the message
        message = data.get('message', '').strip()
        if not message:
            logger.error("Empty message received")
            return jsonify({'error': 'Message is required'}), 400
        
        logger.info(f"Processing message from user {current_user.id}: {message[:30]}{'...' if len(message) > 30 else ''}")
        
        # Get session ID from request or generate new one
        session_id = data.get('session_id', None)
        if not session_id:
            session_id = f"session_{current_user.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Process message using enhanced chatbot
        try:
            # Use the robust enhanced chatbot (no complex dependencies)
            from ..utils.robust_enhanced_chatbot import robust_enhanced_chatbot
            chatbot = robust_enhanced_chatbot
            
            result = run_async(chatbot.process_message(
                user_id=str(current_user.id),
                session_id=session_id,
                message=message
            ))
            
            logger.info(f"Enhanced processing complete. Crisis level: {result.get('crisis_level', 'none')}")
            
            # Extract response data
            response = result.get('response', "I'm sorry, I couldn't process your message.")
            sentiment = result.get('sentiment', 'neutral')
            emotions = result.get('emotions', {})
            topics = result.get('topics', [])
            crisis_level = result.get('crisis_level', 'none')
            escalation_needed = result.get('escalation_needed', False)
            
            # Log and handle crisis situations
            if crisis_level in ['high', 'critical']:
                logger.warning(f"CRISIS DETECTED for user {current_user.id}: {crisis_level}")
                # Prepend crisis resources to response
                crisis_header = "\n\n⚠️ **CRISIS SUPPORT RESOURCES** ⚠️\n"
                crisis_resources_text = (
                    "🇮🇳 **India Crisis Helplines:**\n"
                    "• KIRAN Mental Health: 1800-599-0019 (24/7)\n"
                    "• Vandrevala Foundation: 1860-2662-345\n"
                    "• iCall: +91-9152987821 (WhatsApp)\n"
                    "• Emergency: 108 / 100\n\n"
                )
                response = crisis_header + crisis_resources_text + response
                
                # AUTOMATIC CRISIS RESPONSE - Book therapy & notify emergency contacts
                try:
                    from ..utils.crisis_response import CrisisResponseManager
                    from ..models import EmergencyContact
                    
                    crisis_manager = CrisisResponseManager()
                    
                    # Get emergency contacts
                    emergency_contacts_db = EmergencyContact.query.filter_by(
                        user_id=current_user.id, 
                        is_active=True
                    ).all()
                    
                    emergency_contacts = [
                        {
                            'name': contact.contact_name,
                            'relationship': contact.relationship,
                            'phone': contact.phone,
                            'email': contact.email,
                            'is_primary': contact.is_primary
                        }
                        for contact in emergency_contacts_db
                    ]
                    
                    user_info = {
                        'id': current_user.id,
                        'name': current_user.name,
                        'email': current_user.email,
                        'phone': getattr(current_user, 'phone', None),
                        'emergency_contacts': emergency_contacts
                    }
                    
                    crisis_data = {
                        'crisis_detected': True,
                        'crisis_level': crisis_level,
                        'crisis_types': ['chatbot', 'conversation'],
                        'detected_in': 'chatbot'
                    }
                    
                    crisis_response = run_async(crisis_manager.handle_crisis_response(
                        str(current_user.id), crisis_data, user_info
                    ))
                    
                    if crisis_response.get('crisis_handled'):
                        response += "\n\n🚨 **AUTOMATIC ACTIONS TAKEN:**\n• Emergency therapy session booked\n• Your emergency contacts have been notified\n"
                        logger.warning(f"Crisis response activated for user {current_user.id} from chatbot")
                except Exception as e:
                    logger.error(f"Error in automatic crisis response from chatbot: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error in enhanced processing: {str(e)}")
            # Fallback response
            response = "I'm having trouble with advanced processing right now. How else can I help you?"
            sentiment = 'neutral'
            emotions = {}
            topics = []
            crisis_level = 'none'
            escalation_needed = False
        
        # Save the conversation to the database
        try:
            chat_entry = ChatHistory(
                user_id=current_user.id,
                message=message,
                response=response,
                sentiment_score=0.5,  # Default value
                sentiment_label=sentiment.upper(),
                timestamp=datetime.utcnow()
            )
            db.session.add(chat_entry)
            db.session.commit()
            logger.info(f"Chat entry saved successfully for user {current_user.id}")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        
        # Create response with enhanced data
        return jsonify({
            'response': response,
            'sentiment': sentiment,
            'emotions': emotions,
            'topics': topics,
            'crisis_level': crisis_level,
            'escalation_needed': escalation_needed,
            'session_id': session_id,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        logger.exception(f"Error in enhanced send_message: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message',
            'response': "I'm having trouble right now. Please try again later."
        }), 500

@enhanced_ai_chat_bp.route('/crisis-resources')
@login_required
def crisis_resources():
    """Provide crisis resources page"""
    return render_template('ai/crisis_resources.html')

@enhanced_ai_chat_bp.route('/conversation-summary/<session_id>')
@login_required
def conversation_summary(session_id):
    """Get conversation summary for analysis"""
    try:
        from ..utils.robust_enhanced_chatbot import robust_enhanced_chatbot
        summary = robust_enhanced_chatbot.get_conversation_summary(session_id)
        return jsonify(summary)
    except Exception as e:
        logger.error(f"Error getting conversation summary: {str(e)}")
        return jsonify({'error': 'Could not retrieve conversation summary'}), 500

@enhanced_ai_chat_bp.route('/user-profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    """Get or update user profile for personalized responses"""
    if request.method == 'GET':
        try:
            from ..utils.robust_enhanced_chatbot import robust_enhanced_chatbot
            profile = robust_enhanced_chatbot.get_user_profile(str(current_user.id))
            if profile:
                return jsonify({
                    'preferred_name': getattr(profile, 'preferred_name', None),
                    'age_range': getattr(profile, 'age_range', None),
                    'mental_health_concerns': getattr(profile, 'mental_health_concerns', []),
                    'coping_strategies': getattr(profile, 'coping_strategies', []),
                    'support_system': getattr(profile, 'support_system', False),
                    'therapy_history': getattr(profile, 'therapy_history', False),
                    'crisis_history': getattr(profile, 'crisis_history', False)
                })
            return jsonify({})
        except Exception as e:
            logger.error(f"Error getting user profile: {str(e)}")
            return jsonify({'error': 'Could not retrieve profile'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            from ..utils.robust_enhanced_chatbot import robust_enhanced_chatbot
            
            # Create a simple profile object
            class SimpleProfile:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)
            
            profile = SimpleProfile(
                user_id=str(current_user.id),
                preferred_name=data.get('preferred_name'),
                age_range=data.get('age_range'),
                mental_health_concerns=data.get('mental_health_concerns', []),
                coping_strategies=data.get('coping_strategies', []),
                support_system=data.get('support_system', False),
                therapy_history=data.get('therapy_history', False),
                crisis_history=data.get('crisis_history', False)
            )
            
            robust_enhanced_chatbot.update_user_profile(str(current_user.id), profile)
            return jsonify({'success': True, 'message': 'Profile updated successfully'})
            
        except Exception as e:
            logger.error(f"Error updating user profile: {str(e)}")
            return jsonify({'error': 'Could not update profile'}), 500

def get_user_context(user_id):
    """Gather context about the user for personalized responses."""
    context = {}
    
    # Get recent mood entries
    moods = MoodEntry.query.filter_by(user_id=user_id).order_by(MoodEntry.date_created.desc()).limit(5).all()
    if moods:
        avg_mood = sum(m.mood_score for m in moods) / len(moods)
        context['recent_mood_avg'] = avg_mood
        context['current_mood'] = moods[0].mood_score
    
    # Get recent journal entries
    journals = JournalEntry.query.filter_by(user_id=user_id).order_by(JournalEntry.date_created.desc()).limit(3).all()
    if journals:
        context['has_journal'] = True
        context['recent_journal_topic'] = journals[0].title
    
    return context
