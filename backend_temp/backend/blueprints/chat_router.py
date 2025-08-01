# backend/blueprints/chat_router.py

from .llm_prompt import *
from .tables.chat import *
from .tables.message import append_message, get_user_message_count, get_last_message, get_stage_message
from .tables.question_cache import store_question_answer_pairs, get_question, get_answer
from .tables.story_cache import get_story_from_cache, store_story_to_cache
from .tables.story import get_story
from .story_api import get_value_by_story

def send_message(chat_id, message, is_user):
    '''
    Send the message.
    '''
    stage = get_chat_stage(chat_id)
    _, creation_time = append_message(chat_id, stage, message, is_user)
    update_chat_latest_time(chat_id)
    return creation_time

def routing_begin_message(chat_id, data):
    '''
    Routing begin message handling for different types of chat creation method.
    '''
    method = data['method']

    match method:
        case "blank":
            begin_message = '今日想要學習什麼價值觀？'
            send_message(chat_id, begin_message, 0)

        case "main":
            begin_message = '今日想要學習什麼價值觀？'
            send_message(chat_id, begin_message, 0)

            user_message = data['message']
            send_message(chat_id, user_message, 1)

            update_chat_status(chat_id, 1)

        case 'story':
            story_id = data['storyID']
            title, story = get_story(story_id)
            user_message = f'我想閱讀「{title}」這個故事。'
            send_message(chat_id, user_message, 1)
            update_chat_stage(chat_id, 1)

            store_story_to_cache(chat_id, story)
            value = get_value_by_story(story_id)
            set_chat_value(chat_id, value)
            
            automated_message = f'''當然！

            {story}
            
            如果你看完故事，試一試答以下的問題吧。'''
            send_message(chat_id, automated_message, 0)
            update_chat_status(chat_id, 1)

def routing_message(chat_id):
    '''
    This is the central part of the chatbot that performs action in order.
    '''
    message = get_last_message(chat_id)
    stage = get_chat_stage(chat_id)
    if stage == 0:
        # Stage 0: initializing chat.
        value = intent_classify(message)
        if value == '沒有':
            automated_message = '抱歉，可以再說一次你想學習什麼價值觀嗎？'
            creation_time = send_message(chat_id, automated_message, 0)
            return automated_message, creation_time
        
        set_chat_value(chat_id, value)
        update_chat_stage(chat_id, 1)

        story = generate_new_story(value)
        store_story_to_cache(chat_id, story)
        automated_message = f'''看來你想學習什麼是{value}呢！我講一個有關{value}的故事吧！

        {story}

        如果你看完故事，試一試答以下的問題吧。
        '''
        creation_time = send_message(chat_id, automated_message, 0)
        update_chat_status(chat_id, 1)
    
    if stage == 1:
        # Stage 1: Story is shown to the user and generating questions
        story = get_story_from_cache(chat_id)
        value = get_chat_value(chat_id)

        questions, answers = generate_questions(story, value)
        store_question_answer_pairs(chat_id, questions, answers)
        update_chat_stage(chat_id, 2)

    if stage in [1,2]:
        # Stage 2: Show each question and corresponding answers one-by-one.
        answer = get_answer(chat_id)
        question = get_question(chat_id)
        answer_format = f'答案：{answer}\n\n' if answer else ''
        value = get_chat_value(chat_id)
        question_format = f'問題：{question}' if question else \
            f'想必你已經對{value}有一點點了解。接下來，我會問一個情景題。'
        automated_message = f'{answer_format}{question_format}'
        creation_time = send_message(chat_id, automated_message, 0)

        if question == None:
            update_chat_stage(chat_id, 3)
            update_chat_status(chat_id, 1)
        else:
            update_chat_status(chat_id, 0)
    
    if stage == 3:
        # Stage 3: Scenario-based question 
        update_chat_stage(chat_id, 4)

        value = get_chat_value(chat_id)
        automated_message = generate_scenario(value)
        creation_time = send_message(chat_id, automated_message, 0)

        update_chat_status(chat_id, 0)
    
    if stage == 4:
        # Stage 4: Scenario persuasion
        if get_user_message_count(chat_id, 4) > 3:
            update_chat_stage(chat_id, 5)
        records = get_stage_message(chat_id, stage)
        automated_message = generate_scenario_persuasion(records)
        creation_time = send_message(chat_id, automated_message, 0)

        update_chat_status(chat_id, 0)

    if stage == 5:
        # Stage 5: Feedback
        records = get_stage_message(chat_id, stage)
        automated_message = generate_scenario_feedback(records)
        creation_time = send_message(chat_id, automated_message, 0)

        update_chat_stage(chat_id, 6)
        update_chat_status(chat_id, 1)
    
    if stage not in range(6):
        # Chat finished
        automated_message = '如果你想認識其他價值觀或者故事，請創建新會話。'
        creation_time = send_message(chat_id, automated_message, 0)

        update_chat_status(chat_id, 0)
    return automated_message, creation_time


