import json
from datetime import datetime
from typing import Dict, Any, Optional

class SecurityMonitor:
    """Monitor and log security events for veterinary platform"""
    
    def __init__(self):
        self.security_events = []
        self.threat_patterns = [
            'multiple_failed_logins',
            'suspicious_input_patterns', 
            'unusual_data_access',
            'potential_injection_attempts',
            'rate_limit_exceeded'
        ]
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], 
                          user_id: Optional[str] = None):
        """Log security events with veterinary context"""
        
        event = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'user_id': user_id,
            'details': self._sanitize_log_data(details),
            'severity': self._calculate_severity(event_type, details),
            'ip_address': details.get('ip_address', 'unknown'),
            'user_agent': details.get('user_agent', 'unknown')[:200]  # Limit length
        }
        
        self.security_events.append(event)
        
        # Write to security log
        with open('/var/log/hardcard/security.log', 'a') as f:
            f.write(json.dumps(event) + '\n')
        
        # Alert on high-severity events
        if event['severity'] == 'HIGH':
            self._send_security_alert(event)
    
    def _sanitize_log_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive data from logs"""
        sensitive_fields = ['password', 'token', 'ssn', 'credit_card']
        
        sanitized = {}
        for key, value in data.items():
            if any(field in key.lower() for field in sensitive_fields):
                sanitized[key] = '[REDACTED]'
            elif isinstance(value, str) and len(value) > 1000:
                sanitized[key] = value[:1000] + '[TRUNCATED]'
            else:
                sanitized[key] = value
        
        return sanitized
    
    def _calculate_severity(self, event_type: str, details: Dict[str, Any]) -> str:
        """Calculate event severity for veterinary context"""
        high_severity_events = [
            'potential_injection_attempts',
            'data_breach_attempt', 
            'unauthorized_admin_access',
            'hipaa_violation_detected'
        ]
        
        if event_type in high_severity_events:
            return 'HIGH'
        elif details.get('failed_attempts', 0) > 5:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _send_security_alert(self, event: Dict[str, Any]):
        """Send alert for high-severity security events"""
        print(f"🚨 SECURITY ALERT: {event['event_type']}")
        print(f"   Time: {event['timestamp']}")
        print(f"   User: {event.get('user_id', 'Unknown')}")
        print(f"   Details: {event['details']}")

# Global security monitor
security_monitor = SecurityMonitor()