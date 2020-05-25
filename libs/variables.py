import os

SESSION_TYPE = os.getenv('SESSION_TYPE','redis')
REDIS_URL = os.getenv('REDIS_URL','')
DATABASE_URL = os.getenv("DATABASE_URL", "postgres://hvqogvevkqpplz:e6113c0ef737828a6287b527ba54d94a55ac5a03f502a5894f9f962a8089fa9d@ec2-54-217-204-34.eu-west-1.compute.amazonaws.com:5432/d5q2igekbibr4j")
LOG_LEVEL = os.getenv('LOG_LEVEL','INFO')
WEBPORT = os.getenv('PORT', '5000')

# environment variable
DATETIME_PATTERN='%Y-%m-%dT%H:%M:%S%z'
DATE_PATTERN='%Y-%m-%d'
DEFAULT_ADMIN_USERNAME="admin"
DEFAULT_ADMIN_EMAIL="admin@email.com"
DEFAULT_ADMIN_PASSWORD='password'
TEMPLATES_URL = "../templates"
STATIC_URL = "../static"    