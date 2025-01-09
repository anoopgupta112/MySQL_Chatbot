import os
from datetime import timedelta

class Config:
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    DEBUG = os.getenv('FLASK_DEBUG', 'False') == 'True'
    
    # Database settings
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # API settings
    API_KEY = os.getenv('API_KEY')
    
    # Cache settings
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 300
    
    # Security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=30)
    
    # Rate limiting
    RATELIMIT_DEFAULT = "100/hour"
    RATELIMIT_STORAGE_URL = "memory://"
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = 'app.log'
    
    # Query settings
    MAX_QUERY_LENGTH = 1000
    MAX_RESULTS_PER_PAGE = 100
    ALLOWED_QUERY_COMPLEXITY = 5  # Maximum number of joins
    
    # Google AI settings
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
    
    # Custom settings
    ALLOWED_TABLES = [
        'orders',
        'orders_details',
        'pizza_types',
        'pizzas'
    ]
    
    SENSITIVE_FIELDS = [
        'password',
        'credit_card',
        'email'
    ]
    
    # Error messages
    ERROR_MESSAGES = {
        'unauthorized': 'Unauthorized access',
        'rate_limit': 'Rate limit exceeded',
        'invalid_query': 'Invalid query',
        'database_error': 'Database error occurred'
    }
    
    # Response templates
    RESPONSE_TEMPLATES = {
        'success': {
            'status': 'success',
            'message': None,
            'data': None
        },
        'error': {
            'status': 'error',
            'message': None,
            'error_code': None
        }
    }