import os
ENV = os.getenv('ENV', 'development')
if ENV == 'production':
    DB_DIR = '/mnt/bases/'
else:
    DB_DIR = '/var/www/bases/'