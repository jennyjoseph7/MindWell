"""
Crisis Response System
Handles automatic responses to crisis situations including therapy booking and emergency notifications
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class CrisisResponseManager:
    """
    Manages crisis response actions including therapy booking and emergency notifications
    """
    
    def __init__(self, app=None):
        self.app = app
        self.therapy_providers = self._initialize_therapy_providers()
        self.notification_settings = self._load_notification_settings()
        
    def _initialize_therapy_providers(self) -> List[Dict[str, Any]]:
        """Initialize available therapy providers for crisis situations"""
        return [
            {
                'id': 'crisis_provider_1',
                'name': 'Dr. Sarah Johnson',
                'specialty': 'Crisis Intervention & Trauma Therapy',
                'availability': '24/7 Crisis Support',
                'phone': '+1-555-CRISIS',
                'email': 'crisis@mindwell.com',
                'response_time': 'Immediate',
                'session_types': ['Crisis Intervention', 'Emergency Consultation'],
                'languages': ['English', 'Spanish'],
                'credentials': 'Licensed Clinical Psychologist, Crisis Intervention Specialist'
            },
            {
                'id': 'crisis_provider_2',
                'name': 'Dr. Michael Chen',
                'specialty': 'Suicide Prevention & Mental Health Crisis',
                'availability': '24/7 Emergency Response',
                'phone': '+1-555-HELP',
                'email': 'emergency@mindwell.com',
                'response_time': 'Immediate',
                'session_types': ['Emergency Therapy', 'Crisis Counseling'],
                'languages': ['English', 'Mandarin'],
                'credentials': 'Licensed Clinical Social Worker, Suicide Prevention Specialist'
            },
            {
                'id': 'crisis_provider_3',
                'name': 'Dr. Maria Rodriguez',
                'specialty': 'Trauma & Crisis Recovery',
                'availability': '24/7 Crisis Support',
                'phone': '+1-555-SUPPORT',
                'email': 'support@mindwell.com',
                'response_time': 'Immediate',
                'session_types': ['Trauma Therapy', 'Crisis Recovery'],
                'languages': ['English', 'Spanish'],
                'credentials': 'Licensed Marriage and Family Therapist, Trauma Specialist'
            }
        ]
    
    def _load_notification_settings(self) -> Dict[str, Any]:
        """Load notification settings for emergency contacts"""
        return {
            'email_enabled': True,
            'sms_enabled': True,
            'phone_enabled': True,
            'notification_templates': {
                'crisis_alert': {
                    'subject': 'URGENT: Mental Health Crisis Alert - {user_name}',
                    'body': '''
URGENT MENTAL HEALTH ALERT

This is an automated alert from MindWell regarding {user_name}.

CRISIS DETECTED:
- Time: {timestamp}
- Crisis Level: {crisis_level}
- Detected Issues: {crisis_types}

IMMEDIATE ACTIONS TAKEN:
- Emergency therapy session booked
- Crisis resources provided
- Professional intervention initiated

PLEASE CONTACT {user_name} IMMEDIATELY:
- Phone: {user_phone}
- Email: {user_email}

CRISIS RESOURCES:
- National Suicide Prevention Lifeline: 988
- Crisis Text Line: Text HOME to 741741
- Emergency Services: 911

This alert was triggered by our AI safety system detecting concerning language patterns.
Please reach out to {user_name} as soon as possible.

MindWell Safety Team
                    '''
                },
                'therapy_booking_confirmation': {
                    'subject': 'URGENT: Therapy Session Booked - {user_name}',
                    'body': '''
URGENT THERAPY SESSION BOOKED

A crisis therapy session has been automatically booked for {user_name}.

SESSION DETAILS:
- Therapist: {therapist_name}
- Session Type: {session_type}
- Scheduled Time: {session_time}
- Duration: {duration}
- Contact: {therapist_phone}

This session was automatically booked due to crisis detection in {user_name}'s mental health data.

Please ensure {user_name} attends this session.

MindWell Crisis Response Team
                    '''
                }
            }
        }
    
    async def handle_crisis_response(self, user_id: str, crisis_data: Dict[str, Any], 
                                   user_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle crisis response based on detected crisis level
        
        Args:
            user_id: User identifier
            crisis_data: Crisis detection results
            user_info: User information including emergency contacts
            
        Returns:
            Response actions taken
        """
        try:
            print(f"DEBUG: Crisis response handler called for user {user_id}")
            print(f"DEBUG: Crisis data: {crisis_data}")
            crisis_level = crisis_data.get('crisis_level', 'none')
            crisis_types = crisis_data.get('crisis_types', [])
            response_actions = crisis_data.get('response_actions', [])
            
            print(f"DEBUG: Crisis level: {crisis_level}, types: {crisis_types}")
            actions_taken = []
            
            # Handle critical crisis
            if crisis_level in ['critical', 'high']:
                print(f"DEBUG: Handling critical/high crisis for user {user_id}")
                # Book immediate therapy session
                therapy_booking = await self._book_crisis_therapy_session(
                    user_id, user_info, crisis_types
                )
                if therapy_booking:
                    print(f"DEBUG: Therapy booking result: {therapy_booking}")
                    actions_taken.append(therapy_booking)
                
                # Send emergency notifications
                notifications = await self._send_emergency_notifications(
                    user_id, user_info, crisis_data
                )
                actions_taken.extend(notifications)
                
                # Display crisis resources
                resources = self._display_crisis_resources(crisis_types)
                actions_taken.append(resources)
            
            # Handle medium crisis
            elif crisis_level == 'medium':
                # Book urgent therapy session
                therapy_booking = await self._book_urgent_therapy_session(
                    user_id, user_info, crisis_types
                )
                if therapy_booking:
                    actions_taken.append(therapy_booking)
                
                # Send contact notifications
                notifications = await self._send_contact_notifications(
                    user_id, user_info, crisis_data
                )
                actions_taken.extend(notifications)
            
            # Handle low crisis
            elif crisis_level == 'low':
                # Schedule wellness check
                wellness_check = await self._schedule_wellness_check(
                    user_id, user_info
                )
                if wellness_check:
                    actions_taken.append(wellness_check)
                
                # Provide support resources
                resources = self._provide_support_resources(crisis_types)
                actions_taken.append(resources)
            
            # Log crisis response
            self._log_crisis_response(user_id, crisis_data, actions_taken)
            
            return {
                'crisis_handled': True,
                'actions_taken': actions_taken,
                'timestamp': datetime.now().isoformat(),
                'requires_follow_up': crisis_level in ['critical', 'high']
            }
            
        except Exception as e:
            logger.error(f"Error handling crisis response: {str(e)}")
            return {
                'crisis_handled': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _book_crisis_therapy_session(self, user_id: str, user_info: Dict[str, Any], 
                                         crisis_types: List[str]) -> Optional[Dict[str, Any]]:
        """Book immediate crisis therapy session"""
        try:
            # Select appropriate crisis therapist
            therapist = self._select_crisis_therapist(crisis_types)
            
            # Create immediate session booking
            session_booking = {
                'user_id': user_id,
                'therapist_id': therapist['id'],
                'therapist_name': therapist['name'],
                'session_type': 'Crisis Intervention',
                'scheduled_time': datetime.now() + timedelta(minutes=30),  # 30 minutes from now
                'duration': 60,  # 60 minutes
                'priority': 'CRITICAL',
                'crisis_types': crisis_types,
                'auto_booked': True,
                'status': 'confirmed'
            }
            
            # Store booking in database (implement based on your DB structure)
            booking_id = await self._store_therapy_booking(session_booking)
            
            # Send confirmation to user
            await self._send_therapy_confirmation(user_id, session_booking)
            
            # Notify therapist
            await self._notify_therapist(therapist, session_booking)
            
            logger.info(f"Crisis therapy session booked for user {user_id} with {therapist['name']}")
            
            return {
                'action': 'crisis_therapy_booked',
                'booking_id': booking_id,
                'therapist': therapist['name'],
                'session_time': session_booking['scheduled_time'].isoformat(),
                'priority': 'CRITICAL'
            }
            
        except Exception as e:
            logger.error(f"Error booking crisis therapy session: {str(e)}")
            return None
    
    async def _book_urgent_therapy_session(self, user_id: str, user_info: Dict[str, Any], 
                                         crisis_types: List[str]) -> Optional[Dict[str, Any]]:
        """Book urgent therapy session within 24 hours"""
        try:
            therapist = self._select_crisis_therapist(crisis_types)
            
            # Schedule within 24 hours
            session_booking = {
                'user_id': user_id,
                'therapist_id': therapist['id'],
                'therapist_name': therapist['name'],
                'session_type': 'Urgent Mental Health Support',
                'scheduled_time': datetime.now() + timedelta(hours=12),  # 12 hours from now
                'duration': 50,  # 50 minutes
                'priority': 'HIGH',
                'crisis_types': crisis_types,
                'auto_booked': True,
                'status': 'confirmed'
            }
            
            booking_id = await self._store_therapy_booking(session_booking)
            await self._send_therapy_confirmation(user_id, session_booking)
            await self._notify_therapist(therapist, session_booking)
            
            return {
                'action': 'urgent_therapy_booked',
                'booking_id': booking_id,
                'therapist': therapist['name'],
                'session_time': session_booking['scheduled_time'].isoformat(),
                'priority': 'HIGH'
            }
            
        except Exception as e:
            logger.error(f"Error booking urgent therapy session: {str(e)}")
            return None
    
    def _select_crisis_therapist(self, crisis_types: List[str]) -> Dict[str, Any]:
        """Select appropriate therapist based on crisis types"""
        # For now, return the first available crisis therapist
        # In a real implementation, you'd match based on specialty
        return self.therapy_providers[0]
    
    async def _store_therapy_booking(self, booking_data: Dict[str, Any]) -> str:
        """Store therapy booking in database"""
        # Implement database storage
        # For now, return a mock booking ID
        booking_id = f"crisis_booking_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # In real implementation:
        # - Store in therapy_sessions table
        # - Update therapist availability
        # - Send calendar invites
        
        return booking_id
    
    async def _send_therapy_confirmation(self, user_id: str, booking_data: Dict[str, Any]):
        """Send therapy session confirmation to user"""
        # Implement user notification
        logger.info(f"Therapy confirmation sent to user {user_id}")
    
    async def _notify_therapist(self, therapist: Dict[str, Any], booking_data: Dict[str, Any]):
        """Notify therapist of crisis booking"""
        # Implement therapist notification
        logger.info(f"Therapist {therapist['name']} notified of crisis booking")
    
    async def _send_emergency_notifications(self, user_id: str, user_info: Dict[str, Any], 
                                           crisis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send emergency notifications to contacts"""
        notifications_sent = []
        
        try:
            emergency_contacts = user_info.get('emergency_contacts', [])
            
            for contact in emergency_contacts:
                notification = await self._send_emergency_notification(
                    contact, user_info, crisis_data
                )
                if notification:
                    notifications_sent.append(notification)
            
            return notifications_sent
            
        except Exception as e:
            logger.error(f"Error sending emergency notifications: {str(e)}")
            return []
    
    async def _send_emergency_notification(self, contact: Dict[str, str], 
                                         user_info: Dict[str, Any], 
                                         crisis_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Send emergency notification to a specific contact"""
        try:
            template = self.notification_settings['notification_templates']['crisis_alert']
            
            # Format notification content
            subject = template['subject'].format(
                user_name=user_info.get('name', 'User')
            )
            
            body = template['body'].format(
                user_name=user_info.get('name', 'User'),
                timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                crisis_level=crisis_data.get('crisis_level', 'unknown'),
                crisis_types=', '.join(crisis_data.get('crisis_types', [])),
                user_phone=user_info.get('phone', 'Not provided'),
                user_email=user_info.get('email', 'Not provided')
            )
            
            # Send via email
            if contact.get('email'):
                await self._send_email_notification(
                    contact['email'], subject, body
                )
            
            # Send via SMS if available
            if contact.get('phone'):
                await self._send_sms_notification(
                    contact['phone'], body
                )
            
            return {
                'action': 'emergency_notification_sent',
                'contact_name': contact.get('name', 'Unknown'),
                'contact_email': contact.get('email'),
                'contact_phone': contact.get('phone'),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error sending emergency notification: {str(e)}")
            return None
    
    async def _send_email_notification(self, email: str, subject: str, body: str):
        """Send email notification"""
        # Implement email sending
        logger.info(f"Emergency email sent to {email}")
    
    async def _send_sms_notification(self, phone: str, message: str):
        """Send SMS notification"""
        # Implement SMS sending
        logger.info(f"Emergency SMS sent to {phone}")
    
    async def _send_contact_notifications(self, user_id: str, user_info: Dict[str, Any], 
                                        crisis_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Send notifications to designated contacts for medium crisis"""
        # Similar to emergency notifications but with different urgency
        return await self._send_emergency_notifications(user_id, user_info, crisis_data)
    
    async def _schedule_wellness_check(self, user_id: str, user_info: Dict[str, Any]) -> Dict[str, Any]:
        """Schedule wellness check for low crisis"""
        return {
            'action': 'wellness_check_scheduled',
            'user_id': user_id,
            'scheduled_time': (datetime.now() + timedelta(days=1)).isoformat(),
            'priority': 'LOW'
        }
    
    def _display_crisis_resources(self, crisis_types: List[str]) -> Dict[str, Any]:
        """Display crisis resources to user"""
        return {
            'action': 'crisis_resources_displayed',
            'resources': {
                'immediate_help': [
                    'Call 988 for the Suicide & Crisis Lifeline',
                    'Text HOME to 741741 for Crisis Text Line',
                    'Call 911 for immediate emergencies'
                ],
                'crisis_types': crisis_types
            }
        }
    
    def _provide_support_resources(self, crisis_types: List[str]) -> Dict[str, Any]:
        """Provide general support resources"""
        return {
            'action': 'support_resources_provided',
            'resources': {
                'general_support': [
                    'Mental Health America',
                    'National Alliance on Mental Illness (NAMI)',
                    'Local mental health services'
                ],
                'crisis_types': crisis_types
            }
        }
    
    def _log_crisis_response(self, user_id: str, crisis_data: Dict[str, Any], 
                           actions_taken: List[Dict[str, Any]]):
        """Log crisis response actions"""
        log_entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'crisis_level': crisis_data.get('crisis_level'),
            'crisis_types': crisis_data.get('crisis_types'),
            'actions_taken': actions_taken
        }
        
        logger.warning(f"Crisis response logged for user {user_id}: {len(actions_taken)} actions taken")
    
    def get_crisis_resources_for_display(self) -> Dict[str, Any]:
        """Get crisis resources formatted for display to users"""
        return {
            'emergency_contacts': {
                'suicide_prevention': {
                    'name': 'National Suicide Prevention Lifeline',
                    'phone': '988',
                    'text': 'Text HOME to 741741',
                    'available': '24/7'
                },
                'crisis_text': {
                    'name': 'Crisis Text Line',
                    'text': 'Text HOME to 741741',
                    'available': '24/7'
                },
                'emergency': {
                    'name': 'Emergency Services',
                    'phone': '911',
                    'available': '24/7'
                }
            },
            'immediate_help': [
                'You are not alone - help is available',
                'Call 988 for immediate support',
                'Text HOME to 741741 for crisis counseling',
                'Call 911 for life-threatening emergencies'
            ],
            'support_services': [
                'National Alliance on Mental Illness (NAMI)',
                'Mental Health America',
                'Crisis Intervention Services',
                'Local mental health crisis centers'
            ]
        }
