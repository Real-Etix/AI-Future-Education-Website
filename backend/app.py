# backend/app.py

from dotenv import load_dotenv
load_dotenv()

from flask import render_template, send_from_directory
from flask_app import init_app

app = init_app()

# Render static files
@app.route('/AI-Future-Education-Website/static/<path:path>', methods=['GET'])
def serve_static(path):
    return app.send_static_file(path)

# Render index.html
@app.route('/', defaults={'path': ''})
@app.route('/AI-Future-Education-Website/<path:path>', methods=['GET'])
def catch_all(path):
    return render_template('index.html')

@app.errorhandler(404)
def not_found(e):
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False)