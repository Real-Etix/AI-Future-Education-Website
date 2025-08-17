# backend/flask_app/chat_router.py

from .llm_prompt import *
from .tables import *
from .story_api import get_value_by_story
import re

def send_message(chat_id, message, is_user):
    '''
    Send the message.
    '''

    if type(message) is not str:
        raise TypeError("Message must be a string or a coroutine that returns a string.")
    else:
        message = message.strip()
    stage = get_chat_stage(chat_id)
    _, creation_time = append_message(chat_id, stage, message, is_user)
    update_chat_last_updated(chat_id)

async def send_message_replace_line_break(chat_id, generator, is_user):
    """
    Replaces line breaks in the text from an asynchronous generator.
    Send the message after processing.

    Args:
        chat_id (int): The ID of the chat.
        generator (async generator): The asynchronous generator to process.
        is_user (int): Indicates if the message is from the user.

    Returns:
        async generator: A new asynchronous generator with line breaks replaced.
    """
    text = ''
    async for chunk in generator:
        text += chunk
        chunk = re.sub(r'(\r\n|\r|\n)', '<br/>', chunk)
        yield chunk
    send_message(chat_id, text, is_user)


def routing_begin_message(chat_id, data):
    '''
    Routing begin message handling for different types of chat creation method.
    '''
    method = data['method']

    match method:
        case "blank" | "main":
            begin_message = '今日想要學習什麼價值觀？'
            send_message(chat_id, begin_message, 0)
            return update_chat_status(chat_id, 0)

        case 'story':
            story_id = data['storyID']
            title, story = get_story(story_id)
            user_message = f'我想閱讀「{title}」這個故事。'
            send_message(chat_id, user_message, 1)
            update_chat_stage(chat_id, 2)

            store_story_to_cache(chat_id, story)
            value = get_value_by_story(story_id)
            set_chat_value(chat_id, value)
            
            automated_message = f'''當然！\n\n{story}'''
            send_message(chat_id, automated_message, 0)
            return update_chat_status(chat_id, 1)

async def routing_message(chat_id):
    '''
    This is the central part of the chatbot that performs action in order.
    It will return the response to the chatbot.
    Send the message after calling this function.
    '''
    message = get_last_message(chat_id)
    stage = get_chat_stage(chat_id)
    match stage:
        case 0:
            # Stage 0: Intent Classification
            value = await intent_classify(message)
            if value == '沒有':
                yield update_chat_status(chat_id, 0)

                automated_message = '抱歉，我不明白你的意思。請問你想學習什麼價值觀？'
            
            elif value == '問候':
                yield update_chat_status(chat_id, 0)

                automated_message = '你好！今天想學習什麼價值觀？'
            
            else:
                set_chat_value(chat_id, value)

                yield update_chat_status(chat_id, 1)

                automated_message = f'看來你想學習什麼是{value}呢！我們先來講一個有關{value}的故事吧！請給我幾分鐘寫一個故事。'

                update_chat_stage(chat_id, 1)
            
            for text in automated_message:
                yield text

        case 1:
            # Stage 1: Story Generation
            value = get_chat_value(chat_id)
            yield update_chat_status(chat_id, 1)

            story_generator = generate_new_story(value)

            story = ''
            async for text in story_generator:
                story += text
                yield text
            
            automated_message = f'\n\n花幾分鐘看看這個故事，我會同時準備一些關於故事的問題。'

            for text in automated_message:
                yield text

            store_story_to_cache(chat_id, story)

            update_chat_stage(chat_id, 2)
            

        case 2:
            # Stage 2: Question-and-Answer Generation
            story = get_story_from_cache(chat_id)
            value = get_chat_value(chat_id)
            questions, answers = await generate_qa_pairs(story, value)
            store_question_answer_pairs(chat_id, questions, answers)

            yield update_chat_status(chat_id, 0)

            automated_message = '看完了嗎？如果看完請告訴我，我會問你一些問題。'

            for text in automated_message:
                yield text
            
            update_chat_stage(chat_id, 3)

        case 3:
            # Stage 3: Showing question
            question = get_question(chat_id)
            if question:
                yield update_chat_status(chat_id, 0)

                automated_message = f'問題：{question}'
            else:
                answer = get_answer(chat_id)

                yield update_chat_status(chat_id, 1)

                automated_message = f'答案：{answer}' if answer else ''
            
            for text in automated_message:
                yield text

            if not exist_question_cache_record(chat_id):
                update_chat_stage(chat_id, 4)
        
        case 4:
            # Stage 4: Asking user about similar scenario 
            value = get_chat_value(chat_id)
            yield update_chat_status(chat_id, 0)

            automated_message = f'想必你已經對{value}有一點點了解。日常中有沒有發生什麼事和故事有關？'

            for text in automated_message:
                yield text
            
            update_chat_stage(chat_id, 5)
        
        case 5:
            # Stage 5: Generate similar scenario
            yield update_chat_status(chat_id, 0)

            automated_message = "那我用一個類似的情景來考一考你吧！\n\n"

            for text in automated_message:
                yield text
            
            async for text in generate_scenario(message):
                yield text

            update_chat_stage(chat_id, 6)

        case 6:
            # Stage 6: Scenario Response
            if get_user_message_count(chat_id, 6) > 3:
                update_chat_stage(chat_id, 7)

            value = get_chat_value(chat_id)

            records = get_stage_message(chat_id, stage)

            yield update_chat_status(chat_id, 0)

            async for text in generate_scenario_persuasion(records, value):
                yield text

        
        case 7:
            # Stage 7: Scenario Feedback
            value = get_chat_value(chat_id)

            records = get_stage_message(chat_id, stage)

            yield update_chat_status(chat_id, 0)

            async for text in generate_scenario_feedback(records, value):
                yield text

            update_chat_stage(chat_id, 8)
        
        case _:
            # Stage 8: Ended Conversation
            yield update_chat_status(chat_id, 0)

            yield '如果你想認識其他價值觀或者故事，請創建新會話。'
        
