"""
Mental Health Tracker Application
A Flask-based web application for tracking mental health and emotional well-being.
"""

from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from datetime import datetime, timedelta
from sqlalchemy import func, text
from werkzeug.security import generate_password_hash, check_password_hash
import os
import re
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, RadioField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from collections import defaultdict
import random

# Import the database instance and models
from .models import (
    db,
    User,
    MoodEntry,
    JournalEntry,
    ChatHistory,
    MusicTherapySession,
    UserActivity,
    BreathingExercise,
    TicTacToeGame,
    ColorMatchingGame
)

# Import utility functions
from .utils.ai_utils import analyze_sentiment, analyze_emotions, generate_chat_response

# Authentication forms
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=4, max=20)
    ])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password')
    ])
    submit = SubmitField('Register')

class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    submit = SubmitField('Request Password Reset')

class JournalEntryForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    mood = RadioField('Current Mood', choices=[
        ('very_sad', 'Very Sad'),
        ('sad', 'Sad'),
        ('neutral', 'Neutral'),
        ('happy', 'Happy'),
        ('very_happy', 'Very Happy')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Entry')

# Helper functions for music therapy
def scan_audio_files(mood):
    """Scan the audio directory for files matching the mood"""
    audio_dir = os.path.join(app.root_path, 'static', 'audio')
    mood_tracks = []
    
    # Check if audio directory exists
    if not os.path.exists(audio_dir):
        return []
    
    # Get all files in the audio directory
    files = os.listdir(audio_dir)
    
    # Filter files by mood (using naming convention: mood1.mp3, mood2.mp3, etc.)
    mood_pattern = f"{mood.lower()}[0-9]+.mp3"
    mood_files = [f for f in files if re.match(mood_pattern, f.lower())]
    
    # Sort files by number (e.g., happy1.mp3, happy2.mp3)
    mood_files.sort(key=lambda x: int(re.search(r'\d+', x).group()))
    
    # Create track objects
    for file in mood_files:
        track_id = f"{mood.lower()}_{file.split('.')[0]}"
        track_path = os.path.join('audio', file)
        mood_tracks.append({
            'id': track_id,
            'title': generate_title(track_id),
            'artist': generate_artist(mood),
            'file': track_path,
            'mood': mood
        })
    
    return mood_tracks

def generate_title(file_id):
    """Generate a user-friendly title from the file ID"""
    mood = file_id.split('_')[0]
    mood_map = {
        'happy': 'Uplifting',
        'sad': 'Reflective',
        'calm': 'Peaceful',
        'anxious': 'Calmative',
        'energetic': 'Motivating'
    }
    mood_name = mood_map.get(mood, 'Therapeutic')
    track_num = file_id.split('_')[1].split('.')[0]
    return f"{mood_name} Melody {track_num}"

def generate_artist(mood):
    """Generate an artist name based on the mood"""
    mood_map = {
        'happy': 'Positive Vibes',
        'sad': 'Emotional Harmony',
        'calm': 'Soothing Sounds',
        'anxious': 'Calmative Waves',
        'energetic': 'Motivation Mix'
    }
    return mood_map.get(mood, 'Therapeutic Sounds')

def get_therapy_tip(mood):
    """Provide therapy tips based on mood"""
    tips = {
        'happy': "Maintain your positive energy by engaging in activities you enjoy.",
        'sad': "It's okay to feel sad. Try expressing your emotions through writing or talking to someone.",
        'calm': "Practice deep breathing exercises to maintain your inner peace.",
        'anxious': "Try progressive muscle relaxation to ease your anxiety.",
        'energetic': "Channel your energy into productive activities you enjoy."
    }
    return tips.get(mood, "Take a moment to breathe and center yourself.")

def save_music_session():
    """Save a user's music therapy session data"""
    if request.method == 'POST':
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        try:
            session = MusicTherapySession(
                user_id=current_user.id,
                initial_mood=data.get('initial_mood', 'calm'),
                final_mood=data.get('final_mood', 'calm'),
                tracks_played=data.get('tracks_played', []),
                duration=data.get('duration', 0),
                feedback=data.get('feedback', '')
            )
            db.session.add(session)
            db.session.commit()
            
            return jsonify({'status': 'success'})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

def create_app(test_config=None):
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Configure the application
    app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI='sqlite:///mental_health.db',
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_SECURE=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE='Lax'
    )
    
    if test_config is None:
        # Load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # Load the test config if passed in
        app.config.update(test_config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize CSRF protection only if enabled in config
    if app.config.get('WTF_CSRF_ENABLED', False):
        csrf = CSRFProtect(app)
        
        # Ensure CSRF token is available in all templates
        @app.context_processor
        def inject_csrf_token():
            return dict(csrf_token=generate_csrf())
    else:
        # Log warning about disabled CSRF protection
        app.logger.warning("CSRF protection is disabled. This is not recommended for production.")
    
    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register timeago filter
    @app.template_filter('timeago')
    def timeago_filter(date):
        """Humanize a datetime as relative time. Treats naive datetimes as UTC.
        Guards against future timestamps by returning 'Just now'.
        """
        try:
            from datetime import timezone
            # Normalize to aware UTC
            if getattr(date, 'tzinfo', None) is None:
                date = date.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            diff = now - date
            # If somehow in the future (clock skew), clamp to zero
            if diff.total_seconds() < 0:
                diff = now - now

            if diff.days > 365:
                years = diff.days // 365
                return f"{years} year{'s' if years > 1 else ''} ago"
            if diff.days > 30:
                months = diff.days // 30
                return f"{months} month{'s' if months > 1 else ''} ago"
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            hours = diff.seconds // 3600
            if hours >= 1:
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            minutes = (diff.seconds % 3600) // 60
            if minutes >= 1:
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            return "Just now"
        except Exception:
            return "Just now"
    
    # Register blueprints
    from .routes import ai_chat_bp
    from .routes.enhanced_ai_chat import enhanced_ai_chat_bp
    from .routes.counseling import counseling_bp
    app.register_blueprint(ai_chat_bp)
    app.register_blueprint(enhanced_ai_chat_bp)
    app.register_blueprint(counseling_bp)
    
    # Add custom Jinja2 filters
    @app.template_filter('nl2br')
    def nl2br_filter(text):
        """Convert newlines to HTML line breaks"""
        if text is None:
            return ''
        return text.replace('\n', '<br>')
    
    # Register error handlers
    from .error_handlers import register_error_handlers
    register_error_handlers(app)
    
    # Define routes
    @app.route('/')
    def index():
        return render_template('index.html')

    # Serve favicon to prevent 404s
    @app.route('/favicon.ico')
    def favicon():
        return redirect(url_for('static', filename='favicon.ico'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('index'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            if not username or not password:
                flash('Please fill in all fields.', 'error')
                return redirect(url_for('login'))
            
            user = User.query.filter_by(username=username).first()
            
            if user and user.check_password(password):
                login_user(user)
                flash('Logged in successfully!', 'success')
                return redirect(url_for('index'))
            
            flash('Invalid username or password.', 'error')
        return render_template('auth/login.html')
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
            
        if request.method == 'POST':
            username = request.form.get('username')
            email = request.form.get('email')
            password = request.form.get('password')
            confirm_password = request.form.get('confirm_password')
            
            if not username or not email or not password or not confirm_password:
                flash('Please fill in all fields.', 'error')
                return redirect(url_for('register'))
            
            if password != confirm_password:
                flash('Passwords do not match.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(username=username).first():
                flash('Username already exists.', 'error')
                return redirect(url_for('register'))
            
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'error')
                return redirect(url_for('register'))
            
            user = User(
                username=username,
                email=email,
                name=username  # Set name to username if no separate name field
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        
        return render_template('auth/login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Get recent activities
        recent_activities = UserActivity.query.filter_by(user_id=current_user.id).order_by(UserActivity.created_at.desc()).limit(5).all()
        
        # Get recent mood entries
        recent_moods = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date_created.desc()).limit(10).all()
        
        # Get recent journal entries
        journal_entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).limit(2).all()
        
        # Calculate mood trend
        mood_trend = None
        if recent_moods:
            latest_mood = sum(mood.mood_score for mood in recent_moods[:3]) / min(len(recent_moods), 3)
            older_mood = sum(mood.mood_score for mood in recent_moods[-3:]) / min(len(recent_moods), 3)
            mood_trend = "improving" if latest_mood > older_mood else "steady" if latest_mood == older_mood else "declining"
        
        return render_template('dashboard.html',
                             recent_activities=recent_activities,
                             recent_moods=recent_moods,
                             journal_entries=journal_entries,
                             mood_trend=mood_trend,
                             current_date=datetime.now().strftime('%B %d, %Y'))

    @app.route('/chat')
    @login_required
    def chat():
        return render_template('chat.html')

    @app.route('/ai-chat')
    @login_required
    def ai_chat():
        # Get recent chat history
        chat_history = ChatHistory.query.filter_by(user_id=current_user.id).order_by(ChatHistory.timestamp.desc()).limit(10).all()
        
        return render_template('ai_chat.html', 
                             chat_history=chat_history)

    @app.route('/api/chat', methods=['POST'])
    @login_required
    def chat_api():
        try:
            data = request.get_json()
            if not data:
                return jsonify({'error': 'No data provided'}), 400
    
            message = data.get('message', '').strip()
            if not message:
                return jsonify({'error': 'Message is required'}), 400
    
            # Generate response
            response = generate_chat_response(message)
            
            # Save chat history
            chat = ChatHistory(
                user_id=current_user.id,
                message=message,
                response=response,
                timestamp=datetime.utcnow()
            )
            db.session.add(chat)
            db.session.commit()
    
            return jsonify({'response': response})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Journal routes
    @app.route('/journal')
    @login_required
    def journal_list():
        journal_entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).all()
        return render_template('journal/list.html', journal_entries=journal_entries)

    @app.route('/journal/new', methods=['GET', 'POST'])
    @login_required
    def journal_new():
        form = JournalEntryForm()
        
        if form.validate_on_submit():
            # Check for crisis indicators in journal content
            from .utils.robust_enhanced_chatbot import robust_enhanced_chatbot
            content_to_analyze = f"{form.title.data} {form.content.data}".lower()
            
            crisis_detected = False
            crisis_level = 'none'
            
            # Check crisis patterns
            for pattern in robust_enhanced_chatbot.crisis_patterns:
                if re.search(pattern, content_to_analyze):
                    crisis_detected = True
                    # Check if critical
                    critical_patterns = [
                        r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end(ing)? my life|want to die|wanna die)\b',
                        r'\b(harm(ing)? myself|hurt(ing)? myself|cut(ting)? myself|cutting)\b'
                    ]
                    if any(re.search(p, content_to_analyze) for p in critical_patterns):
                        crisis_level = 'critical'
                    else:
                        crisis_level = 'high'
                    break
            
            journal_entry = JournalEntry(
                user_id=current_user.id,
                title=form.title.data,
                content=form.content.data,
                date_created=datetime.now()
            )
            
            db.session.add(journal_entry)
            
            # Add activity record
            activity = UserActivity(
                user_id=current_user.id,
                activity_type="Journal Entry",
                description=f"Created journal entry: {form.title.data[:30]}...",
                created_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            # Flash different messages based on crisis detection
            if crisis_detected:
                flash('Journal entry saved. We noticed you may be going through a difficult time. Please consider reaching out for support.', 'warning')
                # Add crisis resources flash
                flash('Crisis Support: KIRAN Mental Health Helpline: 1800-599-0019 (24/7) | Emergency: 108', 'danger')
                
                # AUTOMATIC CRISIS RESPONSE
                if crisis_level in ['critical', 'high']:
                    try:
                        import asyncio
                        from .utils.crisis_response import CrisisResponseManager
                        
                        # Initialize crisis response manager
                        crisis_manager = CrisisResponseManager()
                        
                        # Get user info and emergency contacts
                        emergency_contacts = get_user_emergency_contacts(current_user.id)
                        user_info = {
                            'id': current_user.id,
                            'name': current_user.name,
                            'email': current_user.email,
                            'phone': getattr(current_user, 'phone', None),
                            'emergency_contacts': emergency_contacts
                        }
                        
                        # Crisis data
                        crisis_data = {
                            'crisis_detected': True,
                            'crisis_level': crisis_level,
                            'crisis_types': ['journal_entry'],
                            'detected_in': 'journal'
                        }
                        
                        # Handle crisis response (book therapy + notify contacts)
                        def run_async(coro):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(coro)
                            finally:
                                loop.close()
                        
                        response = run_async(crisis_manager.handle_crisis_response(
                            str(current_user.id), crisis_data, user_info
                        ))
                        
                        if response.get('crisis_handled'):
                            flash('🚨 AUTOMATIC ACTIONS TAKEN: Therapy session booked & emergency contacts notified', 'info')
                            logger.warning(f"Crisis response activated for user {current_user.id} from journal entry")
                    except Exception as e:
                        logger.error(f"Error in automatic crisis response: {str(e)}")
            else:
                flash('Journal entry saved successfully!', 'success')
            
            return redirect(url_for('dashboard'))
            
        return render_template('journal/new.html', form=form)

    @app.route('/journal/<int:entry_id>')
    @login_required
    def journal_view(entry_id):
        entry = JournalEntry.query.filter_by(
            id=entry_id,
            user_id=current_user.id
        ).first_or_404()
        
        return render_template('journal/view.html', entry=entry)

    @app.route('/journal/<int:entry_id>/edit', methods=['GET', 'POST'])
    @login_required
    def journal_edit(entry_id):
        entry = JournalEntry.query.filter_by(
            id=entry_id,
            user_id=current_user.id
        ).first_or_404()
        
        if request.method == 'POST':
            entry.title = request.form.get('title')
            entry.content = request.form.get('content')
            entry.date_modified = datetime.utcnow()
            
            # Check for crisis indicators in updated journal content
            from .utils.robust_enhanced_chatbot import robust_enhanced_chatbot
            content_to_analyze = f"{entry.title} {entry.content}".lower()
            
            crisis_detected = False
            crisis_level = 'none'
            
            # Check crisis patterns
            for pattern in robust_enhanced_chatbot.crisis_patterns:
                if re.search(pattern, content_to_analyze):
                    crisis_detected = True
                    # Check if critical
                    critical_patterns = [
                        r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end(ing)? my life|want to die|wanna die)\b',
                        r'\b(harm(ing)? myself|hurt(ing)? myself|cut(ting)? myself|cutting)\b'
                    ]
                    if any(re.search(p, content_to_analyze) for p in critical_patterns):
                        crisis_level = 'critical'
                    else:
                        crisis_level = 'high'
                    break
            
            db.session.commit()
            
            # Flash different messages based on crisis detection
            if crisis_detected:
                flash('Journal entry updated. We noticed you may be going through a difficult time. Please consider reaching out for support.', 'warning')
                flash('Crisis Support: KIRAN Mental Health Helpline: 1800-599-0019 (24/7) | Emergency: 108', 'danger')
                
                # AUTOMATIC CRISIS RESPONSE
                if crisis_level in ['critical', 'high']:
                    try:
                        import asyncio
                        from .utils.crisis_response import CrisisResponseManager
                        
                        crisis_manager = CrisisResponseManager()
                        emergency_contacts = get_user_emergency_contacts(current_user.id)
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
                            'crisis_types': ['journal_entry'],
                            'detected_in': 'journal_edit'
                        }
                        
                        def run_async(coro):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(coro)
                            finally:
                                loop.close()
                        
                        response = run_async(crisis_manager.handle_crisis_response(
                            str(current_user.id), crisis_data, user_info
                        ))
                        
                        if response.get('crisis_handled'):
                            flash('🚨 AUTOMATIC ACTIONS TAKEN: Therapy session booked & emergency contacts notified', 'info')
                            logger.warning(f"Crisis response activated for user {current_user.id} from journal edit")
                    except Exception as e:
                        logger.error(f"Error in automatic crisis response: {str(e)}")
            else:
                flash('Journal entry updated successfully!', 'success')
            
            return redirect(url_for('journal_view', entry_id=entry_id))
        
        return render_template('journal/edit.html', entry=entry)

    @app.route('/journal/<int:entry_id>/delete', methods=['POST'])
    @login_required
    def journal_delete(entry_id):
        entry = JournalEntry.query.filter_by(
            id=entry_id,
            user_id=current_user.id
        ).first_or_404()
        
        db.session.delete(entry)
        db.session.commit()
        
        flash('Journal entry deleted successfully!', 'success')
        return redirect(url_for('journal_list'))

    @app.route('/journal/entries')
    @login_required
    def journal_entries():
        # Get user's journal entries
        entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).all()
        
        # Add mood display information to entries
        for entry in entries:
            mood_text_map = {1: 'Very Sad', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
            mood_color_map = {1: 'danger', 2: 'warning', 3: 'secondary', 4: 'info', 5: 'success'}
            if entry.mood_score is not None:
                entry.mood = mood_text_map.get(entry.mood_score, 'Neutral')
                entry.mood_color = mood_color_map.get(entry.mood_score, 'secondary')
            else:
                entry.mood = 'Neutral'
                entry.mood_color = 'secondary'
        
        return render_template('journal/list.html', entries=entries)

    @app.route('/progress/dashboard')
    @login_required
    def progress_dashboard():
        # Get user's journal entries
        entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).all()
        
        # Prepare data for charts
        dates = []
        mood_scores = []
        activity_dates = []
        entry_counts = []
        
        # Process last 30 days of entries
        today = datetime.now()
        thirty_days_ago = today - timedelta(days=30)
        
        # Create mood data
        for entry in entries:
            if entry.date_created >= thirty_days_ago:
                dates.append(entry.date_created.strftime('%Y-%m-%d'))
                # Use mood_score from the entry (default to 3 if None)
                mood_scores.append(entry.mood_score if entry.mood_score is not None else 3)
        
        # Create activity data (entries per day)
        daily_counts = defaultdict(int)
        for entry in entries:
            if entry.date_created >= thirty_days_ago:
                date_str = entry.date_created.strftime('%Y-%m-%d')
                daily_counts[date_str] += 1
        
        # Sort by date
        for date in sorted(daily_counts.keys()):
            activity_dates.append(date)
            entry_counts.append(daily_counts[date])
        
        # Add mood display information to entries
        for entry in entries:
            # Map numeric mood score to display text and color
            mood_text_map = {1: 'Very Sad', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
            mood_color_map = {1: 'danger', 2: 'warning', 3: 'secondary', 4: 'info', 5: 'success'}
            
            if entry.mood_score is not None:
                entry.mood = mood_text_map.get(entry.mood_score, 'Neutral')
                entry.mood_color = mood_color_map.get(entry.mood_score, 'secondary')
            else:
                entry.mood = 'Neutral'
                entry.mood_color = 'secondary'
        
        return render_template(
            'progress/dashboard.html',
            entries=entries,
            dates=dates,
            mood_scores=mood_scores,
            activity_dates=activity_dates,
            entry_counts=entry_counts
        )

    @app.route('/insights')
    @login_required
    def ai_insights():
        # Get user's journal entries
        entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).limit(10).all()
        
        # Add mood display information to entries
        for entry in entries:
            # Map numeric mood score to display text and color
            mood_text_map = {1: 'Very Sad', 2: 'Sad', 3: 'Neutral', 4: 'Happy', 5: 'Very Happy'}
            mood_color_map = {1: 'danger', 2: 'warning', 3: 'secondary', 4: 'info', 5: 'success'}
            
            if entry.mood_score is not None:
                entry.mood = mood_text_map.get(entry.mood_score, 'Neutral')
                entry.mood_color = mood_color_map.get(entry.mood_score, 'secondary')
            else:
                entry.mood = 'Neutral'
                entry.mood_color = 'secondary'
        
        # Prepare data for sentiment analysis chart
        dates = []
        sentiment_scores = []
        
        # Mock sentiment analysis (replace with actual sentiment analysis in production)
        for entry in entries:
            dates.append(entry.date_created.strftime('%Y-%m-%d'))
            sentiment_scores.append(random.uniform(0, 1))  # Mock sentiment score between 0 and 1
        
        # Mock theme analysis
        themes = ['Family', 'Work', 'Health', 'Relationships', 'Personal Growth']
        theme_scores = [random.uniform(0, 1) for _ in themes]  # Mock theme frequencies
        
        return render_template(
            'insights/dashboard.html',
            entries=entries,
            dates=dates,
            sentiment_scores=sentiment_scores,
            themes=themes,
            theme_scores=theme_scores
        )

    @app.route('/music-dashboard')
    @login_required
    def music_dashboard():
        # Get recent music therapy sessions
        if current_user.is_authenticated:
            sessions = MusicTherapySession.query.filter_by(user_id=current_user.id).order_by(MusicTherapySession.start_time.desc()).limit(5).all()
        else:
            sessions = []
            
        return render_template('music/dashboard.html', sessions=sessions)
        
    # Music Therapy routes
    @app.route('/music-therapy')
    @login_required
    def music_therapy():
        # Get recent music therapy sessions
        sessions = MusicTherapySession.query.filter_by(user_id=current_user.id).order_by(MusicTherapySession.start_time.desc()).limit(5).all()
        
        # Get recent mood entries for mood recommendation
        latest_mood = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date_created.desc()).first()
        recommended_mood = None
        
        if latest_mood:
            mood_mapping = {
                1: 'sad',
                2: 'anxious',
                3: 'calm',
                4: 'happy',
                5: 'energetic'
            }
            recommended_mood = mood_mapping.get(latest_mood.mood_score, 'calm')
        
        return render_template('music_therapy.html',
                              sessions=sessions,
                              recommended_mood=recommended_mood)

    @app.route('/api/music-recommendations', methods=['POST'])
    @login_required
    def music_recommendations():
        try:
            data = request.get_json()
            mood = data.get('mood', 'calm')
            create_session = data.get('create_session', False)
            
            # If creating a new session, record it
            if create_session:
                session = MusicTherapySession(
                    user_id=current_user.id,
                    initial_mood=mood,
                    start_time=datetime.utcnow()
                )
                db.session.add(session)
                db.session.commit()
            
            # Get music tracks based on mood
            tracks = scan_audio_files(mood)
            
            return jsonify({
                'status': 'success',
                'tracks': tracks,
                'mood': mood
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/save-music-session', methods=['POST'])
    @login_required
    def save_music_session_api():
        return save_music_session()

    # Focus Mode routes
    @app.route('/focus')
    @login_required
    def focus_mode():
        # Get recent focus sessions
        sessions = UserActivity.query.filter_by(
            user_id=current_user.id,
            activity_type='focus'
        ).order_by(UserActivity.created_at.desc()).limit(5).all()
        
        # Get user's current focus streak
        streak = calculate_focus_streak(current_user.id)
        
        return render_template('focus_mode.html',
                              sessions=sessions,
                              focus_streak=streak)

    @app.route('/focus/dashboard')
    @login_required
    def focus_dashboard():
        # Get focus statistics
        stats = {
            'total_sessions': UserActivity.query.filter_by(
                user_id=current_user.id,
                activity_type='focus'
            ).count(),
            'recent_sessions': UserActivity.query.filter_by(
                user_id=current_user.id,
                activity_type='focus'
            ).order_by(UserActivity.created_at.desc()).limit(5).all(),
            'focus_streak': calculate_focus_streak(current_user.id),
            'most_productive_time': get_most_productive_time(current_user.id)
        }
        
        return render_template('focus_mode.html', stats=stats)

    # Helper functions for focus mode
    def calculate_focus_streak(user_id):
        """Calculate the user's current focus streak"""
        today = datetime.utcnow().date()
        streak = 0
        
        for i in range(7):  # Check last 7 days
            date = today - timedelta(days=i)
            has_session = UserActivity.query.filter(
                UserActivity.user_id == user_id,
                UserActivity.activity_type == 'focus',
                func.date(UserActivity.created_at) == date
            ).first()
            
            if has_session:
                streak += 1
            else:
                break
        
        return streak

    def get_most_productive_time(user_id):
        """Get the user's most productive time of day"""
        sessions = UserActivity.query.filter_by(
            user_id=user_id,
            activity_type='focus'
        ).all()
        
        if not sessions:
            return None
        
        time_counts = {}
        for session in sessions:
            hour = session.created_at.hour
            time_counts[hour] = time_counts.get(hour, 0) + 1
        
        most_productive_hour = max(time_counts, key=time_counts.get)
        return f"{most_productive_hour}:00 - {most_productive_hour + 1}:00"

    # Save Focus Session (Pomodoro) API
    @app.route('/api/save-focus-session', methods=['POST'])
    @login_required
    def save_focus_session_api():
        try:
            data = request.get_json() or {}
            cycles = int(data.get('cycles', 1))
            focus_minutes = int(data.get('focus_minutes', 25))
            break_minutes = int(data.get('break_minutes', 5))
            duration_seconds = int(data.get('duration_seconds', cycles * (focus_minutes + break_minutes) * 60))
            mood_before = data.get('mood_before')
            mood_after = data.get('mood_after')
            score = float(data.get('focus_score', 0))

            description_parts = [
                f"Pomodoro Quest: {cycles} cycle(s) {focus_minutes}/{break_minutes}m",
                f"Score {score:.0f}"
            ]
            if mood_before is not None and mood_after is not None:
                description_parts.append(f"Mood {mood_before}→{mood_after}")
            description = ' | '.join(description_parts)

            activity = UserActivity(
                user_id=current_user.id,
                activity_type='focus',
                description=description,
                created_at=datetime.utcnow()
            )
            # If the model has duration field, set it
            if hasattr(activity, 'duration'):
                setattr(activity, 'duration', duration_seconds)
            db.session.add(activity)
            db.session.commit()

            return jsonify({
                'status': 'success',
                'message': 'Focus session saved',
            })
        except Exception as e:
            db.session.rollback()
            return jsonify({'status': 'error', 'message': str(e)}), 500

    # Games routes
    @app.route('/games')
    @login_required
    def games_list():
        return render_template('games.html')

    @app.route('/games/dashboard')
    @login_required
    def games_dashboard():
        # Get breathing statistics
        breathing_stats = db.session.query(
            db.func.count(BreathingExercise.id).label('total_sessions'),
            db.func.sum(BreathingExercise.duration).label('total_minutes'),
            db.func.max(BreathingExercise.created_at).label('last_session')
        ).filter(BreathingExercise.user_id == current_user.id).first()

        # Get Tic Tac Toe statistics
        ttt_stats = db.session.query(
            db.func.count(TicTacToeGame.id).label('total_games'),
            db.func.sum(db.case((TicTacToeGame.winner == 'leaf', 1), else_=0)).label('leaf_wins'),
            db.func.sum(db.case((TicTacToeGame.winner == 'twig', 1), else_=0)).label('twig_wins'),
            db.func.sum(db.case((TicTacToeGame.winner == 'draw', 1), else_=0)).label('draws')
        ).filter(TicTacToeGame.user_id == current_user.id).first()

        # Get Color Matching statistics
        matching_stats = db.session.query(
            db.func.count(ColorMatchingGame.id).label('total_games'),
            db.func.max(ColorMatchingGame.score).label('best_score')
        ).filter(ColorMatchingGame.user_id == current_user.id).first()

        # Calculate weekly totals (last 7 days) across activities
        one_week_ago = datetime.utcnow() - timedelta(days=7)
        weekly_breathing_sessions = BreathingExercise.query.filter(
            BreathingExercise.user_id == current_user.id,
            BreathingExercise.created_at >= one_week_ago
        ).count()
        # Count all game activities logged in the last 7 days (covers TTT, Matching, etc.)
        weekly_game_activities = UserActivity.query.filter(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == 'game',
            UserActivity.created_at >= one_week_ago
        ).count()
        weekly_total_activities = weekly_breathing_sessions + weekly_game_activities

        # Get recent game activities
        recent_activities = UserActivity.query.filter(
            UserActivity.user_id == current_user.id,
            UserActivity.activity_type == 'game'
        ).order_by(UserActivity.created_at.desc()).limit(5).all()

        # Process recent activities for display
        processed_activities = []
        for activity in recent_activities:
            processed_activities.append({
                'description': activity.description,
                'type': 'Game',
                'type_class': 'success',
                'duration': '{}s'.format(activity.duration) if hasattr(activity, 'duration') else 'N/A',
                'date': activity.created_at.strftime('%Y-%m-%d %H:%M')
            })

        # Format data as expected by the template
        stats = {
            'breathing': {
                'total_sessions': breathing_stats.total_sessions if breathing_stats.total_sessions else 0,
                'total_minutes': breathing_stats.total_minutes // 60 if breathing_stats.total_minutes else 0,
                'last_session_date': breathing_stats.last_session.strftime('%Y-%m-%d') if breathing_stats.last_session else 'Never',
                # Use combined weekly total for the overview "This Week" metric
                'weekly_sessions': weekly_total_activities,
                'weekly_progress': min(weekly_total_activities * 14, 100)  # 7 activities per week = 100%
            },
            'ttt': {
                'total_games': ttt_stats.total_games if ttt_stats.total_games else 0,
                'leaf_wins': ttt_stats.leaf_wins if ttt_stats.leaf_wins else 0,
                'twig_wins': ttt_stats.twig_wins if ttt_stats.twig_wins else 0,
                'draws': ttt_stats.draws if ttt_stats.draws else 0
            },
            'matching': {
                'total_games': matching_stats.total_games if matching_stats.total_games else 0,
                'best_score': matching_stats.best_score if matching_stats.best_score else 0
            },
            'recent_activities': processed_activities
        }

        return render_template('games_dashboard.html', stats=stats)

    @app.route('/api/games/overview')
    @login_required
    def api_games_overview():
        """Return dynamic overview stats for the games dashboard.
        Output: { totalActivities, minutesSpent, bestScore, thisWeek }
        """
        try:
            # Totals (safe fallbacks)
            try:
                total_breathing = BreathingExercise.query.filter_by(user_id=current_user.id).count()
            except Exception:
                total_breathing = 0
            try:
                total_ttt = TicTacToeGame.query.filter_by(user_id=current_user.id).count()
            except Exception:
                total_ttt = 0
            try:
                total_matching = ColorMatchingGame.query.filter_by(user_id=current_user.id).count()
            except Exception:
                total_matching = 0
            if not total_matching:
                try:
                    total_matching = db.session.query(db.func.count(UserActivity.id)).filter(
                        UserActivity.user_id == current_user.id,
                        UserActivity.activity_type == 'game',
                        UserActivity.description.ilike('%color matching%')
                    ).scalar() or 0
                except Exception:
                    total_matching = 0

            # Minutes spent is sum of breathing durations (seconds -> minutes)
            minutes_spent = 0
            try:
                total_breathing_seconds = db.session.query(db.func.sum(BreathingExercise.duration)).filter(
                    BreathingExercise.user_id == current_user.id
                ).scalar() or 0
                minutes_spent = int((total_breathing_seconds or 0) // 60)
            except Exception:
                minutes_spent = 0

            # Best score from matching (with activity fallback)
            best_score = 0
            try:
                best_score = db.session.query(db.func.max(ColorMatchingGame.score)).filter(
                    ColorMatchingGame.user_id == current_user.id
                ).scalar() or 0
            except Exception:
                best_score = 0
            if not best_score:
                try:
                    acts = UserActivity.query.filter(
                        UserActivity.user_id == current_user.id,
                        UserActivity.activity_type == 'game',
                        UserActivity.description.ilike('%color matching%')
                    ).all()
                    import re
                    for a in acts:
                        m = re.search(r'score\s+(\d+)', a.description or '', re.IGNORECASE)
                        if m:
                            best_score = max(best_score, int(m.group(1)))
                except Exception:
                    pass

            # This week (last 7 days) - count directly from game tables plus breathing
            this_week = 0
            try:
                one_week_ago = datetime.utcnow() - timedelta(days=7)
                weekly_breathing = BreathingExercise.query.filter(
                    BreathingExercise.user_id == current_user.id,
                    BreathingExercise.created_at >= one_week_ago
                ).count()
            except Exception:
                weekly_breathing = 0
            try:
                weekly_ttt = TicTacToeGame.query.filter(
                    TicTacToeGame.user_id == current_user.id,
                    TicTacToeGame.created_at >= one_week_ago
                ).count()
            except Exception:
                weekly_ttt = 0
            try:
                weekly_matching = ColorMatchingGame.query.filter(
                    ColorMatchingGame.user_id == current_user.id,
                    ColorMatchingGame.created_at >= one_week_ago
                ).count()
            except Exception:
                weekly_matching = 0
            if not weekly_matching:
                try:
                    weekly_matching = db.session.query(db.func.count(UserActivity.id)).filter(
                        UserActivity.user_id == current_user.id,
                        UserActivity.activity_type == 'game',
                        UserActivity.created_at >= one_week_ago,
                        UserActivity.description.ilike('%color matching%')
                    ).scalar() or 0
                except Exception:
                    weekly_matching = 0
            this_week = int((weekly_breathing or 0) + (weekly_ttt or 0) + (weekly_matching or 0))

            return jsonify({
                'totalActivities': int((total_breathing or 0) + (total_ttt or 0) + (total_matching or 0)),
                'minutesSpent': int(minutes_spent or 0),
                'bestScore': int(best_score or 0),
                'thisWeek': int(this_week or 0)
            })
        except Exception as e:
            return jsonify({'error': 'overview_failed', 'details': str(e)}), 500

    @app.route('/games/breathing')
    @login_required
    def breathing_exercise():
        # Get user's recent breathing sessions
        recent_sessions = BreathingExercise.query.filter_by(user_id=current_user.id)\
            .order_by(BreathingExercise.created_at.desc()).limit(5).all()
        
        # Get user's breathing statistics
        total_sessions = BreathingExercise.query.filter_by(user_id=current_user.id).count()
        total_minutes = db.session.query(db.func.sum(BreathingExercise.duration))\
            .filter_by(user_id=current_user.id).scalar() or 0
        total_minutes = total_minutes // 60  # Convert seconds to minutes
        
        # Get last session date
        last_session = BreathingExercise.query.filter_by(user_id=current_user.id)\
            .order_by(BreathingExercise.created_at.desc()).first()
        last_session_date = last_session.created_at.strftime('%Y-%m-%d') if last_session else 'Never'
        
        return render_template('games/breathing.html', 
                              recent_sessions=recent_sessions,
                              total_sessions=total_sessions,
                              total_minutes=total_minutes,
                              last_session_date=last_session_date,
                              hide_nav=True,
                              hide_footer=True)

    @app.route('/api/save-breathing-session', methods=['POST'])
    @login_required
    def save_breathing_session():
        data = request.json
        technique = data.get('technique')
        duration = data.get('duration')
        
        if not technique or not duration:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        # Create new breathing session
        session = BreathingExercise(
            user_id=current_user.id,
            technique=technique,
            duration=duration
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Breathing session saved successfully'})

    @app.route('/games/honor-score')
    @login_required
    def honor_score():
        # Get user's honor score
        honor_score = UserActivity.query.filter_by(
            user_id=current_user.id,
            activity_type='game'
        ).count()
        
        return render_template('honor_score.html', honor_score=honor_score)

    @app.route('/games/ttt')
    @login_required
    def ttt_excercise():
        return render_template('games/ttt.html')

    @app.route('/games/snake')
    @login_required
    def snake_exercise():
        return render_template('games/snake.html')

    @app.route('/games/matching')
    @login_required
    def matching_exercise():
        print("Rendering matching game template")
        return render_template('games/matching.html', hide_nav=True, hide_footer=True)

    @app.route('/games/gratitude-wordle')
    @login_required
    def gratitude_wordle():
        return render_template('games/gratitude_wordle.html', hide_nav=True, hide_footer=True)

    @app.route('/api/games/weekly-activity')
    @login_required
    def api_games_weekly_activity():
        """Return last 7 days of activity counts for each game.
        Output: { labels: [Mon..Sun], breathing: [], ttt: [], matching: [], snake: [], wordle: [] }
        """
        try:
            today = datetime.utcnow().date()
            labels = []
            breathing_counts = []
            ttt_counts = []
            matching_counts = []
            snake_counts = []
            wordle_counts = []

            for i in range(6, -1, -1):
                day = today - timedelta(days=i)
                labels.append(day.strftime('%a'))

                day_start = datetime(day.year, day.month, day.day)
                day_end = day_start + timedelta(days=1)

                # Breathing sessions by day
                b = db.session.query(db.func.count(BreathingExercise.id)).filter(
                    BreathingExercise.user_id == current_user.id,
                    BreathingExercise.created_at >= day_start,
                    BreathingExercise.created_at < day_end
                ).scalar() or 0

                # TicTacToe by day
                ttt = db.session.query(db.func.count(TicTacToeGame.id)).filter(
                    TicTacToeGame.user_id == current_user.id,
                    TicTacToeGame.created_at >= day_start,
                    TicTacToeGame.created_at < day_end
                ).scalar() or 0

                # Matching by day (table count, with activity fallback)
                try:
                    match = db.session.query(db.func.count(ColorMatchingGame.id)).filter(
                        ColorMatchingGame.user_id == current_user.id,
                        ColorMatchingGame.created_at >= day_start,
                        ColorMatchingGame.created_at < day_end
                    ).scalar() or 0
                except Exception:
                    match = 0
                if not match:
                    match = db.session.query(db.func.count(UserActivity.id)).filter(
                        UserActivity.user_id == current_user.id,
                        UserActivity.activity_type == 'game',
                        UserActivity.created_at >= day_start,
                        UserActivity.created_at < day_end,
                        UserActivity.description.ilike('%color matching%')
                    ).scalar() or 0

                # Snake and Wordle via UserActivity descriptions
                snake = db.session.query(db.func.count(UserActivity.id)).filter(
                    UserActivity.user_id == current_user.id,
                    UserActivity.activity_type == 'game',
                    UserActivity.created_at >= day_start,
                    UserActivity.created_at < day_end,
                    UserActivity.description.ilike('%snake%')
                ).scalar() or 0
                wordle = db.session.query(db.func.count(UserActivity.id)).filter(
                    UserActivity.user_id == current_user.id,
                    UserActivity.activity_type == 'game',
                    UserActivity.created_at >= day_start,
                    UserActivity.created_at < day_end,
                    (UserActivity.description.ilike('%wordle%') | UserActivity.description.ilike('%gratitude%'))
                ).scalar() or 0

                breathing_counts.append(int(b))
                ttt_counts.append(int(ttt))
                matching_counts.append(int(match))
                snake_counts.append(int(snake))
                wordle_counts.append(int(wordle))

            return jsonify({
                'labels': labels,
                'breathing': breathing_counts,
                'ttt': ttt_counts,
                'matching': matching_counts,
                'snake': snake_counts,
                'wordle': wordle_counts
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # Authentication routes
    @app.route('/auth/reset-password', methods=['GET', 'POST'])
    def auth_reset_password():
        form = ResetPasswordForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                # In a real application, you would send a password reset email
                flash('Password reset instructions have been sent to your email.', 'success')
            else:
                flash('If an account exists with that email, you will receive reset instructions.', 'info')
            return redirect(url_for('login'))
        
        return render_template('auth/reset_password.html', form=form)
    
    # Mood tracking routes
    @app.route('/mood-tracker')
    @login_required
    def mood_tracker():
        # Get the mood entries for the user, ordered by date
        entries = MoodEntry.query.filter_by(user_id=current_user.id).order_by(MoodEntry.date_created.desc()).all()
        return render_template('mood/index.html', entries=entries)

    @app.route('/mood/new', methods=['GET', 'POST'])
    @login_required
    def mood_new():
        if request.method == 'POST':
            mood_score = int(request.form.get('mood_score', 3))
            mood_note = request.form.get('mood_note', '')
            
            mood_entry = MoodEntry(
                user_id=current_user.id,
                mood_score=mood_score,
                notes=mood_note,
                date_created=datetime.now()
            )
            
            db.session.add(mood_entry)
            
            # Add activity record
            activity = UserActivity(
                user_id=current_user.id,
                activity_type="Mood Tracking",
                description=f"Recorded mood: {mood_score}/5",
                created_at=datetime.utcnow()
            )
            db.session.add(activity)
            db.session.commit()
            
            # CRISIS DETECTION IN MOOD TRACKER
            crisis_detected = False
            crisis_level = 'none'
            
            # Check for very low mood score (1-2 out of 5)
            if mood_score <= 2:
                crisis_detected = True
                crisis_level = 'high' if mood_score == 1 else 'moderate'
            
            # Check mood notes for crisis keywords
            if mood_note:
                from .utils.robust_enhanced_chatbot import robust_enhanced_chatbot
                mood_note_lower = mood_note.lower()
                
                for pattern in robust_enhanced_chatbot.crisis_patterns:
                    if re.search(pattern, mood_note_lower):
                        crisis_detected = True
                        # Check if critical
                        critical_patterns = [
                            r'\b(kill myself|suici[dt][ae]l?|sucidal|suicide?|end(ing)? my life|want to die|wanna die)\b',
                            r'\b(harm(ing)? myself|hurt(ing)? myself|cut(ting)? myself|cutting)\b'
                        ]
                        if any(re.search(p, mood_note_lower) for p in critical_patterns):
                            crisis_level = 'critical'
                        else:
                            crisis_level = 'high'
                        break
            
            # Handle crisis if detected
            if crisis_detected:
                flash('Mood recorded. We noticed you may be going through a difficult time.', 'warning')
                flash('Crisis Support: KIRAN Mental Health Helpline: 1800-599-0019 (24/7) | Emergency: 108', 'danger')
                
                # AUTOMATIC CRISIS RESPONSE
                if crisis_level in ['critical', 'high']:
                    try:
                        import asyncio
                        from .utils.crisis_response import CrisisResponseManager
                        
                        crisis_manager = CrisisResponseManager()
                        emergency_contacts = get_user_emergency_contacts(current_user.id)
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
                            'crisis_types': ['mood_tracker', f'mood_score_{mood_score}'],
                            'detected_in': 'mood_tracker'
                        }
                        
                        def run_async(coro):
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            try:
                                return loop.run_until_complete(coro)
                            finally:
                                loop.close()
                        
                        response = run_async(crisis_manager.handle_crisis_response(
                            str(current_user.id), crisis_data, user_info
                        ))
                        
                        if response.get('crisis_handled'):
                            flash('🚨 AUTOMATIC ACTIONS TAKEN: Therapy session booked & emergency contacts notified', 'info')
                            logger.warning(f"Crisis response activated for user {current_user.id} from mood tracker")
                    except Exception as e:
                        logger.error(f"Error in automatic crisis response: {str(e)}")
            else:
                flash('Mood recorded successfully!', 'success')
            
            return redirect(url_for('dashboard'))
            
        return render_template('mood/new_entry.html')
    
    @app.route('/music')
    def music_redirect():
        # Redirect /music to /music-dashboard
        return redirect(url_for('music_dashboard'))
        
    @app.route('/hboard')
    def hboard_view():
        if not current_user.is_authenticated:
            return render_template('music/dashboard.html', sessions=None, requires_login=True)
        
        sessions = MusicTherapySession.query.filter_by(user_id=current_user.id).order_by(MusicTherapySession.start_time.desc()).limit(5).all()
        return render_template('music/dashboard.html', sessions=sessions, requires_login=False)

    @app.route('/api/save-ttt-game', methods=['POST'])
    @login_required
    def save_ttt_game():
        data = request.json
        winner = data.get('winner')
        moves = data.get('moves')
        duration = data.get('duration')
        
        if not winner or not moves or not duration:
            return jsonify({'success': False, 'message': 'Missing required data'}), 400
        
        # Create new game record
        game = TicTacToeGame(
            user_id=current_user.id,
            winner=winner,
            moves=moves,
            duration=duration
        )
        
        db.session.add(game)
        
        # Add activity record
        activity = UserActivity(
            user_id=current_user.id,
            activity_type="game",
            description=f"Played Tic Tac Toe - {winner.capitalize()} won in {moves} moves",
            created_at=datetime.utcnow()
        )
        db.session.add(activity)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Game statistics saved successfully'})

    @app.route('/api/save-matching-game', methods=['POST'])
    @login_required
    def save_matching_game():
        data = request.get_json(silent=True) or {}
        if 'score' not in data or 'duration' not in data:
            return jsonify({'error': 'missing_fields', 'details': 'score and duration are required'}), 400

        try:
            score = int(data.get('score', 0))
        except Exception:
            return jsonify({'error': 'invalid_score', 'details': f"score='{data.get('score')}'"}), 400
        try:
            duration = int(data.get('duration', 0))
        except Exception:
            return jsonify({'error': 'invalid_duration', 'details': f"duration='{data.get('duration')}'"}), 400

        difficulty = str(data.get('difficulty', 'easy'))

        try:
            # Insert for existing schema (without difficulty) if needed
            try:
                game = ColorMatchingGame(
                    user_id=current_user.id,
                    score=score,
                    duration=duration,
                    difficulty=difficulty
                )
                db.session.add(game)
                schema_has_difficulty = True
            except TypeError:
                # Fallback: model/table without difficulty column
                schema_has_difficulty = False
                db.session.execute(
                    text("INSERT INTO color_matching_game (user_id, score, duration, created_at) VALUES (:uid, :score, :duration, :created_at)"),
                    {
                        'uid': current_user.id,
                        'score': score,
                        'duration': duration,
                        'created_at': datetime.utcnow()
                    }
                )

            activity = UserActivity(
                user_id=current_user.id,
                activity_type='game',
                description=f'Completed Color Matching game ({difficulty}) with score {score} in {duration} seconds',
                created_at=datetime.utcnow()
            )
            db.session.add(activity)
            
            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                # Auto-create tables if they are missing, then retry once
                if 'no such table' in str(e).lower() or 'does not exist' in str(e).lower():
                    try:
                        db.create_all()
                        if schema_has_difficulty:
                            db.session.add(game)
                        else:
                            db.session.execute(
                                text("INSERT INTO color_matching_game (user_id, score, duration, created_at) VALUES (:uid, :score, :duration, :created_at)"),
                                {
                                    'uid': current_user.id,
                                    'score': score,
                                    'duration': duration,
                                    'created_at': datetime.utcnow()
                                }
                            )
                        db.session.add(activity)
                        db.session.commit()
                    except Exception as e2:
                        db.session.rollback()
                        return jsonify({'error': 'save_failed_after_create', 'details': str(e2)}), 500
                else:
                    return jsonify({'error': 'save_failed', 'details': str(e)}), 500

            return jsonify({'message': 'Game statistics saved successfully'})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': 'save_exception', 'details': str(e)}), 500

    @app.route('/api/journal/summary')
    @login_required
    def journal_summary():
        try:
            # Get user's journal entries
            entries = JournalEntry.query.filter_by(user_id=current_user.id).order_by(JournalEntry.date_created.desc()).all()
            
            # Calculate total entries
            total_entries = len(entries)
            
            # Calculate average mood score
            mood_scores = [entry.mood_score for entry in entries if entry.mood_score is not None]
            average_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
            
            # Get recent insights (last 3 entries)
            recent_insights = []
            for entry in entries[:3]:
                if entry.sentiment_label:
                    insight = f"Your recent entry shows {entry.sentiment_label} sentiment"
                    if entry.mood_score:
                        mood_map = {1: "very low", 2: "low", 3: "neutral", 4: "high", 5: "very high"}
                        insight += f" with {mood_map[entry.mood_score]} mood"
                    recent_insights.append(insight)
            
            # Extract common keywords from recent entries
            keywords = set()
            for entry in entries[:5]:  # Look at last 5 entries
                content = entry.content.lower()
                # Simple keyword extraction (can be enhanced with NLP)
                words = content.split()
                for word in words:
                    if len(word) > 4 and word.isalpha():  # Basic filtering
                        keywords.add(word)
            
            return jsonify({
                'total_entries': total_entries,
                'average_mood': average_mood,
                'recent_insights': recent_insights,
                'keywords': list(keywords)[:10]  # Limit to 10 keywords
            })
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/journal/sentiment-series')
    @login_required
    def journal_sentiment_series():
        """Return recent journal sentiment scores as a time series for charts.
        Output: { labels: [isoDate], sentiments: [0-100] }
        """
        try:
            # Last 10 journal entries for current user ordered ascending by date
            entries = JournalEntry.query \
                .filter_by(user_id=current_user.id) \
                .order_by(JournalEntry.date_created.desc()) \
                .limit(10).all()
            entries = list(reversed(entries))

            labels = []
            sentiments = []
            for entry in entries:
                # ISO date label
                labels.append(entry.date_created.strftime('%Y-%m-%d'))
                # sentiment_score may be None; default to neutral 0.5
                raw = entry.sentiment_score if entry.sentiment_score is not None else 0.5
                # Normalize assumed 0..1 to 0..100; clamp for safety
                try:
                    pct = max(0, min(100, float(raw) * 100.0))
                except Exception:
                    pct = 50.0
                sentiments.append(round(pct, 2))

            return jsonify({ 'labels': labels, 'sentiments': sentiments })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/moods/latest')
    @login_required
    def api_moods_latest():
        """Return last 10 mood entries for current user as a simple series."""
        try:
            moods = (
                MoodEntry.query
                .filter_by(user_id=current_user.id)
                .order_by(MoodEntry.date_created.desc())
                .limit(10)
                .all()
            )
            return jsonify([
                {
                    "timestamp": mood.date_created.isoformat(),
                    "mood": mood.mood_score
                }
                for mood in reversed(moods)
            ])
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/daily-progress')
    @login_required
    def api_daily_progress():
        """Compute today's progress toward daily goals.
        Goals: mood (1), journal (1), games (3), music (>=5 min).
        Returns: { percentage, goals: {mood:bool, journal:bool, games:int, musicMinutes:int} }
        """
        try:
            from datetime import timezone
            today = datetime.now(timezone.utc).date()

            # Mood today
            mood_done = bool(
                MoodEntry.query
                .filter_by(user_id=current_user.id)
                .filter(db.func.date(MoodEntry.date_created) == today)
                .first()
            )

            # Journal today
            journal_done = bool(
                JournalEntry.query
                .filter_by(user_id=current_user.id)
                .filter(db.func.date(JournalEntry.date_created) == today)
                .first()
            )

            # Games count today
            from .models import TicTacToeGame, ColorMatchingGame
            games_count = 0
            games_count += db.session.query(db.func.count(TicTacToeGame.id)).filter(
                TicTacToeGame.user_id == current_user.id,
                db.func.date(TicTacToeGame.created_at) == today
            ).scalar() or 0
            games_count += db.session.query(db.func.count(ColorMatchingGame.id)).filter(
                ColorMatchingGame.user_id == current_user.id,
                db.func.date(ColorMatchingGame.created_at) == today
            ).scalar() or 0

            # Music minutes today
            music_minutes = 0
            try:
                from .models import MusicTherapySession
                sessions = MusicTherapySession.query.filter(
                    MusicTherapySession.user_id == current_user.id,
                    db.func.date(MusicTherapySession.start_time) == today
                ).all()
                for s in sessions:
                    # prefer duration_seconds if set; else diff between end and start
                    seconds = getattr(s, 'duration_seconds', None) or 0
                    if not seconds and getattr(s, 'end_time', None):
                        seconds = int((s.end_time - s.start_time).total_seconds())
                    music_minutes += int(seconds // 60)
            except Exception:
                music_minutes = 0

            # Compute percentage
            completed = 0
            if mood_done: completed += 1
            if journal_done: completed += 1
            if games_count >= 3: completed += 1
            if music_minutes >= 5: completed += 1
            percentage = int((completed / 4) * 100)

            return jsonify({
                'percentage': percentage,
                'goals': {
                    'mood': mood_done,
                    'journal': journal_done,
                    'games': games_count,
                    'musicMinutes': music_minutes
                }
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    # Initialize the database
    with app.app_context():
        db.create_all()
    
    return app

__version__ = '1.0.0'
__all__ = ['create_app', 'db'] 