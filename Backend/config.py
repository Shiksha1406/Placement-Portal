import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    ADMIN_SECRET_KEY = os.environ.get('ADMIN_SECRET_KEY', 'admin@123')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

    # Caching — uses Redis if available, falls back to simple in-memory
    CACHE_TYPE                  = 'RedisCache'
    CACHE_REDIS_URL             = os.environ.get('REDIS_URL', 'redis://localhost:6379/1')
    CACHE_DEFAULT_TIMEOUT       = 300          # 5 minutes
    
    # Rate limiting
    RATELIMIT_STORAGE_URL       = os.environ.get('REDIS_URL', 'redis://localhost:6379/2')
    RATELIMIT_DEFAULT           = '200 per day;50 per hour'
    RATELIMIT_HEADERS_ENABLED   = True         

    # OpenAI API key
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '') or os.environ.get('ANTHROPIC_API_KEY', '')

    # Celery
    CELERY_BROKER_URL        = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0')
    CELERY_RESULT_BACKEND    = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

    #Mail
    MAIL_SERVER         = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT           = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS        = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME       = os.environ.get('MAIL_USERNAME', 'shru61762@gmail.com')
    MAIL_PASSWORD       = os.environ.get('MAIL_PASSWORD', 'asuq qsrw euhs wiuz')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'shru61762@gmail.com')


    # Admin Creation (used on first startup)
    ADMIN_USERNAME      = os.environ.get('ADMIN_USERNAME', 'admin')
    ADMIN_PASSWORD      = os.environ.get('ADMIN_PASSWORD', 'admin@123')


    
# To run Celery:
#   Worker:  celery -A tasks.celery worker --loglevel=info --pool=solo
#   Beat:    celery -A tasks.celery beat --loglevel=info