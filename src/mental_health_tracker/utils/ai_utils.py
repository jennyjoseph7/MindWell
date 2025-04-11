from textblob import TextBlob
import json
import numpy as np
from datetime import datetime, timedelta
from transformers import pipeline
import logging
import google.generativeai as genai
from ..config import GEMINI_API_KEY

# Import the missing MoodEntry model
try:
    from ..models import MoodEntry
except ImportError:
    # For direct execution of this file
    MoodEntry = None
    print("Warning: MoodEntry model not imported properly")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize sentiment and emotion analyzers with error handling
try:
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    emotion_analyzer = pipeline("text-classification", model="j-hartmann/emotion-english-distilroberta-base")
    logger.info("Successfully loaded sentiment and emotion analysis models")
except Exception as e:
    logger.warning(f"Failed to load AI models: {str(e)}. Using TextBlob as fallback.")
    sentiment_analyzer = None
    emotion_analyzer = None

# Configure Gemini API
try:
    genai.configure(api_key=GEMINI_API_KEY)
    model_config = {
        "temperature": 0.7,
        "top_p": 0.8,
        "top_k": 40,
        "max_output_tokens": 1024,
    }
    gemini_model = genai.GenerativeModel("gemini-pro", generation_config=model_config)
    chat_session = gemini_model.start_chat(history=[])
    logger.info("Successfully initialized Gemini model")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    logger.info("Falling back to template-based responses")
    gemini_model = None
    chat_session = None

def analyze_sentiment(text):
    """Analyze sentiment of text using TextBlob and transformers if available"""
    try:
        # Get TextBlob sentiment (always available as a fallback)
        blob = TextBlob(text)
        textblob_score = blob.sentiment.polarity
        
        # Try to get transformers sentiment if available
        if sentiment_analyzer:
            try:
                result = sentiment_analyzer(text)[0]
                transformers_score = float(result['score'])
                if result['label'] == 'NEGATIVE':
                    transformers_score = -transformers_score
                
                # Combine both scores
                final_score = (textblob_score + transformers_score) / 2
            except Exception as e:
                logger.error(f"Error using transformer model: {str(e)}")
                final_score = textblob_score  # Fallback to TextBlob
        else:
            final_score = textblob_score
        
        # Determine label
        if final_score > 0.2:
            return final_score, 'POSITIVE'
        elif final_score < -0.2:
            return final_score, 'NEGATIVE'
        else:
            return final_score, 'NEUTRAL'
    except Exception as e:
        logger.error(f"Critical error in sentiment analysis: {str(e)}")
        return 0.0, 'NEUTRAL'

def analyze_emotions(text):
    """Analyze emotions in text using transformers if available, otherwise return basic emotions"""
    try:
        if emotion_analyzer:
            try:
                results = emotion_analyzer(text)
                if isinstance(results, list) and len(results) > 0:
                    # Handle different formats of results
                    if isinstance(results[0], dict) and 'label' in results[0] and 'score' in results[0]:
                        emotions = {result['label']: float(result['score']) for result in results}
                    else:
                        # Fallback to basic emotion detection
                        emotions = {"joy": 0.5, "sadness": 0.5}
                else:
                    emotions = {"neutral": 1.0}
            except Exception as e:
                logger.error(f"Error using emotion analyzer: {str(e)}")
                # Fallback to basic emotion detection using TextBlob
                emotions = _get_basic_emotions(text)
        else:
            # Fallback to basic emotion detection using TextBlob
            emotions = _get_basic_emotions(text)
            
        return emotions  # Return dictionary directly
    except Exception as e:
        logger.error(f"Critical error in emotion analysis: {str(e)}")
        return {"neutral": 1.0}

def _get_basic_emotions(text):
    """Fallback method to get basic emotions using TextBlob"""
    try:
        blob = TextBlob(text)
        score = blob.sentiment.polarity
        if score > 0.2:
            return {"joy": 0.8, "sadness": 0.2}
        elif score < -0.2:
            return {"joy": 0.2, "sadness": 0.8}
        else:
            return {"joy": 0.5, "sadness": 0.5}
    except Exception:
        return {"neutral": 1.0}

def get_mood_patterns(user_id, db, days=7):
    """Analyze mood patterns over time"""
    try:
        recent_moods = db.session.query(MoodEntry).filter(
            MoodEntry.user_id == user_id,
            MoodEntry.date_created >= datetime.utcnow() - timedelta(days=days)
        ).all()
        
        if not recent_moods:
            return None
            
        # Calculate average mood and trend
        mood_scores = [mood.mood_score for mood in recent_moods]
        avg_mood = sum(mood_scores) / len(mood_scores)
        
        # Calculate trend (positive if improving, negative if declining)
        if len(mood_scores) > 1:
            trend = mood_scores[-1] - mood_scores[0]
        else:
            trend = 0
            
        return {
            "average_mood": round(avg_mood, 2),
            "trend": round(trend, 2),
            "total_entries": len(recent_moods)
        }
    except Exception as e:
        logger.error(f"Error in mood pattern analysis: {str(e)}")
        return None

def generate_chat_response(message, user_context=None):
    """Generate a chat response using Gemini if available, otherwise fall back to template-based responses"""
    try:
        # Try using Gemini first
        if chat_session:
            try:
                # Construct context-aware prompt
                context_prompt = "You are an empathetic AI mental health assistant. "
                if user_context:
                    if 'recent_mood_avg' in user_context:
                        context_prompt += f"The user's average mood has been {user_context['recent_mood_avg']}/5. "
                    if 'mood_trend' in user_context:
                        trend = "improving" if user_context['mood_trend'] > 0 else "declining" if user_context['mood_trend'] < 0 else "stable"
                        context_prompt += f"Their mood has been {trend}. "
                    if 'last_journal_sentiment' in user_context:
                        context_prompt += f"Their recent journal entries show {user_context['last_journal_sentiment']} sentiment. "
                
                # Analyze emotions for additional context
                emotions = analyze_emotions(message)
                if emotions:
                    dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                    context_prompt += f"The user seems to be feeling {dominant_emotion}. "
                
                context_prompt += f"Here's their message: '{message}'. Respond with empathy and support."
                
                # Get response from Gemini
                response = chat_session.send_message(context_prompt)
                return response.text
                
            except Exception as e:
                logger.error(f"Error using Gemini model: {str(e)}")
                # Fall back to template-based response
                return _generate_template_response(message, user_context)
        else:
            # Use template-based response if Gemini is not available
            return _generate_template_response(message, user_context)
            
    except Exception as e:
        logger.error(f"Critical error in chat response generation: {str(e)}")
        return "I'm here to listen and support you. How can I help?"

def _generate_template_response(message, user_context=None):
    """Original template-based response generation as fallback"""
    # Analyze sentiment and emotions for context
    sentiment = analyze_sentiment(message)
    emotions = analyze_emotions(message)
    
    # Define contextual response templates
    context_templates = {
        'emotional_support': {
            'patterns': ['feel', 'feeling', 'sad', 'depressed', 'unhappy', 'lonely', 'alone', 'miserable'],
            'responses': [
                "I can hear that you're experiencing some difficult emotions. It's completely valid to feel this way. Could you tell me more about what's been happening? I'm here to listen and support you through this.",
                "Thank you for sharing your feelings with me. It takes courage to open up. Would you like to explore what might be contributing to these feelings? Sometimes talking things through can help us understand them better.",
                "I'm here to support you through these emotions. Let's take a moment to understand what you're going through. What do you think triggered these feelings?"
            ]
        },
        'anxiety_support': {
            'patterns': ['anxious', 'worried', 'nervous', 'stress', 'stressed', 'overwhelmed', 'panic', 'fear'],
            'responses': [
                "I understand anxiety can be really overwhelming. Let's break this down together. What specific aspects are causing you the most concern right now? We can work on some coping strategies that might help.",
                "Anxiety is a natural response, but I hear that it's becoming difficult to manage. Would you like to try some grounding exercises together? They can help bring you back to the present moment.",
                "When you're feeling anxious, it's important to remember that you're not alone. Can you tell me more about what's making you feel this way? Understanding the triggers can help us develop better coping mechanisms."
            ]
        },
        'positive_reinforcement': {
            'patterns': ['happy', 'good', 'great', 'better', 'proud', 'accomplished', 'excited', 'hopeful'],
            'responses': [
                "It's wonderful to hear you're experiencing positive emotions! These moments are worth celebrating. What specific things have contributed to your good mood? Identifying these can help maintain this positive state.",
                "I'm really glad you're feeling this way! It's important to acknowledge and appreciate these positive moments. Would you like to explore what's working well for you? This can help build on these positive experiences.",
                "Your positive outlook is inspiring! Let's take a moment to reflect on what's going well. Understanding what brings us joy can help us create more such moments in the future."
            ]
        },
        'seeking_help': {
            'patterns': ['help', 'advice', 'suggestion', 'guidance', 'support', 'cope', 'deal'],
            'responses': [
                "I appreciate you reaching out for support. That's a really positive step. Could you tell me more specifically what kind of help you're looking for? This will help me provide more targeted suggestions.",
                "Thank you for trusting me with your concerns. Let's work together to find strategies that work for you. What have you tried so far, and what kind of support would be most helpful right now?",
                "Seeking help is a sign of strength, not weakness. I'm here to support you. Could you share more about what you're hoping to achieve? This will help us develop a more effective approach."
            ]
        }
    }
    
    # Check message context and generate appropriate response
    message_lower = message.lower()
    
    # Unpack sentiment analysis results
    sentiment_score, sentiment_label = sentiment
    
    # Find matching context
    for context, data in context_templates.items():
        if any(pattern in message_lower for pattern in data['patterns']):
            # Get base response
            base_response = np.random.choice(data['responses'])
            
            # Add sentiment-based acknowledgment
            if sentiment_label == "NEGATIVE":
                sentiment_prefix = "I can sense that this is difficult for you. "
            elif sentiment_label == "POSITIVE":
                sentiment_prefix = "I'm glad you're feeling positive about this. "
            else:
                sentiment_prefix = ""
            
            # Add emotion-specific support
            if emotions:
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                if dominant_emotion in ['sadness', 'fear', 'anger']:
                    emotion_support = f"\n\nI notice you're feeling strong {dominant_emotion}. Remember that emotions are temporary and it's okay to feel this way. Would you like to explore some coping strategies specific to dealing with {dominant_emotion}?"
                elif dominant_emotion in ['joy', 'love', 'surprise']:
                    emotion_support = f"\n\nIt's great to see your {dominant_emotion}! These positive emotions can be really energizing. Would you like to discuss ways to maintain this positive state?"
                else:
                    emotion_support = ""
            else:
                emotion_support = ""
            
            return sentiment_prefix + base_response + emotion_support
    
    # If no specific context matches, provide a thoughtful general response
    if sentiment == "POSITIVE":
        return "I appreciate you sharing that with me. Your positive energy comes through in your message. Would you like to explore what's contributing to these good feelings? Understanding what works well for us can help create more positive experiences."
    elif sentiment == "NEGATIVE":
        return "Thank you for opening up to me. I can hear that you're going through something challenging. I'm here to listen and support you. Would you like to talk more about what's troubling you? Sometimes sharing our concerns can help us see them from a new perspective."
    else:
        return "Thank you for sharing your thoughts with me. I'm here to listen and support you in whatever way would be most helpful. Would you like to explore your feelings further or discuss any specific concerns you have?"

def generate_recommendations(emotions_data):
    """Generate personalized recommendations based on detected emotions"""
    try:
        # If emotions_data is a string, parse it
        if isinstance(emotions_data, str):
            emotions = json.loads(emotions_data)
        else:
            emotions = emotions_data
            
        recommendations = []
        
        # Find the dominant emotion(s)
        if not emotions:
            return ["Consider tracking your mood regularly to get personalized recommendations."]
            
        # Sort emotions by intensity
        sorted_emotions = sorted(emotions.items(), key=lambda x: x[1], reverse=True)
        dominant_emotion, intensity = sorted_emotions[0]
        
        # Generate recommendations based on the dominant emotion
        if dominant_emotion == "joy" or dominant_emotion == "happy":
            recommendations = [
                "It's great that you're feeling positive! Consider journaling about what contributed to these good feelings.",
                "Maintain this positive momentum by engaging in activities you enjoy.",
                "Share your positive energy with others who might need support."
            ]
        elif dominant_emotion == "sadness":
            recommendations = [
                "Consider practicing self-compassion exercises when feeling down.",
                "Gentle physical activity like walking or yoga might help lift your mood.",
                "Connecting with a supportive friend or family member could be beneficial.",
                "Try our Music Therapy feature with calming tracks to soothe your mind."
            ]
        elif dominant_emotion == "anger":
            recommendations = [
                "Practice deep breathing exercises to help manage intense feelings.",
                "Consider writing a letter expressing your feelings (without sending it).",
                "Physical exercise can be an effective way to release tension.",
                "Try our Focus Mode to channel your energy productively."
            ]
        elif dominant_emotion == "fear" or dominant_emotion == "anxious":
            recommendations = [
                "Grounding exercises can help when feeling overwhelmed or anxious.",
                "Try the 5-4-3-2-1 technique: identify 5 things you see, 4 things you can touch, 3 things you hear, 2 things you smell, and 1 thing you taste.",
                "Our breathing exercises in the Games section might help reduce anxiety.",
                "Consider scheduling worry time to contain anxious thoughts."
            ]
        elif dominant_emotion == "surprise":
            recommendations = [
                "Take time to process unexpected events or information.",
                "Journaling can help you make sense of surprising developments.",
                "Consider how this surprise aligns with or challenges your expectations."
            ]
        elif dominant_emotion == "disgust":
            recommendations = [
                "Reflect on what triggered these feelings and whether a boundary has been crossed.",
                "Consider if there are actions you can take to address the situation.",
                "Self-care activities might help restore your sense of well-being."
            ]
        else:
            recommendations = [
                "Continue tracking your emotions to receive more personalized recommendations.",
                "Regular journaling can help you identify patterns in your emotional experiences.",
                "Consider trying different features of our app to support your mental well-being."
            ]
            
        # Add some general well-being recommendations
        general_recommendations = [
            "Remember that emotions are temporary and will pass with time.",
            "Practicing mindfulness can help you stay present with your feelings without judgment.",
            "Regular sleep, nutrition, and exercise form the foundation of mental well-being."
        ]
        
        # Combine specific and general recommendations
        recommendations.extend(general_recommendations)
        
        # Randomly select 3 recommendations to avoid overwhelming the user
        if len(recommendations) > 3:
            import random
            recommendations = random.sample(recommendations, 3)
            
        return recommendations
        
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        return ["Continue tracking your emotions for personalized recommendations."]