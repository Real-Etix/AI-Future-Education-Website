# backend/blueprints/chat_api.py

from flask import Blueprint, request, abort, jsonify
from .tables import (
    get_chat_list, get_chat_name, get_chat_status, 
    append_chat, get_chat_last_updated, update_chat_last_updated, 
    get_message_list
)
from .chat_router import send_message, routing_begin_message, routing_message
from .tools import obtain_text_from_generator
import asyncio

# This file defines the chat API blueprint
chat_api = Blueprint('chat_api', __name__)

@chat_api.route('/get-chat-list', methods=['POST'])
def obtain_chat_list():
    '''
    Get the list from the database and send back to the frontend.
    '''
    if request.method == 'POST':
        user_id = request.get_json()['userID']
        response = get_chat_list(user_id)
        return jsonify(response)
    abort(405)

@chat_api.route('/create-chat', methods=['POST'])
def create_chat():
    '''
    Create the chat in the server and send the id to the frontend.
    '''
    if request.method == 'POST':
        data = request.get_json()
        chat_name = data['name']
        user_id = data['userID']

        new_chat_id = append_chat(user_id, chat_name, 0)

        routing_begin_message(new_chat_id, data)
        
        update_chat_last_updated(new_chat_id)
        response = {'chatID': new_chat_id}
        return jsonify(response)
    abort(405)

@chat_api.route('/send-message', methods=['POST'])
def update_chat_on_message_sent():
    '''
    Manage sending message and send the response to the frontend.
    '''
    if request.method == 'POST':
        data = request.get_json()
        chat_id = data['chatID']
        message = data['message']
        send_message(chat_id, message, 1)
        generator = routing_message(chat_id)
        response_text = asyncio.run(obtain_text_from_generator(generator))
        send_message(chat_id, response_text, 0)
        created_at = get_chat_last_updated(chat_id)
        status = get_chat_status(chat_id)
        response = {
            'message': response_text,
            'createdAt': created_at,
            'status': status
        }
        return jsonify(response)
    abort(405)

@chat_api.route('/get-chat-message', methods=['POST'])
def obtain_chat():
    '''
    Get the relevant chat infomation into the frontend.
    Status is used to indicated that there are some remaining messages that are not sent yet.
    '''
    if request.method == 'POST':
        chat_id = request.get_json()['chatID']
        title = get_chat_name(chat_id)
        response = get_message_list(chat_id)
        status = get_chat_status(chat_id)
        return jsonify({'title': title, 'result': response, 'status': status})
    abort(405)

@chat_api.route('/get-remaining-message', methods=['POST'])
def obtain_remaining_message():
    '''
    Get the remaining unsent message to the frontend.
    '''
    if request.method == 'POST':
        chat_id = request.get_json()['chatID']
        generator = routing_message(chat_id)
        message = asyncio.run(obtain_text_from_generator(generator))
        send_message(chat_id, message, 0)
        creation_time = get_chat_last_updated(chat_id)
        status = get_chat_status(chat_id)
        return jsonify({'message': message, 'createdAt': creation_time, 'status': status})
    abort(405)