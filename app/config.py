# import os
# from dotenv import dotenv_values

# class Config:
#     MODE = os.getenv('FLASK_ENV', 'development')
#     DEBUG = MODE == 'development'
#     SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

#     # Database configuration
#     basedir = os.path.abspath(os.path.dirname(__file__))

#     env = dotenv_values("./.env")
#     username = env.get("DATABASE_USERNAME")
#     password = env.get("DATABASE_PASSWORD")
#     dbname = env.get("DATABASE_NAME")
#     port = env.get("DATABASE_PORT")
#     host = env.get("DATABASE_HOST")


# # Ensure the data directory exists
#     if not os.path.exists(os.path.join(basedir, 'instance')):
#         os.makedirs(os.path.join(basedir, 'instance'))

#     if MODE == 'development':
#         SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "development.db")}'
#     else:
#         SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{dbname}"
#         # SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

#     SQLALCHEMY_TRACK_MODIFICATIONS = False
import os

class Config:
    MODE = os.getenv('FLASK_ENV', 'development')
    DEBUG = MODE == 'development'
    SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key')

    # Database configuration
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Local development: fallback to SQLite
    if MODE == 'development':
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(basedir, "instance", "development.db")}'
    else:
        # In production, expect DATABASE_URL from Supabase or Vercel
        SQLALCHEMY_DATABASE_URI = os.getenv('POSTGRES_URL')

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Ensure the data directory exists in dev (optional)
    if MODE == 'development':
        instance_path = os.path.join(basedir, 'instance')
        if not os.path.exists(instance_path):
            os.makedirs(instance_path)
