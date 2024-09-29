import os

class Config:
    ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = ENV == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))
    import os

# Ensure the data directory exists
    if not os.path.exists(os.path.join(basedir, 'instance')):
        os.makedirs(os.path.join(basedir, 'instance'))

    if ENV == 'development':
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "development.db")}'
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')

    SQLALCHEMY_TRACK_MODIFICATIONS = False
