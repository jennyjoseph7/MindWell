from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_login import current_user, login_required
from ..models import db, ChatHistory, MoodEntry, JournalEntry
from ..utils.ai_utils import analyze_sentiment, analyze_emotions
from ..utils.ai_chat_integration import process_message
from ..utils.crisis_detection import CrisisDetector
from ..utils.crisis_response import CrisisResponseManager
from datetime import datetime
import json
import logging
import asyncio

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
ai_chat_bp = Blueprint('ai_chat', __name__, url_prefix='/ai-chat')

# Initialize crisis detection and response systems
crisis_detector = CrisisDetector()
crisis_response_manager = CrisisResponseManager()

@ai_chat_bp.route('/')
@login_required
def index():
    """Display the AI chat interface."""
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
    
    return render_template('ai/chat.html', messages=formatted_messages)

def run_async(coro):
    """Run an async coroutine in a synchronous context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@ai_chat_bp.route('/send', methods=['POST'])
@login_required
# We're running with CSRF disabled in config instead of using decorators
def send_message():
    """Process an incoming message and generate a response using advanced components."""
    try:
        # Log the request 
        logger.info(f"Received message request from user {current_user.id}")
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
        
        # CRISIS DETECTION - Check for crisis situations first
        user_context = get_user_context(current_user.id)
        print(f"DEBUG: Checking chatbot message for crisis: '{message}'")
        crisis_result = crisis_detector.detect_crisis(
            text=message,
            user_id=str(current_user.id),
            context=user_context
        )
        print(f"DEBUG: Crisis detection result: {crisis_result}")
        
        # Handle crisis response if detected
        crisis_actions = []
        if crisis_result.get('crisis_detected', False):
            print(f"DEBUG: CRISIS DETECTED in chatbot for user {current_user.id}: {crisis_result.get('crisis_level')}")
            logger.warning(f"CRISIS DETECTED for user {current_user.id}: {crisis_result.get('crisis_level')}")
            
            # Get user info for crisis response
            user_info = {
                'id': current_user.id,
                'name': current_user.name,
                'email': current_user.email,
                'phone': getattr(current_user, 'phone', None),
                'emergency_contacts': get_user_emergency_contacts(current_user.id)
            }
            
            # Handle crisis response
            crisis_response = run_async(crisis_response_manager.handle_crisis_response(
                user_id=str(current_user.id),
                crisis_data=crisis_result,
                user_info=user_info
            ))
            
            crisis_actions = crisis_response.get('actions_taken', [])
            logger.warning(f"Crisis response actions taken: {len(crisis_actions)}")
        
        # Process message using advanced components
        try:
            # Process the message through our advanced components
            result = run_async(process_message(
                user_id=str(current_user.id),
                session_id=session_id,
                message=message
            ))
            
            logger.info(f"Advanced processing complete. Escalation level: {result.get('escalation_level', 0)}")
            
            response = result.get('response', "I'm sorry, I couldn't process your message.")
            sentiment_label = result.get('sentiment_label', 'NEUTRAL')
            emotions = result.get('emotions', {"neutral": 1.0})
            
            # Update session_id for frontend to maintain conversation state
            session_id = result.get('session_id')
        except Exception as e:
            logger.error(f"Error in advanced processing: {str(e)}")
            # Fallback to basic sentiment analysis
            sentiment_score, sentiment_label = analyze_sentiment(message)
            emotions = analyze_emotions(message)
            response = "I'm having trouble with advanced processing right now. How else can I help you?"
        
        # Save the conversation to the database
        try:
            chat_entry = ChatHistory(
                user_id=current_user.id,
                message=message,
                response=response,
                sentiment_score=0.5,  # Default value
                sentiment_label=sentiment_label,
                timestamp=datetime.utcnow()
            )
            db.session.add(chat_entry)
            db.session.commit()
            logger.info(f"Chat entry saved successfully for user {current_user.id}")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        
        # Create response with session ID to maintain conversation state
        response_data = {
            'response': response,
            'sentiment_label': sentiment_label,
            'emotions': emotions,
            'session_id': session_id
        }
        
        # Add crisis information if detected
        if crisis_result.get('crisis_detected', False):
            response_data.update({
                'crisis_detected': True,
                'crisis_level': crisis_result.get('crisis_level'),
                'crisis_types': crisis_result.get('crisis_types', []),
                'crisis_actions': crisis_actions,
                'crisis_resources': crisis_detector.get_crisis_resources()
            })
            
            # Override response for crisis situations
            if crisis_result.get('crisis_level') in ['critical', 'high']:
                response_data['response'] = self._get_crisis_response(crisis_result)
        
        return jsonify(response_data)
    
    except Exception as e:
        logger.exception(f"Error in send_message: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your message',
            'response': "I'm having trouble right now. Please try again later."
        }), 500

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

def get_user_emergency_contacts(user_id):
    """Get emergency contacts for a user."""
    try:
        from ..models import EmergencyContact
        contacts = EmergencyContact.query.filter_by(user_id=user_id, is_active=True).all()
        return [
            {
                'name': contact.contact_name,
                'relationship': contact.relationship,
                'phone': contact.phone,
                'email': contact.email,
                'is_primary': contact.is_primary
            }
            for contact in contacts
        ]
    except Exception as e:
        logger.error(f"Error getting emergency contacts: {str(e)}")
        return []

def _get_crisis_response(crisis_result):
    """Get appropriate crisis response message."""
    crisis_level = crisis_result.get('crisis_level', 'medium')
    crisis_types = crisis_result.get('crisis_types', [])
    
    if crisis_level == 'critical':
        return """I'm deeply concerned about what you're sharing with me. Your safety is the most important thing right now. 

I've immediately booked a crisis therapy session for you and notified your emergency contacts. 

Please know that you are not alone:
• Call 988 for the Suicide & Crisis Lifeline (24/7)
• Text HOME to 741741 for Crisis Text Line
• Call 911 for immediate emergencies

Help is available right now. Please reach out to one of these resources immediately."""

    elif crisis_level == 'high':
        return """I'm very concerned about what you're sharing. I've booked an urgent therapy session for you and notified your emergency contacts.

Your mental health and safety are my top priority. Please consider reaching out to:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

You don't have to face this alone. Help is available."""

    else:
        return """I'm concerned about what you're sharing. I've scheduled a wellness check for you and provided some resources.

Please remember that help is available:
• Mental Health America: 1-800-950-6264
• National Alliance on Mental Illness: 1-800-950-NAMI
• Local mental health services

You're taking an important step by reaching out. Please don't hesitate to use these resources.""" 