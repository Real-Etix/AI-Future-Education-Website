# backend/__init__.py

from flask import Flask

from .blueprints import *

from .config import db_config

import os

def init_app():
    '''
    Initialize Flask app.
    '''

    # Create the Flask application.
    # Static folder contains all the images, css and js files
    # Template folder contains the html
    app = Flask(__name__, 
        static_folder="../dist/static",
        template_folder="../dist",
        # static_url_path="/AI-Future-Education-Website"
    )

    # Database configuration
    app.config.from_object(db_config) 

    # Initialize Plugins
    db.init_app(app)

    # Bare minimum session security
    app.config['SECRET_KEY'] = os.urandom(24)

    with app.app_context():
        classify_llm.init_llm()
        preload_prompt()

        # Register Blueprints
        app.register_blueprint(chat_api, url_prefix='/chat-api')
        app.register_blueprint(story_api, url_prefix='/story-api')

        return app