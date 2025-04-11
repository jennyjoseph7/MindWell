from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_wtf.csrf import CSRFProtect
from transformers import pipeline
import google.generativeai as genai
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this to a secure secret key in production

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Initialize models
emotion_classifier = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

# Configure Gemini API
genai.configure(api_key="YOUR_API_KEY_HERE")  # Replace with your actual Gemini API key
gemini_model = genai.GenerativeModel("gemini-pro")
chat_session = gemini_model.start_chat()

@app.route('/')
def ai_chat():
    if 'chat_history' not in session:
        session['chat_history'] = []
    return render_template('ai/chat.html', messages=session['chat_history'])

@app.route('/new_chat')
def new_chat():
    session['chat_history'] = []
    return redirect(url_for('ai_chat'))

@app.route('/send_message', methods=['POST'])
def send_message():
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'Empty message'}), 400
    
    try:
        # Emotion detection
        emotion_results = emotion_classifier(user_input)
        emotions = {res['label']: res['score'] for res in emotion_results[0]}
        dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
        
        # Construct prompt for Gemini
        prompt = f"The user seems to be feeling {dominant_emotion}. Here's their message: '{user_input}'. Respond appropriately with empathy."
        
        # Get response from Gemini
        response = chat_session.send_message(prompt)
        
        # Determine sentiment based on dominant emotion
        sentiment = 'POSITIVE' if dominant_emotion in ['joy', 'love'] else 'NEGATIVE'
        if dominant_emotion in ['neutral']:
            sentiment = 'NEUTRAL'
        
        # Save to session
        message_data = {
            'user_message': user_input,
            'ai_response': response.text,
            'timestamp': datetime.now(),
            'sentiment': sentiment,
            'emotions': emotions
        }
        
        if 'chat_history' not in session:
            session['chat_history'] = []
        
        session['chat_history'].append(message_data)
        session.modified = True
        
        return jsonify({
            'response': response.text,
            'sentiment': sentiment,
            'emotions': emotions
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 