#!/usr/bin/env python3
"""
Event-Driven Webhook Manager - Real-Time Pattern Alerts
Monitors for critical events and sends immediate notifications via Telegram/ Discord
"""

import sys
sys.path.insert(0, '/home/avalonas/.hermes')

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Callable
import json
import time
from datetime import datetime
from enum import Enum

# Import local modules
try:
    from database_handler import DatabaseHandler
    from core_symbols import CoreSymbols
except ImportError:
    print("[WEBHOOK] Using mock database handler (local mode)")
    class MockDB:
        def get_relationship_matrix(self): return {}
        def get_analyzed_items(self): return []
    
    class MockCore:
        def items(self): return {}
        def get_all_items(self): return []

    DatabaseHandler = MockDB
    CoreSymbols = MockCore


class EventType(Enum):
    """Event types for webhook notifications"""
    PATTERN_DETECTED = "pattern_detected"       # New correlation/pattern found
    ANOMALY_DETECTED = "anomaly_detected"      # Critical pattern anomaly
    SYMBOL_ACTIVATION = "symbol_activation"     # Core symbol activation
    DOMAINS_CONVERGE = "domains_converge"      # Multiple domains connecting
    CROSS_DOMAIN_FOUND = "cross_domain_found"  # New cross-reference discovered
    VALUE_SPIKE = "value_spike"                # Temporal value spike
    PATTERN_BREAKDOWN = "pattern_breakdown"    # Established pattern breaking


@dataclass
class WebhookEvent:
    """Represents a webhook event to be sent"""
    event_type: EventType
    symbol_id: str
    correlation_strength: float
    description: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    confidence: float
    related_symbols: List[str] = field(default_factory=list)
    data_source: str = "web_search"
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class WebhookManager:
    """Manages event-driven webhook notifications for pattern detection"""
    
    # Event priority weights (higher = more urgent)
    PRIORITY_WEIGHTS = {
        EventType.ANOMALY_DETECTED: 10,
        EventType.CROSS_DOMAIN_FOUND: 8,
        EventType.DOMAINS_CONVERGE: 7,
        EventType.SYMBOL_ACTIVATION: 5,
        EventType.PATTERN_DETECTED: 3,
        EventType.VALUE_SPIKE: 4,
        EventType.PATTERN_BREAKDOWN: 6,
    }
    
    def __init__(self, db_handler=None, core_symbols=None):
        self.db_handler = db_handler or DatabaseHandler()
        self.core_symbols = core_symbols or CoreSymbols()
        
        # Webhook senders (can be configured for different platforms)
        self.telegram_sender = None  # Default to Telegram for now
        self.discord_sender = None
        
        # Event filters
        self.enabled_events: List[EventType] = list(EventType)  # All enabled by default
        self.severity_thresholds: Dict[str, float] = {
            'critical': 0.7,
            'high': 0.6,
            'medium': 0.4,
            'low': 0.2,
        }
        
        # Callback for event processing
        self.on_event_callbacks: List[Callable] = []
        
    def register_callback(self, callback: Callable):
        """Register a function to be called when events are processed"""
        self.on_event_callbacks.append(callback)
    
    def send_telegram_message(self, message: str, parse_mode: str = "Markdown"):
        """Send message to Telegram home channel"""
        if self.telegram_sender:
            try:
                self.telegram_sender.send_message(message)
                return True
            except Exception as e:
                print(f"[WEBHOOK] Telegram send failed: {e}")
                return False
        else:
            # Fallback: print to console (useful for testing)
            print(f"\n🚨 WEBHOOK ALERT:\n{message}")
            return True
    
    def format_anomaly_alert(self, event: WebhookEvent) -> str:
        """Format anomaly detection alert"""
        severity_emoji = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '⚪'
        }.get(event.severity, '🔴')
        
        return f"""{severity_emoji} 🔍 ANOMALY DETECTED - {event.symbol_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: {self._event_type_name(event.event_type)}
Severity: {event.severity.upper()} {severity_emoji}
Correlation: {abs(event.correlation_strength):.3f}
Confidence: {event.confidence:.0%}
Description: {event.description}

Related Symbols: {', '.join(event.related_symbols) or 'None'}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    def format_pattern_alert(self, event: WebhookEvent) -> str:
        """Format pattern detection alert"""
        return f"""✨ 🧩 PATTERN DETECTED - {event.symbol_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Correlation Found
Correlation Strength: {abs(event.correlation_strength):.3f}
Domains Detected: {self._extract_domains(event.description)}
Description: {event.description}

[WEBHOOK] Pattern detected via web_search source
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    def format_cross_domain_alert(self, event: WebhookEvent) -> str:
        """Format cross-domain convergence alert"""
        return f"""✨ 🔗 CROSS-DOMAIN CONNECTION - {event.symbol_id}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Type: Domain Convergence
Related Domains: {', '.join(event.related_symbols) or 'Multiple'}
Correlation: {abs(event.correlation_strength):.3f}
Description: {event.description}

[WEBHOOK] Cross-domain connection discovered
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    def _extract_domains(self, description: str) -> str:
        """Extract domain names from description text"""
        import re
        words = description.lower().split()
        domain_keywords = ['military', 'politic', 'religious', 'elemental', 'symbolic', 
                          'geographic', 'historical', 'cultural', 'temporal']
        found_domains = [w for w in words if any(k in w for k in domain_keywords)]
        return ', '.join(found_domains[:3]) if found_domains else 'Multiple domains'
    
    def _event_type_name(self, event_type: EventType) -> str:
        """Get human-readable event type name"""
        names = {
            EventType.ANOMALY_DETECTED: 'Anomaly Detection',
            EventType.PATTERN_DETECTED: 'Pattern Detection',
            EventType.CROSS_DOMAIN_FOUND: 'Cross-Domain Discovery',
            EventType.SYMBOL_ACTIVATION: 'Symbol Activation',
            EventType.DOMAINS_CONVERGE: 'Domain Convergence',
            EventType.VALUE_SPIKE: 'Value Spike',
            EventType.PATTERN_BREAKDOWN: 'Pattern Breakdown',
        }
        return names.get(event_type, event_type.value.replace('_', ' ').title())
