"""
Database Models
Contains all database models for the application.
"""

from flask_sqlalchemy import SQLAlchemy

# Create a db instance without initializing it
db = SQLAlchemy()

# Import all models after db is created to avoid circular imports
from .models import (
    User,  # Import User first as other models depend on it
    UserActivity,
    MusicTherapySession,
    MoodEntry,
    JournalEntry,
    ChatHistory,
    BreathingExercise,
    TicTacToeGame,
    ColorMatchingGame
)

# Import crisis models
from .crisis_models import (
    CrisisIncident,
    EmergencyContact,
    CrisisTherapySession,
    CrisisNotification,
    CrisisResource,
    WellnessCheck,
    CrisisPattern,
    CrisisConfig
)

__all__ = [
    'db',
    'User',
    'UserActivity',
    'MusicTherapySession',
    'MoodEntry',
    'JournalEntry',
    'ChatHistory',
    'BreathingExercise',
    'TicTacToeGame',
    'ColorMatchingGame',
    'CrisisIncident',
    'EmergencyContact',
    'CrisisTherapySession',
    'CrisisNotification',
    'CrisisResource',
    'WellnessCheck',
    'CrisisPattern',
    'CrisisConfig'
]