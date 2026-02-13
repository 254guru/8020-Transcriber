import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-change-in-production')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///transcriber.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Celery configuration
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
    
    # API configuration
    API_KEY = os.getenv('API_KEY', 'default-api-key')
    REQUEST_LIMIT = os.getenv('REQUEST_LIMIT', '100/hour')
    
    # Job configuration
    JOB_TIMEOUT = int(os.getenv('JOB_TIMEOUT', '3600'))  # 1 hour in seconds
    MAX_URLS_PER_JOB = int(os.getenv('MAX_URLS_PER_JOB', '50'))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    CELERY_ALWAYS_EAGER = True

# Select config based on environment
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

CONFIG = config[os.getenv('FLASK_ENV', 'development')]
