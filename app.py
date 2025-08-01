# Before importing, disable __pycache__ generation.
import sys
sys.dont_write_bytecode = 1

from flask import Flask, render_template, send_from_directory
from backend.blueprints.chat_api import chat_api
from backend.blueprints.story_api import story_api

# These class table definitions need to be imported in order to register foreign keys.
from backend.blueprints.tables.chat import Chat
from backend.blueprints.tables.message import Message
from backend.blueprints.tables.question_cache import QuestionCache
from backend.blueprints.tables.story_value_link import StoryValueLink
from backend.blueprints.tables.story import Story
from backend.blueprints.tables.user import User
from backend.blueprints.tables.value import Value
from backend.blueprints.tables.database import db
from config import db_config
import os
import asyncio

# Create the Flask application.
# Static folder contains all the images, css and js files
# Template folder contains the html
app = Flask(__name__, 
            static_folder="dist/static",
            template_folder="dist",
            static_url_path="/AI-Future-Education-Website"
            )

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')

# Render index.html for dynamic Vue routing
@app.route('/chatbot/<int:chatID>')
def show_chat_website(chatID):
    return render_template('index.html')

# Render static files
@app.route('/AI-Future-Education-Website/static/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path) # type: ignore

if __name__ == '__main__':
    # Bare minimum session security
    app.config['SECRET_KEY'] = os.urandom(24)

    # Database configuration
    app.config.from_object(db_config) 

    # Load all the blueprints for different route or api
    app.register_blueprint(chat_api, url_prefix='/chat-api')
    app.register_blueprint(story_api, url_prefix='/story-api')

    # Run the application to be hosted 
    db.init_app(app)
    app.run(debug=True)