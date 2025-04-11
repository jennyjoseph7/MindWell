from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from flask_login import current_user, login_required
from ..models import db, ChatHistory, MoodEntry, JournalEntry
from ..utils.ai_utils import analyze_sentiment, analyze_emotions, generate_chat_response
from datetime import datetime
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
ai_chat_bp = Blueprint('ai_chat', __name__, url_prefix='/ai-chat')

@ai_chat_bp.route('/')
@login_required
def index():
    """Display the AI chat interface."""
    # Get recent chat history
    chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()
    
    return render_template('ai/chat.html', messages=chat_history)

@ai_chat_bp.route('/new')
@login_required
def new_chat():
    """Start a new chat session."""
    return redirect(url_for('ai_chat.index'))

@ai_chat_bp.route('/send', methods=['POST'])
@login_required
# We're running with CSRF disabled in config instead of using decorators
def send_message():
    """Process an incoming message and generate a response."""
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
        
        # Analyze sentiment and emotions
        try:
            sentiment_score, sentiment_label = analyze_sentiment(message)
            logger.debug(f"Sentiment analysis: {sentiment_label} ({sentiment_score})")
        except Exception as e:
            logger.error(f"Sentiment analysis error: {str(e)}")
            sentiment_score, sentiment_label = 0, "NEUTRAL"
            
        try:
            emotions = analyze_emotions(message)
            logger.debug(f"Emotion analysis: {emotions}")
        except Exception as e:
            logger.error(f"Emotion analysis error: {str(e)}")
            emotions = {"neutral": 1.0}
        
        # Collect user context for personalized response
        user_context = get_user_context(current_user.id)
        
        # Generate AI response
        try:
            response = generate_chat_response(message, user_context)
            logger.debug(f"Generated response: {response[:50]}...")
        except Exception as e:
            logger.error(f"Response generation error: {str(e)}")
            response = "I'm having trouble processing your request right now. Could you try again?"
        
        # Save the conversation to the database
        try:
            chat_entry = ChatHistory(
                user_id=current_user.id,
                user_message=message,
                ai_response=response,
                sentiment=sentiment_label,
                emotions=json.dumps(emotions) if isinstance(emotions, dict) else emotions,
                timestamp=datetime.utcnow()
            )
            
            db.session.add(chat_entry)
            db.session.commit()
            logger.info(f"Chat entry saved successfully for user {current_user.id}")
        except Exception as e:
            logger.error(f"Database error: {str(e)}")
            db.session.rollback()
        
        return jsonify({
            'response': response,
            'sentiment': sentiment_label,
            'emotions': emotions
        })
    
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