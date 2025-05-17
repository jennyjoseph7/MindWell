"""
Crisis Detection and Response System
Handles detection of crisis situations and automatic response protocols
"""

import re
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)

class CrisisLevel(Enum):
    """Crisis severity levels"""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CrisisType(Enum):
    """Types of crisis situations"""
    SUICIDAL_IDEATION = "suicidal_ideation"
    SELF_HARM = "self_harm"
    EXTREME_STRESS = "extreme_stress"
    SUBSTANCE_ABUSE = "substance_abuse"
    VIOLENCE = "violence"
    EATING_DISORDER = "eating_disorder"

class CrisisDetector:
    """
    Advanced crisis detection system for mental health applications
    """
    
    def __init__(self):
        self.crisis_patterns = self._initialize_crisis_patterns()
        self.emergency_contacts = {}
        self.crisis_history = {}
        
    def _initialize_crisis_patterns(self) -> Dict[CrisisType, Dict[str, List[str]]]:
        """Initialize comprehensive crisis detection patterns"""
        return {
            CrisisType.SUICIDAL_IDEATION: {
                'keywords': [
                    'suicide', 'kill myself', 'end it all', 'not worth living',
                    'better off dead', 'want to die', 'end my life', 'take my life',
                    'suicidal', 'self-harm', 'hurt myself', 'cut myself',
                    'overdose', 'jump off', 'hang myself', 'shoot myself',
                    'pills', 'bleeding', 'cutting', 'burning'
                ],
                'phrases': [
                    'i want to die', 'i should die', 'i wish i was dead',
                    'nobody would miss me', 'everyone would be better off',
                    'i have a plan', 'i know how to do it', 'i have the means',
                    'this is goodbye', 'see you never', 'final goodbye'
                ],
                'context_indicators': [
                    'planning', 'method', 'means', 'when', 'where', 'how'
                ]
            },
            CrisisType.SELF_HARM: {
                'keywords': [
                    'cut', 'cutting', 'burn', 'burning', 'scratch', 'scratching',
                    'hurt myself', 'harm myself', 'bleeding', 'blood',
                    'razor', 'knife', 'sharp', 'pain', 'punish myself'
                ],
                'phrases': [
                    'i cut myself', 'i hurt myself', 'i burn myself',
                    'i scratch myself', 'i made myself bleed',
                    'i deserve pain', 'i need to feel pain'
                ],
                'context_indicators': [
                    'wounds', 'scars', 'bandages', 'hiding', 'secret'
                ]
            },
            CrisisType.EXTREME_STRESS: {
                'keywords': [
                    'overwhelmed', 'can\'t cope', 'breaking down', 'falling apart',
                    'losing control', 'panic', 'anxiety attack', 'meltdown',
                    'crisis', 'emergency', 'help me', 'i can\'t do this',
                    'too much', 'breaking point', 'snap', 'lose it'
                ],
                'phrases': [
                    'i can\'t handle this', 'i\'m falling apart',
                    'i\'m losing my mind', 'i\'m having a breakdown',
                    'i need help now', 'i can\'t cope anymore',
                    'this is too much', 'i\'m overwhelmed'
                ],
                'context_indicators': [
                    'crying', 'screaming', 'panic', 'hyperventilating',
                    'can\'t breathe', 'chest pain', 'dizzy'
                ]
            },
            CrisisType.SUBSTANCE_ABUSE: {
                'keywords': [
                    'overdose', 'too many pills', 'mixing drugs', 'alcohol poisoning',
                    'blackout', 'passed out', 'unconscious', 'hospital',
                    'ambulance', 'emergency room', 'narcan', 'naloxone'
                ],
                'phrases': [
                    'i took too many', 'i mixed too much', 'i can\'t wake up',
                    'i think i overdosed', 'i need help', 'call 911'
                ],
                'context_indicators': [
                    'slurred speech', 'confusion', 'vomiting', 'seizure'
                ]
            },
            CrisisType.VIOLENCE: {
                'keywords': [
                    'hurt someone', 'kill someone', 'attack', 'violence',
                    'fight', 'weapon', 'gun', 'knife', 'threaten',
                    'revenge', 'payback', 'get even'
                ],
                'phrases': [
                    'i want to hurt', 'i could kill', 'i have a gun',
                    'i\'m going to hurt', 'they deserve it'
                ],
                'context_indicators': [
                    'weapon', 'planning', 'threat', 'anger'
                ]
            },
            CrisisType.EATING_DISORDER: {
                'keywords': [
                    'starving', 'not eating', 'purging', 'vomiting',
                    'laxatives', 'diet pills', 'fainting', 'weak',
                    'hospital', 'medical emergency'
                ],
                'phrases': [
                    'i haven\'t eaten', 'i can\'t eat', 'i\'m purging',
                    'i\'m fainting', 'i feel weak', 'i need help'
                ],
                'context_indicators': [
                    'weight loss', 'fainting', 'weakness', 'medical'
                ]
            }
        }
    
    def detect_crisis(self, text: str, user_id: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Detect crisis situations in text input
        
        Args:
            text: The text to analyze
            user_id: User identifier
            context: Additional context about the user/session
            
        Returns:
            Crisis detection results
        """
        try:
            # Normalize text for analysis
            normalized_text = self._normalize_text(text)
            
            # Detect crisis types and severity
            crisis_results = {}
            max_severity = CrisisLevel.NONE
            detected_types = []
            
            for crisis_type, patterns in self.crisis_patterns.items():
                severity, confidence = self._analyze_crisis_type(
                    normalized_text, crisis_type, patterns, context
                )
                
                if severity != CrisisLevel.NONE:
                    crisis_results[crisis_type.value] = {
                        'severity': severity.value,
                        'confidence': confidence,
                        'matched_patterns': self._get_matched_patterns(normalized_text, patterns)
                    }
                    detected_types.append(crisis_type)
                    
                    # Update max severity
                    if self._compare_severity(severity, max_severity) > 0:
                        max_severity = severity
            
            # Determine overall crisis level
            overall_crisis_level = self._determine_overall_crisis_level(
                max_severity, detected_types, context
            )
            
            # Generate response recommendations
            response_actions = self._generate_response_actions(
                overall_crisis_level, detected_types, crisis_results
            )
            
            # Log crisis detection
            self._log_crisis_detection(user_id, text, overall_crisis_level, detected_types)
            
            return {
                'crisis_detected': overall_crisis_level != CrisisLevel.NONE,
                'crisis_level': overall_crisis_level.value,
                'crisis_types': [t.value for t in detected_types],
                'detailed_results': crisis_results,
                'response_actions': response_actions,
                'timestamp': datetime.now().isoformat(),
                'requires_immediate_action': overall_crisis_level in [CrisisLevel.HIGH, CrisisLevel.CRITICAL]
            }
            
        except Exception as e:
            logger.error(f"Error in crisis detection: {str(e)}")
            return {
                'crisis_detected': False,
                'crisis_level': CrisisLevel.NONE.value,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove punctuation for some patterns
        text = re.sub(r'[^\w\s]', ' ', text)
        
        return text.strip()
    
    def _analyze_crisis_type(self, text: str, crisis_type: CrisisType, 
                           patterns: Dict[str, List[str]], context: Dict[str, Any] = None) -> Tuple[CrisisLevel, float]:
        """Analyze text for specific crisis type"""
        severity = CrisisLevel.NONE
        confidence = 0.0
        
        # Check keywords
        keyword_matches = 0
        for keyword in patterns['keywords']:
            if keyword in text:
                keyword_matches += 1
        
        # Check phrases
        phrase_matches = 0
        for phrase in patterns['phrases']:
            if phrase in text:
                phrase_matches += 1
        
        # Check context indicators
        context_matches = 0
        if context:
            context_text = ' '.join([str(v) for v in context.values() if isinstance(v, str)]).lower()
            for indicator in patterns['context_indicators']:
                if indicator in context_text:
                    context_matches += 1
        
        # Calculate severity based on matches
        total_matches = keyword_matches + phrase_matches + context_matches
        
        if total_matches == 0:
            return CrisisLevel.NONE, 0.0
        
        # Weight phrase matches more heavily
        weighted_score = keyword_matches + (phrase_matches * 2) + context_matches
        
        if weighted_score >= 3:
            severity = CrisisLevel.CRITICAL
            confidence = min(0.95, 0.7 + (weighted_score * 0.05))
        elif weighted_score >= 2:
            severity = CrisisLevel.HIGH
            confidence = min(0.9, 0.6 + (weighted_score * 0.05))
        elif weighted_score >= 1:
            severity = CrisisLevel.MEDIUM
            confidence = min(0.8, 0.4 + (weighted_score * 0.1))
        else:
            severity = CrisisLevel.LOW
            confidence = 0.3
        
        return severity, confidence
    
    def _get_matched_patterns(self, text: str, patterns: Dict[str, List[str]]) -> List[str]:
        """Get list of matched patterns"""
        matched = []
        
        for keyword in patterns['keywords']:
            if keyword in text:
                matched.append(f"keyword: {keyword}")
        
        for phrase in patterns['phrases']:
            if phrase in text:
                matched.append(f"phrase: {phrase}")
        
        return matched
    
    def _compare_severity(self, severity1: CrisisLevel, severity2: CrisisLevel) -> int:
        """Compare crisis severity levels"""
        severity_order = {
            CrisisLevel.NONE: 0,
            CrisisLevel.LOW: 1,
            CrisisLevel.MEDIUM: 2,
            CrisisLevel.HIGH: 3,
            CrisisLevel.CRITICAL: 4
        }
        
        return severity_order[severity1] - severity_order[severity2]
    
    def _determine_overall_crisis_level(self, max_severity: CrisisLevel, 
                                      detected_types: List[CrisisType], 
                                      context: Dict[str, Any] = None) -> CrisisLevel:
        """Determine overall crisis level based on multiple factors"""
        
        # Multiple crisis types increase severity
        if len(detected_types) > 1:
            if max_severity == CrisisLevel.MEDIUM:
                return CrisisLevel.HIGH
            elif max_severity == CrisisLevel.HIGH:
                return CrisisLevel.CRITICAL
        
        # Check for escalation patterns
        if context and 'crisis_history' in context:
            recent_crises = context['crisis_history']
            if len(recent_crises) >= 2:
                # Escalating pattern
                return CrisisLevel.CRITICAL if max_severity == CrisisLevel.HIGH else CrisisLevel.HIGH
        
        return max_severity
    
    def _generate_response_actions(self, crisis_level: CrisisLevel, 
                                 detected_types: List[CrisisType], 
                                 crisis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate appropriate response actions based on crisis level"""
        actions = []
        
        if crisis_level == CrisisLevel.CRITICAL:
            actions.extend([
                {
                    'action': 'immediate_therapy_booking',
                    'priority': 'critical',
                    'description': 'Automatically book immediate therapy session'
                },
                {
                    'action': 'emergency_contact_notification',
                    'priority': 'critical',
                    'description': 'Notify emergency contacts immediately'
                },
                {
                    'action': 'crisis_resources_display',
                    'priority': 'high',
                    'description': 'Display crisis resources and hotlines'
                },
                {
                    'action': 'professional_escalation',
                    'priority': 'critical',
                    'description': 'Escalate to mental health professionals'
                }
            ])
        elif crisis_level == CrisisLevel.HIGH:
            actions.extend([
                {
                    'action': 'urgent_therapy_booking',
                    'priority': 'high',
                    'description': 'Book urgent therapy session within 24 hours'
                },
                {
                    'action': 'contact_notification',
                    'priority': 'high',
                    'description': 'Notify designated contacts'
                },
                {
                    'action': 'crisis_resources_display',
                    'priority': 'medium',
                    'description': 'Display crisis resources'
                }
            ])
        elif crisis_level == CrisisLevel.MEDIUM:
            actions.extend([
                {
                    'action': 'therapy_booking',
                    'priority': 'medium',
                    'description': 'Suggest therapy session booking'
                },
                {
                    'action': 'support_resources',
                    'priority': 'medium',
                    'description': 'Provide support resources'
                }
            ])
        elif crisis_level == CrisisLevel.LOW:
            actions.extend([
                {
                    'action': 'wellness_check',
                    'priority': 'low',
                    'description': 'Schedule wellness check'
                },
                {
                    'action': 'support_resources',
                    'priority': 'low',
                    'description': 'Provide general support resources'
                }
            ])
        
        return actions
    
    def _log_crisis_detection(self, user_id: str, text: str, 
                            crisis_level: CrisisLevel, detected_types: List[CrisisType]):
        """Log crisis detection for monitoring and analysis"""
        log_entry = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'crisis_level': crisis_level.value,
            'detected_types': [t.value for t in detected_types],
            'text_length': len(text),
            'has_crisis': crisis_level != CrisisLevel.NONE
        }
        
        # Store in crisis history
        if user_id not in self.crisis_history:
            self.crisis_history[user_id] = []
        
        self.crisis_history[user_id].append(log_entry)
        
        # Keep only last 10 entries per user
        if len(self.crisis_history[user_id]) > 10:
            self.crisis_history[user_id] = self.crisis_history[user_id][-10:]
        
        logger.warning(f"Crisis detected for user {user_id}: {crisis_level.value} - {[t.value for t in detected_types]}")
    
    def get_crisis_resources(self) -> Dict[str, Any]:
        """Get crisis resources and emergency contacts"""
        return {
            'emergency_contacts': {
                'national_suicide_prevention': {
                    'name': 'National Suicide Prevention Lifeline',
                    'phone': '988',
                    'text': 'Text HOME to 741741',
                    'website': 'https://suicidepreventionlifeline.org'
                },
                'crisis_text_line': {
                    'name': 'Crisis Text Line',
                    'text': 'Text HOME to 741741',
                    'website': 'https://www.crisistextline.org'
                },
                'emergency': {
                    'name': 'Emergency Services',
                    'phone': '911',
                    'description': 'For immediate life-threatening emergencies'
                }
            },
            'resources': {
                'immediate_help': [
                    'Call 988 for the Suicide & Crisis Lifeline',
                    'Text HOME to 741741 for Crisis Text Line',
                    'Call 911 for immediate emergencies'
                ],
                'support_services': [
                    'National Alliance on Mental Illness (NAMI)',
                    'Mental Health America',
                    'Crisis Intervention Services'
                ]
            }
        }
    
    def set_emergency_contacts(self, user_id: str, contacts: List[Dict[str, str]]):
        """Set emergency contacts for a user"""
        self.emergency_contacts[user_id] = contacts
        logger.info(f"Emergency contacts set for user {user_id}")
    
    def get_emergency_contacts(self, user_id: str) -> List[Dict[str, str]]:
        """Get emergency contacts for a user"""
        return self.emergency_contacts.get(user_id, [])
