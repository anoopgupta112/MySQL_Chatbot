from functools import wraps
from flask import request, jsonify
import re
import os
import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# List of potentially dangerous SQL keywords
DANGEROUS_KEYWORDS = [
    "DROP", "DELETE", "TRUNCATE", "UPDATE", "INSERT",
    "ALTER", "GRANT", "REVOKE", "RENAME"
]

def require_api_key(f):
    """Decorator to require API key for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if not api_key or api_key != os.getenv('API_KEY'):
            logger.warning("Unauthorized API access attempt")
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated_function

def sanitize_input(query: str) -> str:
    """
    Sanitize user input by removing dangerous SQL commands
    and preventing SQL injection
    """
    if not query:
        return ""

    # Convert to uppercase for checking
    query_upper = query.upper()
    
    # Check for dangerous keywords
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in query_upper:
            logger.warning(f"Dangerous keyword detected: {keyword}")
            raise ValueError(f"Unauthorized keyword detected: {keyword}")
    
    # Remove any comments
    query = re.sub(r'/\*.*?\*/', '', query)
    query = re.sub(r'--.*$', '', query)
    
    # Remove multiple spaces
    query = ' '.join(query.split())
    
    return query

def validate_table_name(table_name: str) -> bool:
    """Validate table name against SQL injection"""
    return bool(re.match(r'^[a-zA-Z0-9_]+$', table_name))

def rate_limit(max_requests: int, window: int):
    """
    Decorator for rate limiting
    max_requests: maximum number of requests allowed in the time window
    window: time window in seconds
    """
    def decorator(f):
        requests = {}
        
        @wraps(f)
        def decorated_function(*args, **kwargs):
            now = int(time.time())
            ip = request.remote_addr
            
            # Clean old requests
            requests[ip] = [req_time for req_time in requests.get(ip, [])
                          if req_time > now - window]
            
            if len(requests.get(ip, [])) >= max_requests:
                logger.warning(f"Rate limit exceeded for IP: {ip}")
                return jsonify({"error": "Rate limit exceeded"}), 429
            
            requests.setdefault(ip, []).append(now)
            return f(*args, **kwargs)
            
        return decorated_function
    return decorator

class SecurityManager:
    @staticmethod
    def check_sql_injection(query: str) -> bool:
        """Check for potential SQL injection patterns"""
        # List of SQL injection patterns
        patterns = [
            r'\bOR\b.*?=',
            r'\bAND\b.*?=',
            r';\s*SELECT',
            r';\s*INSERT',
            r'UNION\s+SELECT',
            r'UNION\s+ALL\s+SELECT',
            r'--',
            r'/\*.*?\*/',
        ]
        
        query_upper = query.upper()
        for pattern in patterns:
            if re.search(pattern, query_upper, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {pattern}")
                return True
        return False

    @staticmethod
    def validate_query_complexity(query: str) -> bool:
        """
        Validate query complexity to prevent resource exhaustion
        Returns True if query is too complex
        """
        # Check for multiple joins
        join_count = len(re.findall(r'\bJOIN\b', query.upper()))
        if join_count > 5:
            return False
            
        # Check for deeply nested subqueries
        subquery_depth = len(re.findall(r'\(SELECT', query.upper()))
        if subquery_depth > 3:
            return False
            
        return True

    @staticmethod
    def mask_sensitive_data(data: dict, sensitive_fields: List[str]) -> dict:
        """Mask sensitive data in the response"""
        masked_data = data.copy()
        for field in sensitive_fields:
            if field in masked_data:
                masked_data[field] = '****'
        return masked_data

def init_security_headers():
    """Initialize security headers for the Flask app"""
    headers = {
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
        'X-Content-Type-Options': 'nosniff',
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline';"
    }
    return headers