# backend/app.py

from dotenv import load_dotenv
load_dotenv()

from flask import render_template, send_from_directory
from . import init_app

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
    app.run(host="0.0.0.0", debug=True)