from textblob import TextBlob
import json
import numpy as np
import random
from datetime import datetime, timedelta
from transformers import pipeline
import logging
import google.generativeai as genai
from ..config import GEMINI_API_KEY
from .sentiment_analyzer import SentimentAnalyzer

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

# Initialize sentiment analyzer and other pipelines
try:
    sentiment_analyzer = SentimentAnalyzer()
    logger.info("Successfully initialized sentiment analyzer")
except Exception as e:
    logger.error(f"Error initializing sentiment analyzer: {str(e)}")
    sentiment_analyzer = None

# Initialize Gemini
try:
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        chat_session = genai.GenerativeModel("gemini-pro")
        logger.info("Successfully initialized Google Gemini AI")
    else:
        logger.warning("No Gemini API key found. Fallback responses will be used.")
        chat_session = None
except Exception as e:
    logger.error(f"Error initializing Gemini API: {str(e)}")
    chat_session = None


def analyze_sentiment(text):
    """
    Determine the sentiment of the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        tuple: A tuple of (sentiment_score, sentiment_label)
    """
    try:
        if sentiment_analyzer:
            # Use our advanced sentiment analyzer
            result = sentiment_analyzer.analyze_sentiment(text)
            sentiment_label = result["sentiment"]
            sentiment_score = result["score"]
            return sentiment_score, sentiment_label
        else:
            # Fallback to TextBlob
            blob = TextBlob(text)
            score = blob.sentiment.polarity
            
            if score > 0.3:
                return 0.7, "positive"
            elif score < -0.3:
                return 0.7, "negative"
            else:
                return 0.5, "neutral"
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {str(e)}")
        return 0.5, "neutral"


def analyze_emotions(text):
    """
    Identify emotions in the given text.
    
    Args:
        text (str): The text to analyze
        
    Returns:
        dict: A dictionary of emotions and their scores
    """
    try:
        if sentiment_analyzer:
            # Use our sentiment analyzer to detect emotions
            result = sentiment_analyzer.analyze_sentiment(text)
            detected_emotions = result.get("detected_emotions", [])
            
            # Convert the list of emotions to a dict with fake scores
            emotion_dict = {}
            for i, emotion in enumerate(detected_emotions):
                # Weight emotions by their order - first ones are stronger
                score = 1.0 - (i * 0.2)
                if score > 0:
                    emotion_dict[emotion] = score
            
            return emotion_dict
        else:
            # Simple keyword-based approach as fallback
            emotions = {}
            keywords = {
                "joy": ["happy", "excited", "glad", "joy", "delighted"],
                "sadness": ["sad", "unhappy", "depressed", "down", "miserable"],
                "anger": ["angry", "mad", "furious", "annoyed", "irritated"],
                "fear": ["afraid", "scared", "fearful", "terrified", "worried"],
                "surprise": ["surprised", "shocked", "amazed", "astonished"],
                "disgust": ["disgusted", "repulsed", "revolted"],
                "love": ["love", "adore", "cherish", "affection"],
                "confusion": ["confused", "puzzled", "perplexed"],
            }
            
            text_lower = text.lower()
            for emotion, words in keywords.items():
                for word in words:
                    if word in text_lower:
                        emotions[emotion] = emotions.get(emotion, 0) + 0.7
            
            return emotions
    except Exception as e:
        logger.error(f"Error in emotion analysis: {str(e)}")
        return {}


def check_crisis_keywords(text):
    """
    Check if the text contains any crisis keywords that might indicate a user needs immediate help.
    
    Args:
        text (str): The text to check
        
    Returns:
        bool: True if crisis keywords are found, False otherwise
    """
    try:
        if sentiment_analyzer:
            # Use the sentiment analyzer's internal crisis detection
            result = sentiment_analyzer.analyze_sentiment(text)
            return result["sentiment"] == "highly_negative"
        else:
            # Manual fallback for crisis detection
            crisis_keywords = [
                "suicide", "kill myself", "end my life", "don't want to live",
                "better off dead", "no reason to live", "can't go on", 
                "want to die", "hopeless", "worthless"
            ]
            
            text_lower = text.lower()
            for keyword in crisis_keywords:
                if keyword in text_lower:
                    return True
            
            return False
    except Exception as e:
        logger.error(f"Error in crisis keyword detection: {str(e)}")
        return False


def get_crisis_resources():
    """
    Provide crisis resources for users in need.
    
    Returns:
        str: A string with crisis resources
    """
    if sentiment_analyzer:
        return random.choice(sentiment_analyzer.crisis_resources)
    else:
        return ("If you're in crisis, please contact the National Suicide Prevention Lifeline "
               "at 988 or 1-800-273-8255, or text HOME to 741741 to reach the Crisis Text Line.")


def generate_chat_response(message, user_context=None):
    """Generate a personalized, therapeutic chat response with context awareness"""
    try:
        # Try using Gemini first
        if chat_session:
            try:
                # Get sentiment and emotion analysis
                sentiment_score, sentiment_label = analyze_sentiment(message)
                emotions = analyze_emotions(message)
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
                
                # Build a more directive system prompt to improve response quality
                system_prompt = f"""
                You are a supportive mental health companion chatbot, like a caring friend who listens well.
                
                Current conversation sentiment: {sentiment_label} ({sentiment_score:.2f})
                Detected emotions: {', '.join(emotions.keys()) if emotions else 'none detected'}
                
                Key guidelines:
                - Be warm, supportive, and conversational - like a caring friend, not a therapist
                - Keep responses brief (2-4 sentences) and natural sounding
                - Be empathetic but not overly clinical
                - Strictly limit yourself to ONE or ZERO questions per response
                - For very short user messages (like "yes" or "no"), respond naturally without asking another question
                - If user asks a direct question, provide a direct answer
                - Avoid phrases like "I understand" or "I hear you" too frequently
                - Don't repeat the same response patterns
                - Don't analyze the user's feelings back to them repeatedly
                
                The user's message indicates {dominant_emotion} emotion. Address this appropriately.
                """
                
                # Check for crisis keywords and provide resources
                is_crisis = check_crisis_keywords(message)
                
                if is_crisis:
                    crisis_resources = get_crisis_resources()
                    system_prompt += f"\nIMPORTANT: The user may be in crisis. Include this resource: {crisis_resources}"
                
                # Get context-appropriate response using our sentiment analyzer
                if sentiment_analyzer:
                    sentiment_result = sentiment_analyzer.analyze_sentiment(message)
                    response_data = sentiment_analyzer.get_response(sentiment_result)
                    
                    # Use the response directly from the analyzer
                    ai_response = response_data["response_text"]
                    
                    # Add crisis resources if needed
                    if response_data.get("additional_info"):
                        ai_response += f"\n\n{response_data['additional_info']}"
                    
                    return ai_response
                
                # Fallback to Gemini
                prompt = message
                
                # For very brief responses, add context to get better results
                if len(message.split()) < 3:
                    prompt = f"The user has sent a very brief message: '{message}'. Respond naturally without asking another question."
                
                # For question detection
                is_question = "?" in message or message.lower().startswith(("why", "what", "how", "who", "when", "where", "can", "could", "would", "do", "does", "is", "are"))
                if is_question:
                    prompt = f"The user is asking a direct question: '{message}'. Provide a supportive, direct answer."
                
                # Generate response with Gemini
                # Split the system prompt from the user message to assist the model
                response = chat_session.generate_content([
                    {"role": "user", "parts": [system_prompt]},
                    {"role": "model", "parts": ["I'll follow these guidelines carefully."]},
                    {"role": "user", "parts": [prompt]}
                ])
                
                # Extract just the text response
                ai_response = response.text
                
                # Add crisis resources if needed but wasn't included
                if is_crisis and "crisis" not in ai_response.lower() and "lifeline" not in ai_response.lower():
                    ai_response += f"\n\n{get_crisis_resources()}"
                
                return ai_response
                
            except Exception as e:
                logger.error(f"Error in Gemini response generation: {str(e)}")
                # Fall back to a more robust option
                if sentiment_analyzer:
                    sentiment_result = sentiment_analyzer.analyze_sentiment(message)
                    response_data = sentiment_analyzer.get_response(sentiment_result)
                    return response_data["response_text"]
                else:
                    return _generate_improved_fallback(message)
        else:
            # Use sentiment analyzer directly if Gemini isn't available
            if sentiment_analyzer:
                sentiment_result = sentiment_analyzer.analyze_sentiment(message)
                response_data = sentiment_analyzer.get_response(sentiment_result)
                
                ai_response = response_data["response_text"]
                
                # Add crisis resources if needed
                if response_data.get("additional_info"):
                    ai_response += f"\n\n{response_data['additional_info']}"
                
                return ai_response
            else:
                # Last resort fallback
                return _generate_improved_fallback(message)
    except Exception as e:
        logger.error(f"Error in chat response generation: {str(e)}")
        return "I'm having trouble processing that right now. How are you feeling today?"


def _generate_improved_fallback(message):
    """Generate a fallback response when AI services are unavailable"""
    message_lower = message.lower()
    
    # For very short responses, don't ask questions back
    if len(message.split()) < 3:
        brief_responses = [
            "I'm here with you. There's no rush to share more - I'm here to support you at your own pace.",
            "Thanks for letting me know. I'm here to support you through whatever you're experiencing.",
            "I appreciate you checking in. I'm here to listen whenever you're ready to share more.",
            "I understand. Take your time - I'm here to talk whenever you feel ready."
        ]
        return random.choice(brief_responses)
    
    # For questions, try to provide a more direct response
    if "?" in message or message_lower.startswith(("why", "what", "how", "who", "when", "where", "can", "could", "would", "do", "does", "is", "are")):
        question_responses = [
            "That's a thoughtful question. While I'm not able to provide specific answers, I'm here to support you in finding your own insights.",
            "I understand why you might be wondering about that. What are your own thoughts on this question?",
            "That's something many people wonder about. While I don't have a perfect answer, I'm here to explore this with you.",
            "That's a good question to reflect on. What feels most true for you when you consider this?"
        ]
        return random.choice(question_responses)
    
    # Context-specific responses based on emotional keywords
    if any(word in message_lower for word in ["sad", "down", "depressed", "unhappy", "miserable"]):
        emotion_responses = [
            "I hear that you're feeling down. Those emotions are completely valid, and it takes courage to acknowledge them. Try to be gentle with yourself right now.",
            "I'm sorry you're feeling sad. Would you like to talk more about what's weighing on you? Sometimes sharing can help lighten the burden.",
            "Those feelings of sadness are valid. Remember that all emotions pass with time, even though it might not feel that way right now."
        ]
        return random.choice(emotion_responses)
    
    if any(word in message_lower for word in ["anxious", "worried", "nervous", "stress", "overwhelm"]):
        emotion_responses = [
            "It sounds like you're feeling anxious. Taking slow, deep breaths might help in this moment.",
            "When we feel stressed, it's important to remember that these feelings aren't permanent. What's one small thing you could do to care for yourself right now?",
            "Feeling overwhelmed is really challenging. Sometimes breaking things down into smaller steps can help make things feel more manageable."
        ]
        return random.choice(emotion_responses)
    
    if any(word in message_lower for word in ["angry", "mad", "frustrated", "annoyed", "upset"]):
        emotion_responses = [
            "I can hear your frustration. Those feelings are completely valid given what you've shared.",
            "It's natural to feel angry in situations like this. How might you channel that energy in a way that feels helpful for you?",
            "Your feelings of anger make sense. Sometimes writing down our thoughts can help us process these strong emotions."
        ]
        return random.choice(emotion_responses)
    
    # Family/relationship context
    if any(word in message_lower for word in ["family", "parent", "mother", "father", "mom", "dad", "sister", "brother", "spouse", "partner", "relationship"]):
        relationship_responses = [
            "Family relationships can be deeply complex. It's okay to have mixed feelings about the people closest to us.",
            "Navigating relationships takes a lot of emotional energy. Remember that it's okay to set boundaries when needed.",
            "Those close to us can have the biggest impact on our wellbeing. What might help you feel more at peace with this situation?"
        ]
        return random.choice(relationship_responses)
    
    # Work/school context
    if any(word in message_lower for word in ["work", "job", "boss", "career", "school", "class", "study", "exam"]):
        work_responses = [
            "The pressures of work/school can really add up. Remember that your worth isn't defined by your productivity.",
            "It's common to feel stressed about our professional/academic lives. What small step might help make this situation more manageable?",
            "Finding balance with work/school can be challenging. Your wellbeing matters just as much as your obligations."
        ]
        return random.choice(work_responses)
    
    # Generic supportive responses as last resort
    generic_responses = [
        "Thank you for sharing that with me. I'm here to support you through whatever you're experiencing.",
        "I appreciate you opening up. Would it help to explore this situation further?",
        "It takes courage to express how you're feeling. What would feel most supportive right now?",
        "I'm here with you through this. Would it help to talk more about what's on your mind?"
    ]
    
    return random.choice(generic_responses)