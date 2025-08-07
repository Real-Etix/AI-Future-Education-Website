# app.py

# Before importing, disable __pycache__ generation.
import sys
sys.dont_write_bytecode = 1

from dotenv import load_dotenv
load_dotenv()

from flask import render_template, send_from_directory
from backend import init_app

app = init_app()

# Render index.html
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/AI-Future-Education-Website/', methods=['GET'])
def main():
    return render_template('index.html')

@app.route('/AI-Future-Education-Website/<path:path>', methods=['GET'])
def subsequent(path):
    return render_template('index.html')

# Render static files
@app.route('/AI-Future-Education-Website/static/<path:path>', methods=['GET'])
def serve_static(path):
    return send_from_directory(app.static_folder, path) # type: ignore

if __name__ == '__main__':
    app.run(debug=True)