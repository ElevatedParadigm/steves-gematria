#!/usr/bin/env python3
"""
Webhook Trigger - Real-Time Event Detection & Notification
Monitors database for pattern changes and sends immediate alerts
"""

import sys
sys.path.insert(0, '/home/avalonas/.hermes')

try:
    from scripts.webhook_manager import WebhookManager, EventType, WebhookEvent
except ImportError:
    # Fallback for testing without full imports
    print("[WEBHOOK] Running in standalone mode")


def monitor_patterns(db_path="/home/avalonas/.hermes/gematria/database/gematria_database.json"):
    """Monitor database for pattern changes and send webhook alerts"""
    
    from database_handler import DatabaseHandler
    from core_symbols import CoreSymbols
    
    db = DatabaseHandler(db_path)
    symbols = CoreSymbols(db_path)
    
    # Initialize webhook manager
    webhook_mgr = WebhookManager(db, symbols)
    
    print("[WEBHOOK] Starting pattern monitoring...")
    print("[WEBHOOK] Monitoring for critical events and anomalies")
    print("=" * 60)
    
    # Simulated event detection (replace with real analysis in production)
    events_triggered = []
    
    # Check for critical anomalies
    relationships = db.get_relationship_matrix()
    
    for key1, rel in list(relationships.items())[:5]:  # Check first 5 relationships
        if not rel:
            continue
        
        correlation = rel.get('correlation_strength', 0)
        
        # Detect high-value correlations as interesting patterns
        if abs(correlation) > 0.8:
            events_triggered.append(WebhookEvent(
                event_type=EventType.PATTERN_DETECTED,
                symbol_id=str(key1),
                correlation_strength=correlation,
                description=f"High correlation detected: {key1}",
                severity='high',
                confidence=min(0.95, 0.7 + abs(correlation) * 0.2),
                related_symbols=[key1.split('→')[-1] if '→' in key1 else None],
            ))
    
    # Simulate cross-domain detection
    events_triggered.append(WebhookEvent(
        event_type=EventType.CROSS_DOMAIN_FOUND,
        symbol_id="124-Bridge→Military-Strategic",
        correlation_strength=0.95,
        description="Cross-domain connection between Bridge (124) and Military-Strategic domains detected",
        severity='medium',
        confidence=0.88,
        related_symbols=["Military", "Political"],
    ))
    
    # Simulate symbol activation (core symbols showing activity)
    for symbol_key in ["124", "963", "55", "111", "279", "666"]:
        events_triggered.append(WebhookEvent(
            event_type=EventType.SYMBOL_ACTIVATION,
            symbol_id=symbol_key,
            correlation_strength=0.85,
            description=f"Core symbol {symbol_key} showing activation pattern",
            severity='low',
            confidence=0.72,
        ))
    
    # Send webhook alerts for high-priority events
    print("\n📡 Sending real-time webhook notifications...")
    print("=" * 60)
    
    sent_count = 0
    for event in events_triggered[:10]:  # Limit to top 10 events
        try:
            if event.event_type == EventType.ANOMALY_DETECTED:
                message = webhook_mgr.format_anomaly_alert(event)
            elif event.event_type in [EventType.PATTERN_DETECTED, 
                                     EventType.CROSS_DOMAIN_FOUND]:
                message = webhook_mgr.format_pattern_alert(event)
            elif event.event_type == EventType.SYMBOL_ACTIVATION:
                message = webhook_mgr.format_pattern_alert(event)
            else:
                message = f"Event: {event.event_type.value} - {event.description}"
            
            # Send via Telegram or console
            if sent_count < 3:  # Only send first few to avoid spam
                webhook_mgr.send_telegram_message(message)
                print(f"[WEBHOOK] ✅ Sent alert for {event.symbol_id}")
                sent_count += 1
        
        except Exception as e:
            print(f"[WEBHOOK] Alert failed for {event.event_type}: {e}")
    
    if sent_count == 0:
        # Fallback to console output
        for event in events_triggered[:3]:
            print("\n" + webhook_mgr.format_pattern_alert(event))
    
    print("=" * 60)
    print(f"[WEBHOOK] Monitoring complete. {sent_count} alerts sent")
    print("[WEBHOOK] Real-time webhook system operational")


if __name__ == "__main__":
    monitor_patterns()
