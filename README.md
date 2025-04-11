# AI Mental Health Tracker

A web application that helps users track their mental health through journaling, mood tracking, and interactive relaxation games.

## Features

- Guided breathing exercises
- Interactive games (Tic Tac Toe, Snake, Color Matching)
- Mood tracking and analysis
- Journal entries with sentiment analysis
- AI-powered chat support
- Focus mode
- Music therapy recommendations

## System Requirements

- Windows 10 or later
- Python 3.8 or later
- Minimum 4GB RAM
- At least 10GB free disk space
- Internet connection for AI features

## Installation

1. Clone this repository or download the source code
2. Run the setup script as administrator:
   ```bash
   python setup.py
   ```
   This will:
   - Check system requirements
   - Increase page file size for AI model support
   - Install required Python packages

3. Restart your computer for the changes to take effect

## Running the Application

1. After restarting, open a terminal in the project directory
2. Run the application:
   ```bash
   python main.py
   ```
3. Open your web browser and navigate to `http://localhost:5000`

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