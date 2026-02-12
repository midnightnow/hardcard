import re
import html
from typing import Optional, Dict, Any

class SecureInputValidator:
    """Production-grade input validation for veterinary data"""
    
    def __init__(self):
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocols
            r'on\w+\s*=',  # Event handlers
            r'(union|select|insert|drop|delete|update|exec)\s+',  # SQL injection
            r'--\s*$',  # SQL comments
            r'/\*.*?\*/',  # SQL block comments
        ]
        
        self.max_lengths = {
            'practice_name': 100,
            'owner_name': 50,
            'notes': 2000,
            'email': 254,
            'phone': 20
        }
    
    def sanitize_input(self, input_data: str, field_type: str = 'general') -> str:
        """Sanitize user input with veterinary-specific rules"""
        if not input_data or not isinstance(input_data, str):
            return ''
        
        # HTML escape
        cleaned = html.escape(input_data.strip())
        
        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Apply length limits
        max_length = self.max_lengths.get(field_type, 500)
        cleaned = cleaned[:max_length]
        
        return cleaned
    
    def validate_veterinary_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete veterinary practice data"""
        validated = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                validated[key] = self.sanitize_input(value, key)
            elif isinstance(value, (int, float)):
                # Numeric validation
                validated[key] = max(0, min(value, 1000000))  # Reasonable bounds
            elif isinstance(value, list):
                # List validation
                validated[key] = [self.sanitize_input(str(item)) for item in value[:10]]
            else:
                validated[key] = str(value)[:100]  # Fallback
        
        return validated

# Global validator instance
secure_validator = SecureInputValidator()