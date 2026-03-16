# Indian Stock Market Analytics - Configuration

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 5000))
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Data Source Configuration
    DEFAULT_EXCHANGE = os.getenv('DEFAULT_EXCHANGE', 'NSE')
    DATA_UPDATE_INTERVAL = int(os.getenv('DATA_UPDATE_INTERVAL', 5))  # seconds
    
    # Cache Configuration
    CACHE_ENABLED = os.getenv('CACHE_ENABLED', 'True').lower() == 'true'
    CACHE_DURATION = int(os.getenv('CACHE_DURATION', 60))  # seconds
    REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))
    REDIS_DB = int(os.getenv('REDIS_DB', 0))
    
    # Database Configuration
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'postgresql://user:password@localhost:5432/stock_analytics'
    )
    
    # API Keys (for external data sources)
    ALPHA_VANTAGE_KEY = os.getenv('ALPHA_VANTAGE_KEY', '')
    NSE_API_KEY = os.getenv('NSE_API_KEY', '')
    
    # ML Model Configuration
    MODEL_UPDATE_FREQUENCY = os.getenv('MODEL_UPDATE_FREQUENCY', 'daily')
    PREDICTION_HORIZON = int(os.getenv('PREDICTION_HORIZON', 1))  # days
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.65))
    
    # Risk Profiles
    RISK_PROFILES = {
        'conservative': {
            'max_loss': 0.05,
            'confidence_threshold': 0.75,
            'position_size': 5
        },
        'moderate': {
            'max_loss': 0.10,
            'confidence_threshold': 0.65,
            'position_size': 10
        },
        'aggressive': {
            'max_loss': 0.15,
            'confidence_threshold': 0.55,
            'position_size': 15
        }
    }
    
    # Technical Indicators Configuration
    RSI_PERIOD = int(os.getenv('RSI_PERIOD', 14))
    MACD_FAST = int(os.getenv('MACD_FAST', 12))
    MACD_SLOW = int(os.getenv('MACD_SLOW', 26))
    MACD_SIGNAL = int(os.getenv('MACD_SIGNAL', 9))
    BB_PERIOD = int(os.getenv('BB_PERIOD', 20))
    BB_STD = int(os.getenv('BB_STD', 2))
    
    # Popular Indian Stocks
    POPULAR_STOCKS = [
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
        'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK',
        'LT', 'AXISBANK', 'ASIANPAINT', 'MARUTI', 'TITAN',
        'SUNPHARMA', 'WIPRO', 'ULTRACEMCO', 'NESTLEIND', 'POWERGRID'
    ]
    
    # Market Segments
    MARKET_SEGMENTS = {
        'Nifty 50': [
            'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK',
            'HINDUNILVR', 'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK'
        ],
        'Bank Nifty': [
            'HDFCBANK', 'ICICIBANK', 'SBIN', 'KOTAKBANK', 'AXISBANK',
            'INDUSINDBK', 'BANDHANBNK', 'FEDERALBNK', 'IDFCFIRSTB', 'PNB'
        ],
        'IT': [
            'TCS', 'INFY', 'WIPRO', 'HCLTECH', 'TECHM',
            'LTI', 'MPHASIS', 'COFORGE', 'PERSISTENT', 'LTTS'
        ],
        'Pharma': [
            'SUNPHARMA', 'DRREDDY', 'CIPLA', 'DIVISLAB', 'BIOCON',
            'LUPIN', 'AUROPHARMA', 'TORNTPHARM', 'GLENMARK', 'CADILAHC'
        ]
    }
    
    # Alert Configuration
    ALERT_ENABLED = os.getenv('ALERT_ENABLED', 'True').lower() == 'true'
    ALERT_EMAIL = os.getenv('ALERT_EMAIL', '')
    ALERT_THRESHOLD_GAIN = float(os.getenv('ALERT_THRESHOLD_GAIN', 5.0))  # %
    ALERT_THRESHOLD_LOSS = float(os.getenv('ALERT_THRESHOLD_LOSS', -3.0))  # %
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'stock_analytics.log')
    LOG_MAX_BYTES = int(os.getenv('LOG_MAX_BYTES', 10485760))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv('LOG_BACKUP_COUNT', 5))
    
    # Rate Limiting
    RATE_LIMIT_ENABLED = os.getenv('RATE_LIMIT_ENABLED', 'True').lower() == 'true'
    RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', 60))
    
    # WebSocket Configuration
    WS_ENABLED = os.getenv('WS_ENABLED', 'True').lower() == 'true'
    WS_PORT = int(os.getenv('WS_PORT', 8765))
    
    # Security
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    JWT_EXPIRY = int(os.getenv('JWT_EXPIRY', 3600))  # seconds
    
    # Performance
    MAX_WORKERS = int(os.getenv('MAX_WORKERS', 4))
    BATCH_SIZE = int(os.getenv('BATCH_SIZE', 10))
    
    # Feature Flags
    ENABLE_ML_PREDICTIONS = os.getenv('ENABLE_ML_PREDICTIONS', 'True').lower() == 'true'
    ENABLE_SENTIMENT_ANALYSIS = os.getenv('ENABLE_SENTIMENT_ANALYSIS', 'False').lower() == 'true'
    ENABLE_NEWS_INTEGRATION = os.getenv('ENABLE_NEWS_INTEGRATION', 'False').lower() == 'true'


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    CACHE_DURATION = 30
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG = False
    CACHE_DURATION = 120
    LOG_LEVEL = 'WARNING'
    RATE_LIMIT_PER_MINUTE = 30


class TestingConfig(Config):
    """Testing environment configuration"""
    TESTING = True
    DEBUG = True
    CACHE_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """Get configuration based on environment"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
