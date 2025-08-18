# backend/flask_app/chat_api.py

from flask import Response, Blueprint, request, abort, jsonify, stream_with_context
from .tables import (
    get_chat_list, get_chat_name, get_chat_status, 
    append_chat, update_chat_last_updated, 
    get_message_list
)
from .chat_router import send_message, send_message_replace_line_break, routing_begin_message, routing_message
import asyncio
import json

# This file defines the chat API blueprint
chat_api = Blueprint('chat_api', __name__)

pending_messages = {}

def iter_over_async(ait, loop, status='Complete'):
    ait = ait.__aiter__()
    async def get_next():
        try:
            return False, await ait.__anext__()
        except StopAsyncIteration:
            return True, None
    yield f"data: {json.dumps({'text': '', 'status': 'Stream Starting'})}\n\n"
    while True:
        done, value = loop.run_until_complete(get_next())
        if done:
            yield f"data: {json.dumps({'text': '', 'status': status})}\n\n"
            break
        yield f"data: {json.dumps({'text': value, 'status': 'Stream Loading'})}\n\n"

# def generator_to_json(generator, status='Complete'):
#     """
#     Collects text from an asynchronous generator and yields it.
    
#     Args:
#         generator (async generator): The asynchronous generator to collect text from.
    
#     Yields:
#         str: The collected text.
#     """
#     for text in asyncio.run(async_gen_to_coroutine(generator)):
#         yield f"data: {json.dumps({'text': text, 'status': 'Loading'})}\n\n"
#     yield f"data: {json.dumps({'text': '', 'status': status})}\n\n"

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
    return jsonify({'error': 'Unable to get chat messages'}), 400

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
        return jsonify({'sent': True})
    return jsonify({'error': 'Unable to send message'}), 400

@chat_api.route('/send-message-response', methods=['GET', 'SEE'])
def response_message_stream():
    '''
    Stream the response message to the frontend.
    '''
    chat_id = request.args.get('chatID', type=int)
    if not chat_id:
        return jsonify({'error': 'Chat ID is required'}), 400
    
    generator = routing_message(chat_id)
    has_unsent_message = asyncio.run(anext(generator, 'Complete')) # type: ignore
    response_generator = send_message_replace_line_break(chat_id, generator, 0)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    iter_gen = iter_over_async(response_generator, loop, status=has_unsent_message)
    ctx = stream_with_context(iter_gen)
    return Response(ctx, mimetype='text/event-stream')