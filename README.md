# AI Mental Health Tracker

A web application that helps users track their mental health through journaling, mood tracking, and interactive relaxation games.

## Features

- Guided breathing exercises
- Interactive games (Tic Tac Toe, Snake, Color Matching)
- Mood tracking and analysis
- Journal entries with sentiment analysis
- AI-powered chat support with crisis detection
- Focus mode
- Music therapy recommendations

## Enhanced AI Features

- **Advanced Sentiment Analysis**: Uses RoBERTa model to detect emotions with higher accuracy
- **Emotion Recognition**: Detects specific emotions (anger, sadness, anxiety, fear, confusion) and responds appropriately
- **Context Awareness**: Recognizes topics like family, relationships, work stress and tailors responses
- **Conversation Memory**: Tracks conversation history to avoid repetitive responses
- **Crisis Detection**: Identifies potentially concerning messages and provides appropriate resources
- **Adaptive Responses**: Provides varied, natural responses that fit the user's emotional state
- **Special Handling for Brief Replies**: Properly handles short user messages like "yes", "no", or "ok" without asking redundant questions

## System Requirements

- Windows 10 or later
- Python 3.8 or later
- Minimum 4GB RAM
- At least 10GB free disk space
- Internet connection for AI features

## Installation

1. Clone this repository or download the source code
2. Create a .env file from the example:
   ```bash
   cp env.example .env
   ```
   Then edit .env to add your API keys

3. Run the setup script as administrator:
   ```bash
   python setup.py
   ```
   This will:
   - Check system requirements
   - Increase page file size for AI model support
   - Install required Python packages

4. Restart your computer for the changes to take effect

## API Keys

For full functionality, you'll need to obtain:
- A Google AI API key (Gemini) from https://ai.google.dev/
- Add it to your .env file as GEMINI_API_KEY=your-key-here

## Running the Application

1. After restarting, open a terminal in the project directory
2. Run the application:
   ```bash
   python main.py
   ```
3. Open your web browser and navigate to `http://localhost:5000`

## Testing the Sentiment Analysis

To test the RoBERTa sentiment analyzer functionality:
```bash
python test_sentiment.py
```
This will demonstrate the advanced sentiment analysis and crisis detection features.

## Troubleshooting

If you encounter the "paging file is too small" error:

1. Run the setup script as administrator
2. If the setup script fails, manually increase your page file size:
   - Open System Properties (Win + Pause/Break)
   - Click "Advanced system settings"
   - Under Performance, click "Settings"
   - Go to "Advanced" tab
   - Under Virtual Memory, click "Change"
   - Uncheck "Automatically manage paging file size"
   - Set initial and maximum size to 1.5x your RAM size
   - Click "Set" and "OK"
   - Restart your computer

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 