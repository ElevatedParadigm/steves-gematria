#!/usr/bin/env python3
"""
Anomaly Detection Enhancement - Phase 2 Intelligence Layer
Monitors for symbolic pattern deviations, sudden correlations, and emerging patterns.
Uses multi-agent analysis with threshold-based alerting.
"""

import json
from datetime import datetime, timedelta
import re
import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import time
import threading

from .stability_core import StabilityCore
from .symbol_analysis import SymbolAnalysis
from .core_symbols import CoreSymbols
from .database_handler import DatabaseHandler


@dataclass
class AnomalyRecord:
    """Tracks detected anomalies with severity levels."""
    anomaly_id: str
    timestamp: datetime
    anomaly_type: str  # 'correlation_shift', 'pattern_breakdown', 'cross_domain_divergence', 'value_deviation', 'temporal_spike'
    affected_symbol: str
    current_value: float
    expected_range: Tuple[float, float]
    severity: str  # 'low', 'medium', 'high', 'critical'
    description: str
    related_symbols: List[str] = field(default_factory=list)
    confidence_score: float = 0.5


class AnomalyDetector:
    """Multi-agent anomaly detection system with threshold-based alerts."""
    
    # Thresholds for different anomaly types (can be tuned)
    CORRELATION_THRESHOLD = 0.6  # Significant correlation drop
    PATTERN_BREAKDOWN_THRESHOLD = 2.0  # Sudden value deviation factor
    TEMPORAL_SPIKE_THRESHOLD = 3.0  # Standard deviations from mean
    
    def __init__(self, db_handler: DatabaseHandler, core_symbols: CoreSymbols):
        self.db_handler = db_handler
        self.core_symbols = core_symbols
        
        self.anomalies: Dict[str, AnomalyRecord] = {}
        self.baseline_metrics: Optional[Dict] = None
        self.detected_patterns: List[Dict] = []
        
    def initialize_baseline(self):
        """Establish baseline metrics for anomaly comparison."""
        baseline = {
            'correlation_strength': {},  # avg correlation per relationship
            'pattern_magnitude': {},  # avg magnitude of effects
            'temporal_means': {},  # rolling mean by domain/category
        }
        
        relationships = self.db_handler.get_relationship_matrix()
        for key, rel in relationships.items():
            if rel and 'correlation_strength' in rel:
                sym = str(rel.get('primary_symbol', 'UNKNOWN'))
                baseline['correlation_strength'][sym] = (
                    baseline['correlation_strength'].get(sym, 0) + rel['correlation_strength']
                ) / max(1, self._count_relationships(key))
        
        for key, item in self.core_symbols.items():
            if item.get('temporal_variance'):
                domain = str(item['domain'])
                baseline['temporal_means'][f"{domain}_magnitude"] = (
                    baseline['temporal_means'].get(f"{domain}_magnitude", 0) + abs(item['temporal_variance'])
                ) / max(1, self._count_occurrences(key))
        
        self.baseline_metrics = baseline
        print(f"📊 Baseline metrics initialized: {len(baseline['correlation_strength'])} correlations, "
              f"{len(baseline['temporal_means'])} temporal tracks")
    
    def _count_relationships(self, key) -> int:
        """Count relationship occurrences for averaging."""
        relationships = self.db_handler.get_relationship_matrix()
        count = 0
        for rkey, rel in relationships.items():
            if rkey.startswith(key) or rkey.endswith(key):
                count += 1
        return min(count, 10)
    
    def _count_occurrences(self, key) -> int:
        """Count occurrences for temporal averaging."""
        items = self.core_symbols.get_all_items()
        count = sum(1 for item in items if str(key).lower() in str(item).lower())
        return min(count, 5)
    
    def detect_correlation_anomaly(self, key1: str, key2: str, 
                                   current_corr: float, prev_corr: Optional[float]) -> Optional[AnomalyRecord]:
        """Detect significant correlation strength changes."""
        if not self.baseline_metrics or 'correlation_strength' not in self.baseline_metrics:
            return None
        
        expected_range = (0.7, 1.0)  # High correlations should stay strong
        expected_min = max(expected_range[0], self.baseline_metrics['correlation_strength'].get(str(key1), 0.5))
        
        if abs(current_corr - prev_corr) > self.CORRELATION_THRESHOLD or abs(current_corr) < expected_min:
            severity = 'low'
            confidence = 0.7
            if current_corr < expected_min * 0.5:
                severity = 'critical'
                confidence = 0.9
            elif abs(current_corr - prev_corr) > self.CORRELATION_THRESHOLD * 1.5:
                severity = 'high'
                confidence = 0.8
            
            return AnomalyRecord(
                anomaly_id=f"corr_{key1}_to_{key2}_{int(time.time() % 10000)}",
                timestamp=datetime.now(),
                anomaly_type='correlation_shift',
                affected_symbol=str(key1),
                current_value=current_corr,
                expected_range=(expected_min, 1.0),
                severity=severity,
                description=f"Correlation {key1}→{key2} changed from {prev_corr:.3f} to {current_corr:.3f}",
                related_symbols=[str(key2)],
                confidence_score=confidence
            )
        return None
    
    def detect_pattern_breakdown(self, symbol_key: str, current_value: float, 
                                  baseline_magnitude: Optional[float]) -> Optional[AnomalyRecord]:
        """Detect sudden breakdowns in established pattern magnitudes."""
        if not self.baseline_metrics or 'pattern_magnitude' not in self.baseline_metrics:
            return None
        
        expected = abs(baseline_magnitude) if baseline_magnitude else 50.0
        deviation_factor = abs(current_value) / expected if expected > 0 else float('inf')
        
        if deviation_factor > self.PATTERN_BREAKDOWN_THRESHOLD:
            severity = 'low'
            confidence = 0.6
            if deviation_factor > self.PATTERN_BREAKDOWN_THRESHOLD * 2:
                severity = 'critical'
                confidence = 0.9
            elif deviation_factor > self.PATTERN_BREAKDOWN_THRESHOLD * 1.5:
                severity = 'high'
                confidence = 0.8
            elif deviation_factor > self.PATTERN_BREAKDOWN_THRESHOLD * 1.2:
                severity = 'medium'
                confidence = 0.75
            
            return AnomalyRecord(
                anomaly_id=f"breakdown_{symbol_key}_{int(time.time() % 10000)}",
                timestamp=datetime.now(),
                anomaly_type='pattern_breakdown',
                affected_symbol=symbol_key,
                current_value=current_value,
                expected_range=(-expected * self.PATTERN_BREAKDOWN_THRESHOLD, 
                               expected * self.PATTERN_BREAKDOWN_THRESHOLD),
                severity=severity,
                description=f"Pattern magnitude deviation: {current_value:.1f} vs baseline {baseline_magnitude:.1f}",
                confidence_score=confidence
            )
        return None
    
    def detect_temporal_spike(self, domain: str, current_value: float, 
                               window_mean: Optional[float], window_std: Optional[float]) -> Optional[AnomalyRecord]:
        """Detect temporal spikes in specific domains."""
        if not self.baseline_metrics or 'temporal_means' not in self.baseline_metrics:
            return None
        
        expected = abs(window_mean) if window_mean else 30.0
        deviation_factor = current_value / max(expected, 1)
        
        if deviation_factor > self.TEMPORAL_SPIKE_THRESHOLD:
            severity = 'low'
            confidence = 0.65
            if deviation_factor > self.TEMPORAL_SPIKE_THRESHOLD * 2:
                severity = 'critical'
                confidence = 0.9
            elif deviation_factor > self.TEMPORAL_SPIKE_THRESHOLD * 1.5:
                severity = 'high'
                confidence = 0.8
            elif deviation_factor > self.TEMPORAL_SPIKE_THRESHOLD * 1.2:
                severity = 'medium'
                confidence = 0.75
            
            return AnomalyRecord(
                anomaly_id=f"spike_{domain}_{int(time.time() % 10000)}",
                timestamp=datetime.now(),
                anomaly_type='temporal_spike',
                affected_symbol=domain,
                current_value=current_value,
                expected_range=(-window_mean * self.TEMPORAL_SPIKE_THRESHOLD,
                               window_mean * self.TEMPORAL_SPIKE_THRESHOLD),
                severity=severity,
                description=f"Temporal spike in {domain}: {current_value:.1f} vs mean {window_mean:.1f}",
                confidence_score=confidence
            )
        return None
    
    def detect_cross_domain_divergence(self, domain: str, value: float, 
                                        related_domains: List[str]) -> Optional[AnomalyRecord]:
        """Detect divergence between related domains that should correlate."""
        if not self.baseline_metrics or 'correlation_strength' not in self.baseline_metrics:
            return None
        
        expected_correlation = 0.75  # Related domains should correlate strongly
        min_threshold = expected_correlation * 0.5
        
        if value < min_threshold:
            severity = 'medium' if value < expected_correlation * 0.8 else 'low'
            confidence = 0.6
            
            return AnomalyRecord(
                anomaly_id=f"divergence_{domain}_{int(time.time() % 10000)}",
                timestamp=datetime.now(),
                anomaly_type='cross_domain_divergence',
                affected_symbol=domain,
                current_value=value,
                expected_range=(expected_correlation, 1.0),
                severity=severity,
                description=f"Cross-domain divergence detected in {domain}",
                related_symbols=[str(d) for d in related_domains],
                confidence_score=confidence
            )
        return None
    
    def detect_value_deviation(self, symbol_key: str, current_value: float,
                               historical_mean: Optional[float]) -> Optional[AnomalyRecord]:
        """Detect values deviating significantly from historical means."""
        if not self.baseline_metrics or 'temporal_means' not in self.baseline_metrics:
            return None
        
        expected = abs(historical_mean) if historical_mean else 25.0
        deviation_factor = current_value / max(expected, 1)
        
        if deviation_factor > 3.0:  # Standard deviation threshold
            severity = 'medium'
            confidence = 0.7
            
            return AnomalyRecord(
                anomaly_id=f"deviation_{symbol_key}_{int(time.time() % 10000)}",
                timestamp=datetime.now(),
                anomaly_type='value_deviation',
                affected_symbol=symbol_key,
                current_value=current_value,
                expected_range=(-expected * 2.5, expected * 2.5),
                severity=severity,
                description=f"Value deviation: {current_value:.1f} vs historical mean {historical_mean:.1f}",
                confidence_score=confidence
            )
        return None
    
    def detect_all_anomalies(self) -> List[AnomalyRecord]:
        """Run comprehensive anomaly detection across all patterns."""
        anomalies = []
        
        # Get current relationships
        relationships = self.db_handler.get_relationship_matrix()
        
        for key1, rel in relationships.items():
            if not rel:
                continue
            
            # Check correlation anomalies
            key2 = key1.split('→')[-1] if '→' in key1 else None
            if key2 and rel.get('correlation_strength', 0) != -1:
                current_corr = rel['correlation_strength']
                
                # Get historical value for comparison
                hist_items = self.core_symbols.get_all_items()
                prev_corr = (
                    sum(r.get('correlation_strength', 0) for r in relationships.values() if str(key2) in str(r)) / 
                    max(1, sum(1 for r in relationships.values() if str(key2) in str(r)))
                )
                
                anomaly = self.detect_correlation_anomaly(key1, key2, current_corr, prev_corr)
                if anomaly:
                    anomalies.append(anomaly)
        
        # Get items and check pattern breakdowns
        for symbol_key, item in self.core_symbols.items():
            current_value = item.get('temporal_variance', 0)
            
            # Check historical values from baseline
            hist_items = self.core_symbols.get_all_items()
            historical_mean = sum(abs(i.get('temporal_variance', 0)) for i in hist_items) / len(hist_items)
            
            anomaly = self.detect_pattern_breakdown(symbol_key, current_value, historical_mean)
            if anomaly:
                anomalies.append(anomaly)
        
        # Detect cross-domain divergence (symbolic significance)
        symbolic_domains = {item['domain'] for item in self.core_symbols.get_all_items() 
                          if 'symbolic' in str(item).lower()}
        
        related = [d for d in symbolic_domains if 'military' in str(d).lower()]
        for domain in related:
            corr_value = rel.get('correlation_strength', 1.0) if rel else 0.8
            anomaly = self.detect_cross_domain_divergence(domain, corr_value, related)
            if anomaly:
                anomalies.append(anomaly)
        
        return anomalies
    
    def generate_alert(self, anomaly: AnomalyRecord) -> str:
        """Generate alert message for detected anomaly."""
        severity_indicator = {
            'low': '(⚪ Low)',
            'medium': '(🟡 Medium)', 
            'high': '(🟠 High)',
            'critical': '(🔴 CRITICAL)'
        }
        
        confidence_bar = "█" * int(anomaly.confidence_score * 10) + "░" * (10 - int(anomaly.confidence_score * 10))
        
        return f"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🚨 ANOMALY DETECTED: {anomaly.severity_indicator} {severity_indicator.get(anomaly.severity, '')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Type:         {anomaly.anomaly_type.replace('_', ' ').title()}
Symbol:       {anomaly.affected_symbol}
Timestamp:    {anomaly.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
Description:  {anomaly.description}
Related:      {', '.join(anomaly.related_symbols) if anomaly.related_symbols else 'None'}

Severity:     {severity_indicator.get(anomaly.severity, '')}
Confidence:   [{confidence_bar}] {anomaly.confidence_score:.0%}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""


class AnomalyDetectionEnhanced(StabilityCore):
    """Main class integrating anomaly detection into overnight stability test."""
    
    def __init__(self, db_handler: DatabaseHandler, core_symbols: CoreSymbols, 
                 telegram_sender=None):
        super().__init__()
        self.db_handler = db_handler
        self.core_symbols = core_symbols
        
        # Initialize multi-agent system components
        self.anomaly_detector = AnomalyDetector(db_handler, core_symbols)
        
        # Agent configuration
        self.config = {
            'correlation_anomalies': True,
            'pattern_breakdowns': True,
            'temporal_spikes': True,
            'cross_domain_divergence': True,
            'value_deviations': True,
            
            'correlation_threshold': AnomalyDetector.CORRELATION_THRESHOLD,
            'pattern_breakdown_threshold': AnomalyDetector.PATTERN_BREAKDOWN_THRESHOLD,
            'temporal_spike_threshold': AnomalyDetector.TEMPORAL_SPIKE_THRESHOLD,
        }
        
        self.telegram_sender = telegram_sender
        
    def run_full_anomaly_scan(self) -> List[str]:
        """Run comprehensive anomaly detection and return alerts."""
        print("\n🔍 [Anomaly Detection] Starting full scan across all patterns...")
        start_time = time.time()
        
        try:
            # Initialize baseline if not done
            if not self.anomaly_detector.baseline_metrics:
                self.anomaly_detector.initialize_baseline()
            
            # Detect all anomalies
            print("🔍 [Anomaly Detection] Running detection algorithms...")
            anomalies = self.anomaly_detector.detect_all_anomalies()
            
            print(f"📊 [Anomaly Detection] Found {len(anomalies)} potential anomalies")
            
            # Generate alerts for high-severity anomalies
            alerts = []
            for anomaly in anomalies:
                if anomaly.severity in ['high', 'critical']:
                    alert_msg = self.anomaly_detector.generate_alert(anomaly)
                    alerts.append(alert_msg.strip())
                    
                    # Send to Telegram if configured
                    if self.telegram_sender and self.config.get('enable_telegram_alerts'):
                        try:
                            self.telegram_sender.send_message(
                                f"🚨 ALERT: {anomaly.severity.upper()} anomaly detected in {anomaly.anomaly_type}\n\n"
                                f"{alert_msg}"
                            )
                            print(f"✅ Alert sent to Telegram")
                        except Exception as e:
                            print(f"⚠️ Telegram alert failed: {e}")
            
            # Print critical alerts to console
            for alert in alerts:
                if 'CRITICAL' in alert or 'HIGH' in alert:
                    print(alert)
                
                return alerts
            
            print("✅ [Anomaly Detection] Scan complete - no anomalies detected")
            return []
            
        except Exception as e:
            self.handle_exception(f"Anomaly detection failed: {e}")
            return None
    
    def update_baseline_metrics(self, current_relationships: Dict):
        """Update baseline metrics with new data."""
        if not self.anomaly_detector.baseline_metrics:
            self.anomaly_detector.initialize_baseline()
        
        for key, rel in current_relationships.items():
            if rel and 'correlation_strength' in rel:
                sym = str(rel.get('primary_symbol', 'UNKNOWN'))
                current_avg = rel['correlation_strength']
                old_avg = self.anomaly_detector.baseline_metrics['correlation_strength'].get(sym, 0)
                
                # Update running average
                count = max(1, sum(1 for r in current_relationships.values() 
                                 if str(sym) in str(r)))
                new_avg = (old_avg * (count - 1) + current_avg) / count
                
                self.anomaly_detector.baseline_metrics['correlation_strength'][sym] = new_avg
        
        print(f"📊 [Anomaly Detection] Baseline updated with {len(current_relationships)} relationships")
    
    def get_anomaly_summary(self) -> Dict:
        """Get summary of detected anomalies."""
        return {
            'total_anomalies': len([a for a in self.anomaly_detector.anomalies.values() 
                                   if a.severity in ['low', 'medium']]),
            'high_severity_anomalies': len([a for a in self.anomaly_detector.anomalies.values() 
                                           if a.severity == 'high']),
            'critical_anomalies': len([a for a in self.anomaly_detector.anomalies.values() 
                                      if a.severity == 'critical']),
            'anomaly_types': {
                type_name: len([a for a in self.anomaly_detector.anomalies.values() 
                               if a.anomaly_type == type_name.replace(' ', '_')])
                for type_name in ['correlation shift', 'pattern breakdown', 
                                  'temporal spike', 'cross domain divergence', 
                                  'value deviation']
            }
        }


# Entry point when run directly
if __name__ == "__main__":
    from stability_core import StabilityCore
    
    # Create instance with default handlers
    core = AnomalyDetectionEnhanced(
        db_handler=DatabaseHandler("/home/avalonas/.hermes/gematria"),
        core_symbols=CoreSymbols("/home/avalonas/.hermes/gematria")
    )
    
    # Run full scan
    alerts = core.run_full_anomaly_scan()
    
    if alerts:
        print("\n" + "="*60)
        print("ANALYSIS COMPLETE - ALERTS GENERATED")
        print("="*60)
        
        for alert in alerts[:5]:  # Limit to top 5 critical/high alerts
            print(alert)
    else:
        print("\n✅ No anomalies detected in current cycle")
        
    print("\n📁 Files updated:")
    print("   - anomaly_detection.py (Anomaly Detection Enhancement)")
    print("   - stability_test_enhanced_optimized.py (integrated anomaly detection)")
