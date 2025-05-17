"""
Counseling and Therapy Booking Routes

This module provides functionality for:
- Viewing booked therapy sessions
- Finding nearby therapists
- Booking new sessions
- Managing therapy appointments
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models import db
from datetime import datetime, timedelta
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create blueprint
counseling_bp = Blueprint('counseling', __name__, url_prefix='/counseling')

@counseling_bp.route('/booking')
@login_required
def booking():
    """Display therapy session booking page with nearby therapists and booked sessions"""
    try:
        # Get user's booked sessions (mock data for now)
        booked_sessions = get_user_booked_sessions(current_user.id)
        
        # Get nearby therapists (mock data for now)
        nearby_therapists = get_nearby_therapists()
        
        # Get available time slots for the selected date (default to today)
        selected_date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        available_slots = get_available_time_slots(selected_date)
        
        return render_template('counseling/booking.html', 
                             booked_sessions=booked_sessions,
                             nearby_therapists=nearby_therapists,
                             available_slots=available_slots,
                             selected_date=selected_date)
        
    except Exception as e:
        logger.error(f"Error in counseling booking: {str(e)}")
        flash('An error occurred while loading the booking page.', 'error')
        return redirect(url_for('index'))

@counseling_bp.route('/book-session', methods=['POST'])
@login_required
def book_session():
    """Book a new therapy session"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['therapist_id', 'date', 'time', 'session_type']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create booking (mock implementation)
        booking_data = {
            'user_id': current_user.id,
            'therapist_id': data['therapist_id'],
            'date': data['date'],
            'time': data['time'],
            'session_type': data['session_type'],
            'status': 'confirmed',
            'created_at': '2024-01-20T10:00:00'
        }
        
        # In a real implementation, you would save this to the database
        logger.info(f"New booking created: {booking_data}")
        
        return jsonify({
            'success': True,
            'message': 'Session booked successfully!',
            'booking_id': f"BK20240120100000"
        })
        
    except Exception as e:
        logger.error(f"Error booking session: {str(e)}")
        return jsonify({'error': 'Failed to book session. Please try again.'}), 500

@counseling_bp.route('/cancel-session/<booking_id>', methods=['POST'])
@login_required
def cancel_session(booking_id):
    """Cancel a booked therapy session"""
    try:
        # In a real implementation, you would update the database
        logger.info(f"Session {booking_id} cancelled by user {current_user.id}")
        
        return jsonify({
            'success': True,
            'message': 'Session cancelled successfully!'
        })
        
    except Exception as e:
        logger.error(f"Error cancelling session: {str(e)}")
        return jsonify({'error': 'Failed to cancel session. Please try again.'}), 500

@counseling_bp.route('/booking-debug')
def booking_debug():
    """Debug version of booking page without authentication"""
    # Simple mock data
    booked_sessions = [
        {
            'id': 'BK001',
            'therapist_name': 'Dr. Priya Sharma',
            'therapist_specialty': 'Anxiety & Depression',
            'date': '2024-01-15',
            'time': '10:00 AM',
            'session_type': 'Individual Therapy',
            'status': 'confirmed',
            'location': 'Online',
            'duration': '50 minutes'
        }
    ]
    
    nearby_therapists = [
        {
            'id': 'T001',
            'name': 'Dr. Priya Sharma',
            'specialty': 'Anxiety & Depression',
            'experience': '8 years',
            'rating': 4.8,
            'price_per_session': '₹2,500',
            'location': 'Mumbai, Maharashtra',
            'distance': '2.5 km',
            'availability': 'Mon-Fri, 9 AM - 6 PM',
            'languages': ['Hindi', 'English', 'Marathi'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Specialized in treating anxiety disorders and depression with CBT and mindfulness techniques.'
        }
    ]
    
    available_slots = ['09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM', '02:00 PM', '03:00 PM']
    selected_date = datetime.now().strftime('%Y-%m-%d')
    
    return render_template('counseling/booking.html', 
                         booked_sessions=booked_sessions,
                         nearby_therapists=nearby_therapists,
                         available_slots=available_slots,
                         selected_date=selected_date)

@counseling_bp.route('/therapist/<therapist_id>')
@login_required
def therapist_details(therapist_id):
    """View detailed information about a specific therapist"""
    try:
        therapist = get_therapist_details(therapist_id)
        if not therapist:
            flash('Therapist not found.', 'error')
            return redirect(url_for('counseling.booking'))
        
        return render_template('counseling/therapist_details.html', therapist=therapist)
        
    except Exception as e:
        logger.error(f"Error loading therapist details: {str(e)}")
        flash('An error occurred while loading therapist details.', 'error')
        return redirect(url_for('counseling.booking'))

def get_user_booked_sessions(user_id):
    """Get user's booked therapy sessions (mock data)"""
    # Mock data - in real implementation, query database
    return [
        {
            'id': 'BK001',
            'therapist_name': 'Dr. Priya Sharma',
            'therapist_specialty': 'Anxiety & Depression',
            'date': '2024-01-15',
            'time': '10:00 AM',
            'session_type': 'Individual Therapy',
            'status': 'confirmed',
            'location': 'Online',
            'duration': '50 minutes'
        },
        {
            'id': 'BK002',
            'therapist_name': 'Dr. Rajesh Kumar',
            'therapist_specialty': 'Family Counseling',
            'date': '2024-01-18',
            'time': '2:00 PM',
            'session_type': 'Couples Therapy',
            'status': 'pending',
            'location': 'Clinic - Mumbai',
            'duration': '60 minutes'
        },
        {
            'id': 'BK003',
            'therapist_name': 'Dr. Anjali Mehta',
            'therapist_specialty': 'Trauma Therapy',
            'date': '2024-01-20',
            'time': '11:30 AM',
            'session_type': 'Individual Therapy',
            'status': 'completed',
            'location': 'Online',
            'duration': '50 minutes'
        }
    ]

def get_nearby_therapists():
    """Get list of nearby therapists (mock data)"""
    # Mock data - in real implementation, query database with location
    return [
        {
            'id': 'T001',
            'name': 'Dr. Priya Sharma',
            'specialty': 'Anxiety & Depression',
            'experience': '8 years',
            'rating': 4.8,
            'price_per_session': '₹2,500',
            'location': 'Mumbai, Maharashtra',
            'distance': '2.5 km',
            'availability': 'Mon-Fri, 9 AM - 6 PM',
            'languages': ['Hindi', 'English', 'Marathi'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Specialized in treating anxiety disorders and depression with CBT and mindfulness techniques.'
        },
        {
            'id': 'T002',
            'name': 'Dr. Rajesh Kumar',
            'specialty': 'Family Counseling',
            'experience': '12 years',
            'rating': 4.9,
            'price_per_session': '₹3,000',
            'location': 'Delhi, NCR',
            'distance': '5.2 km',
            'availability': 'Tue-Sat, 10 AM - 7 PM',
            'languages': ['Hindi', 'English', 'Punjabi'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Expert in family dynamics, relationship counseling, and adolescent therapy.'
        },
        {
            'id': 'T003',
            'name': 'Dr. Anjali Mehta',
            'specialty': 'Trauma Therapy',
            'experience': '10 years',
            'rating': 4.7,
            'price_per_session': '₹3,500',
            'location': 'Bangalore, Karnataka',
            'distance': '3.8 km',
            'availability': 'Mon-Thu, 9 AM - 5 PM',
            'languages': ['Hindi', 'English', 'Kannada'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Specialized in trauma recovery, PTSD treatment, and EMDR therapy.'
        },
        {
            'id': 'T004',
            'name': 'Dr. Vikram Singh',
            'specialty': 'Addiction Counseling',
            'experience': '15 years',
            'rating': 4.6,
            'price_per_session': '₹2,800',
            'location': 'Pune, Maharashtra',
            'distance': '7.1 km',
            'availability': 'Mon-Fri, 8 AM - 6 PM',
            'languages': ['Hindi', 'English', 'Marathi'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Expert in addiction recovery, substance abuse counseling, and relapse prevention.'
        },
        {
            'id': 'T005',
            'name': 'Dr. Smita Patel',
            'specialty': 'Child Psychology',
            'experience': '6 years',
            'rating': 4.9,
            'price_per_session': '₹2,200',
            'location': 'Ahmedabad, Gujarat',
            'distance': '4.3 km',
            'availability': 'Tue-Sat, 10 AM - 6 PM',
            'languages': ['Hindi', 'English', 'Gujarati'],
            'image': 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPGNpcmNsZSBjeD0iNDAiIGN5PSI0MCIgcj0iNDAiIGZpbGw9IiM0QTkwRTIiLz4KPHRleHQgeD0iNDAiIHk9IjQ1IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSJ3aGl0ZSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmb250LXdlaWdodD0iYm9sZCI+RFI8L3RleHQ+Cjwvc3ZnPg==',
            'description': 'Specialized in child and adolescent psychology, behavioral issues, and learning disabilities.'
        }
    ]

def get_available_time_slots(date):
    """Get available time slots for a specific date (mock data)"""
    # Mock data - in real implementation, check actual availability
    base_slots = [
        '09:00 AM', '10:00 AM', '11:00 AM', '12:00 PM',
        '02:00 PM', '03:00 PM', '04:00 PM', '05:00 PM'
    ]
    
    # Simulate some slots being booked
    import random
    available_slots = [slot for slot in base_slots if random.random() > 0.3]
    
    return available_slots

def get_therapist_details(therapist_id):
    """Get detailed information about a specific therapist"""
    therapists = get_nearby_therapists()
    for therapist in therapists:
        if therapist['id'] == therapist_id:
            return therapist
    return None

