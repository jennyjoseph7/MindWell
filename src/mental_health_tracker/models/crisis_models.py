"""
Database models for crisis detection and response system
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON
from . import db

class CrisisIncident(db.Model):
    """Model for storing crisis incidents and responses"""
    __tablename__ = 'crisis_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)  # suicidal_ideation, self_harm, etc.
    crisis_level = db.Column(db.String(20), nullable=False)  # none, low, medium, high, critical
    confidence_score = db.Column(db.Float, nullable=True)
    detected_text = db.Column(db.Text, nullable=True)  # The text that triggered detection
    context_data = db.Column(db.JSON, nullable=True)  # Additional context
    response_actions = db.Column(db.JSON, nullable=True)  # Actions taken
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    resolved = db.Column(db.Boolean, default=False, nullable=False)
    follow_up_required = db.Column(db.Boolean, default=False, nullable=False)
    follow_up_completed = db.Column(db.Boolean, default=False, nullable=False)
    
    # Relationships
    user = db.relationship("User", back_populates="crisis_incidents")
    therapy_sessions = db.relationship("CrisisTherapySession", back_populates="incident")
    notifications = db.relationship("CrisisNotification", back_populates="incident")
    
    def __repr__(self):
        return f'<CrisisIncident {self.id}: {self.crisis_level} - {self.incident_type}>'

class EmergencyContact(db.Model):
    """Model for storing user emergency contacts"""
    __tablename__ = 'emergency_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contact_name = db.Column(db.String(100), nullable=False)
    relationship = db.Column(db.String(50), nullable=False)  # parent, sibling, friend, etc.
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True)
    is_primary = db.Column(db.Boolean, default=False, nullable=False)
    notification_preferences = db.Column(db.JSON, nullable=True)  # email, sms, phone
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship("User", back_populates="emergency_contacts")
    notifications = db.relationship("CrisisNotification", back_populates="contact")
    
    def __repr__(self):
        return f'<EmergencyContact {self.contact_name} ({self.relationship})>'

class CrisisTherapySession(db.Model):
    """Model for crisis therapy sessions"""
    __tablename__ = 'crisis_therapy_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('crisis_incidents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    therapist_id = db.Column(db.String(50), nullable=False)
    therapist_name = db.Column(db.String(100), nullable=False)
    session_type = db.Column(db.String(50), nullable=False)  # crisis_intervention, emergency_consultation
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=60, nullable=False)
    priority = db.Column(db.String(20), nullable=False)  # critical, high, medium, low
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, completed, cancelled
    auto_booked = db.Column(db.Boolean, default=False, nullable=False)
    crisis_types = db.Column(db.JSON, nullable=True)  # List of crisis types
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incident = db.relationship("CrisisIncident", back_populates="therapy_sessions")
    user = db.relationship("User", back_populates="crisis_therapy_sessions")
    
    def __repr__(self):
        return f'<CrisisTherapySession {self.id}: {self.therapist_name} - {self.scheduled_time}>'

class CrisisNotification(db.Model):
    """Model for tracking crisis notifications sent to contacts"""
    __tablename__ = 'crisis_notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('crisis_incidents.id'), nullable=False)
    contact_id = db.Column(db.Integer, db.ForeignKey('emergency_contacts.id'), nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # email, sms, phone
    message_content = db.Column(db.Text, nullable=True)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    delivery_status = db.Column(db.String(20), default='sent', nullable=False)  # sent, delivered, failed
    response_received = db.Column(db.Boolean, default=False, nullable=False)
    response_content = db.Column(db.Text, nullable=True)
    
    # Relationships
    incident = db.relationship("CrisisIncident", back_populates="notifications")
    contact = db.relationship("EmergencyContact", back_populates="notifications")
    
    def __repr__(self):
        return f'<CrisisNotification {self.id}: {self.notification_type} to {self.contact.contact_name}>'

class CrisisResource(db.Model):
    """Model for storing crisis resources and hotlines"""
    __tablename__ = 'crisis_resources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(20), nullable=True)
    text_line = db.Column(db.String(50), nullable=True)
    website = db.Column(db.String(200), nullable=True)
    availability = db.Column(db.String(100), nullable=True)  # 24/7, business hours, etc.
    crisis_types = db.Column(db.JSON, nullable=True)  # Types of crises this resource handles
    region = db.Column(db.String(100), nullable=True)  # National, state, local
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    priority = db.Column(db.Integer, default=1, nullable=False)  # 1 = highest priority
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def __repr__(self):
        return f'<CrisisResource {self.name}>'

class WellnessCheck(db.Model):
    """Model for scheduling and tracking wellness checks"""
    __tablename__ = 'wellness_checks'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    incident_id = db.Column(db.Integer, db.ForeignKey('crisis_incidents.id'), nullable=True)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    check_type = db.Column(db.String(50), nullable=False)  # automated, manual, follow_up
    status = db.Column(db.String(20), default='scheduled', nullable=False)  # scheduled, completed, missed
    check_method = db.Column(db.String(20), nullable=False)  # email, sms, phone, in_app
    questions = db.Column(db.JSON, nullable=True)  # Wellness check questions
    responses = db.Column(db.JSON, nullable=True)  # User responses
    risk_level = db.Column(db.String(20), nullable=True)  # low, medium, high
    follow_up_required = db.Column(db.Boolean, default=False, nullable=False)
    completed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    user = db.relationship("User")
    incident = db.relationship("CrisisIncident")
    
    def __repr__(self):
        return f'<WellnessCheck {self.id}: {self.check_type} for user {self.user_id}>'

class CrisisPattern(db.Model):
    """Model for storing crisis detection patterns and keywords"""
    __tablename__ = 'crisis_patterns'
    
    id = db.Column(db.Integer, primary_key=True)
    pattern_name = db.Column(db.String(100), nullable=False)
    crisis_type = db.Column(db.String(50), nullable=False)
    keywords = db.Column(db.JSON, nullable=False)  # List of keywords
    phrases = db.Column(db.JSON, nullable=True)  # List of phrases
    context_indicators = db.Column(db.JSON, nullable=True)  # Context indicators
    severity_threshold = db.Column(db.Float, default=0.5, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrisisPattern {self.pattern_name}: {self.crisis_type}>'

# Update User model to include relationships
def add_crisis_relationships_to_user():
    """Add crisis-related relationships to User model"""
    # This would be added to the existing User model
    pass

# Crisis detection configuration
class CrisisConfig(db.Model):
    """Model for crisis detection configuration"""
    __tablename__ = 'crisis_config'
    
    id = db.Column(db.Integer, primary_key=True)
    config_name = db.Column(db.String(100), nullable=False, unique=True)
    config_value = db.Column(db.JSON, nullable=False)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<CrisisConfig {self.config_name}>'
