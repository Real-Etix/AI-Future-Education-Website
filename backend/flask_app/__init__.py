# backend/flask_app/__init__.py

# These class table definitions need to be imported in order to register foreign keys.
import os
import asyncio
from flask import Flask
from .config import db_config

from .tables import *
from .llm_call import local_llm, retrieval_llm
from .chat_api import chat_api
from .story_api import story_api
from .llm_prompt import preload_prompt

def init_app():
    '''
    Initialize Flask app.
    '''

    # Create the Flask application.
    # Static folder contains all the images, css and js files
    # Template folder contains the html
    app = Flask(__name__, 
        static_folder="../../frontend/dist/static",
        # static_folder="../dist/static",
        template_folder="../../frontend/dist",
        # template_folder="../dist",
        static_url_path="/AI-Future-Education-Website"
    )

    # Database configuration
    app.config.from_object(db_config) 

    # Initialize Plugins
    db.init_app(app)

    # Bare minimum session security
    app.config['SECRET_KEY'] = os.urandom(24)

    with app.app_context():
        local_llm.init_llm()
        retrieval_llm.init_sentence_llm()
        asyncio.run(preload_prompt())

        # Register Blueprints
        app.register_blueprint(chat_api, url_prefix='/chat-api')
        app.register_blueprint(story_api, url_prefix='/story-api')

        return app