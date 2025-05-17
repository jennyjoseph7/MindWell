# Enhanced Mental Health Chatbot

A comprehensive, well-trained mental health chatbot that provides empathetic, context-aware responses with crisis detection and escalation management.

## 🚀 Features

### Core Capabilities
- **Advanced Sentiment Analysis**: Uses multiple AI models for accurate emotion detection
- **Crisis Detection**: Automatically identifies crisis situations and provides appropriate resources
- **Context-Aware Conversations**: Maintains conversation history and context for better responses
- **Personalized Support**: Adapts responses based on user profile and conversation history
- **Professional Escalation**: Automatically escalates to appropriate crisis resources when needed

### Mental Health Focus
- **Empathetic Responses**: Trained specifically for mental health conversations
- **Crisis Intervention**: Immediate detection and response to suicidal ideation and self-harm
- **Resource Provision**: Automatic provision of crisis hotlines and support resources
- **Emotion Validation**: Acknowledges and validates user emotions appropriately
- **Coping Strategies**: Suggests evidence-based coping mechanisms

### Technical Features
- **Real-time Analysis**: Instant sentiment and emotion analysis
- **Session Management**: Maintains conversation context across sessions
- **Response Validation**: Ensures responses are appropriate and helpful
- **Quality Assurance**: Multiple validation layers for response quality
- **Scalable Architecture**: Built for high-volume usage

## 🏗️ Architecture

### Core Components

#### 1. Enhanced Mental Health Chatbot (`enhanced_mental_health_chatbot.py`)
- Main chatbot class with comprehensive mental health training
- Crisis detection and escalation management
- Context-aware conversation management
- Response validation and quality assurance

#### 2. Enhanced AI Chat Routes (`enhanced_ai_chat.py`)
- Flask routes for chatbot interaction
- Session management and user authentication
- Crisis resource provision
- User profile management

#### 3. Enhanced Chat Interface (`enhanced_chat.html`)
- Modern, responsive UI with real-time analysis
- Crisis status indicators
- Emotion analysis visualization
- Topic tracking and conversation insights

#### 4. Crisis Resources (`crisis_resources.html`)
- Comprehensive crisis resource directory
- Regional support information
- Self-help and coping strategies
- Professional help guidance

## 🧠 AI Capabilities

### Sentiment Analysis
- **Multi-Model Approach**: Combines TextBlob, RoBERTa, and custom models
- **Emotion Detection**: Identifies 20+ emotions including joy, sadness, anger, anxiety, fear
- **Crisis Keywords**: Detects suicidal ideation, self-harm, and crisis language
- **Context Awareness**: Considers conversation history and user patterns

### Crisis Detection
- **Immediate Response**: Detects crisis keywords and phrases
- **Escalation Levels**: None, Low, Moderate, High, Critical
- **Resource Provision**: Automatic provision of appropriate crisis resources
- **Professional Referral**: Escalates to human professionals when needed

### Response Generation
- **Empathetic Tone**: Trained for mental health conversations
- **Validation**: Acknowledges and validates user emotions
- **Coping Strategies**: Suggests evidence-based interventions
- **Crisis Response**: Immediate crisis intervention when needed

## 🎯 Mental Health Topics Covered

### Core Topics
- **Depression**: Recognition, validation, and coping strategies
- **Anxiety**: Grounding techniques and anxiety management
- **Relationships**: Family, romantic, and social relationship support
- **Work Stress**: Professional stress and burnout management
- **Academic Stress**: School and academic pressure support
- **Crisis Situations**: Suicidal ideation and self-harm intervention

### Specialized Support
- **LGBTQ+ Issues**: Specialized support for LGBTQ+ community
- **Trauma**: Trauma-informed responses and support
- **Grief**: Grief and loss support
- **Addiction**: Substance use and addiction support
- **Eating Disorders**: Body image and eating disorder support

## 🚨 Crisis Management

### Detection Patterns
```python
crisis_patterns = [
    r'\b(kill myself|suicide|end my life|want to die)\b',
    r'\b(no reason to live|better off dead|hopeless)\b',
    r'\b(harm myself|hurt myself|self harm)\b',
    r'\b(can\'t go on|give up|no point)\b',
    r'\b(worthless|useless|burden)\b',
    r'\b(no one cares|alone|isolated)\b'
]
```

### Escalation Levels
- **None**: Normal conversation
- **Low**: Mild distress, general support
- **Moderate**: Significant distress, coping strategies
- **High**: Crisis situation, immediate support
- **Critical**: Emergency, immediate intervention

### Crisis Resources
- **US**: 988 Suicide & Crisis Lifeline
- **UK**: 116 123 Samaritans
- **CA**: 1-833-456-4566 Crisis Services Canada
- **AU**: 13 11 14 Lifeline Australia

## 💻 Usage

### Basic Usage
```python
from src.mental_health_tracker.utils.enhanced_mental_health_chatbot import enhanced_chatbot

# Process a message
result = await enhanced_chatbot.process_message(
    user_id="user123",
    session_id="session456",
    message="I'm feeling really depressed today"
)

# Response includes:
# - AI response
# - Sentiment analysis
# - Emotion detection
# - Crisis level assessment
# - Topics discussed
```

### Web Interface
1. Navigate to `/enhanced-ai-chat/`
2. Start a conversation
3. Real-time analysis appears in sidebar
4. Crisis resources available via button

## 🔧 Configuration

### Environment Variables
```bash
# Required
ANTHROPIC_API_KEY=your_api_key

# Optional
USER_REGION=US  # For crisis resources
DEBUG=false
LOG_LEVEL=info
```

### Database Models
The chatbot uses existing database models:
- `ChatHistory`: Stores conversation history
- `MoodEntry`: Tracks user mood patterns
- `JournalEntry`: Links to journal entries for context

## 🛡️ Safety Features

### Crisis Intervention
- **Immediate Detection**: Recognizes crisis language instantly
- **Resource Provision**: Provides appropriate crisis resources
- **Professional Escalation**: Escalates to human professionals
- **Safety Planning**: Guides users through safety planning

### Privacy & Security
- **Data Encryption**: All conversations encrypted
- **Session Management**: Secure session handling
- **User Authentication**: Login required for access
- **Data Retention**: Configurable data retention policies

### Response Validation
- **Quality Checks**: Validates response appropriateness
- **Crisis Validation**: Ensures crisis responses are adequate
- **Empathy Validation**: Confirms empathetic tone
- **Professional Standards**: Meets mental health professional standards

## 📊 Analytics & Insights

### Conversation Analysis
- **Sentiment Tracking**: Monitors emotional trajectory
- **Topic Analysis**: Identifies discussed topics
- **Crisis Patterns**: Tracks crisis mentions and patterns
- **User Engagement**: Measures user interaction quality

### Mental Health Insights
- **Emotional Patterns**: Identifies emotional patterns over time
- **Coping Effectiveness**: Tracks coping strategy effectiveness
- **Progress Tracking**: Monitors mental health progress
- **Risk Assessment**: Assesses mental health risk factors

## 🚀 Deployment

### Requirements
- Python 3.8+
- Flask 2.0+
- SQLAlchemy
- Transformers (Hugging Face)
- Redis (optional, for session storage)

### Installation
```bash
pip install -r requirements.txt
python -m src.mental_health_tracker.app
```

### Production Considerations
- **Load Balancing**: Use multiple instances for high volume
- **Database Optimization**: Optimize database queries for performance
- **Caching**: Implement Redis caching for better performance
- **Monitoring**: Set up monitoring for crisis situations
- **Backup**: Regular database backups for conversation history

## 🤝 Contributing

### Development Guidelines
1. **Mental Health Focus**: All responses must be mental health appropriate
2. **Crisis Awareness**: Always consider crisis situations
3. **Empathy First**: Prioritize empathetic responses
4. **Professional Standards**: Meet mental health professional standards
5. **Testing**: Comprehensive testing for crisis scenarios

### Testing
- **Unit Tests**: Test individual components
- **Integration Tests**: Test full conversation flow
- **Crisis Tests**: Test crisis detection and response
- **User Tests**: Test with real users (with consent)

## 📚 Resources

### Mental Health Resources
- [National Suicide Prevention Lifeline](https://suicidepreventionlifeline.org/)
- [Mental Health America](https://www.mhanational.org/)
- [NAMI](https://www.nami.org/)
- [Crisis Text Line](https://www.crisistextline.org/)

### Technical Resources
- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

## ⚠️ Important Notes

### Limitations
- **Not a Replacement**: Not a replacement for professional mental health care
- **Crisis Situations**: Always escalate crisis situations to professionals
- **Medical Advice**: Does not provide medical advice or diagnosis
- **Emergency Situations**: Not for emergency situations - call 911/999/000

### Ethical Considerations
- **User Consent**: Always obtain user consent for data collection
- **Privacy**: Protect user privacy and confidentiality
- **Professional Oversight**: Regular oversight by mental health professionals
- **Continuous Improvement**: Regular updates based on user feedback

## 📞 Support

For technical support or questions about the enhanced chatbot:
- **Issues**: Report issues via GitHub issues
- **Documentation**: Check this README and inline documentation
- **Community**: Join our mental health tech community
- **Professional Support**: Contact mental health professionals for clinical questions

---

**Remember**: This chatbot is designed to provide support and resources, but it is not a replacement for professional mental health care. Always seek professional help for serious mental health concerns.
