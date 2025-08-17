# backend/flask_app/story_api.py

from flask import Blueprint, request, abort, jsonify, url_for
from .tables import (
    get_value, get_random_value, get_story_list
)

# This file defines the story API blueprint
story_api = Blueprint('story_api', __name__)

def get_value_by_story(story_id: int|None):
    '''
    Get the value randomly that is related to story
    '''
    value_candidate_id = get_random_value(story_id)
    value = get_value(value_candidate_id)
    return value

@story_api.route('/get-story-item-list', methods=['GET'])
def obtain_story_item():
    '''
    Obtain a list of stories shown on the main page
    '''
    if request.method == 'GET':
        result = get_story_list()
        response = [{'id': row[0], 'title': row[1], 'img_link': url_for('static', filename='images/' + row[2])} for row in result]
        return jsonify(response)
    abort(405)
