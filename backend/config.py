# backend/config.py

import os

# Configurations on database file path
# stories.db is set to be the default database
class db_config(object):
    default_database = 'stories'
    base_dir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(base_dir, 'database/stories.db')
    SQLALCHEMY_BINDS = {
        'chats_db': 'sqlite:///' + os.path.join(base_dir, 'database/chats.db')
    }