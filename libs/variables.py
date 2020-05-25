import os

# hard  coded environment variable
SESSION_TYPE = os.getenv('SESSION_TYPE','redis')
REDIS_URL = os.getenv('REDIS_URL','')
DATABASE_URL = os.getenv("DATABASE_URL", "")
LOG_LEVEL = os.getenv('LOG_LEVEL','INFO')
WEBPORT = os.getenv('PORT', '5000')
DATETIME_PATTERN='%Y-%m-%dT%H:%M:%S%z'
DATE_PATTERN='%Y-%m-%d'
TEMPLATES_URL = "../templates"
STATIC_URL = "../static"    

# configurable environment variable
DEFAULT_ADMIN_USERNAME= os.getenv('DEFAULT_ADMIN_USERNAME','admin')
DEFAULT_ADMIN_EMAIL= os.getenv('DEFAULT_ADMIN_EMAIL','admin@email.com')
DEFAULT_ADMIN_PASSWORD= os.getenv('DEFAULT_ADMIN_PASSWORD','password')
DEFAULT_API_URL=os.getenv('DEFAULT_API_URL', '/api/covid19')