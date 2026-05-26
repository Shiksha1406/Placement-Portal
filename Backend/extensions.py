from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_mail import Mail

cache = Cache()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, 
                  default_limits=["200 per day", "50 per hour"],
                  storage_uri="redis://localhost:6379")
