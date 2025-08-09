# backend/blueprints/chat_router.py

from .llm_prompt import *
from .tables import *
from .story_api import get_value_by_story

def send_message(chat_id, message, is_user):
    '''
    Send the message.
    '''
    stage = get_chat_stage(chat_id)
    _, creation_time = append_message(chat_id, stage, message, is_user)
    update_chat_last_updated(chat_id)


def routing_begin_message(chat_id, data):
    '''
    Routing begin message handling for different types of chat creation method.
    '''
    method = data['method']

    match method:
        case "blank" | "main":
            begin_message = '今日想要學習什麼價值觀？'
            send_message(chat_id, begin_message, 0)
            update_chat_status(chat_id, 0)

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
                yield '抱歉，我不明白你的意思。請問你想學習什麼價值觀？'
            
            elif value == '問候':
                yield '你好！今天想學習什麼價值觀？'
            
            else:
                set_chat_value(chat_id, value)

                yield f'看來你想學習什麼是{value}呢！我們先來講一個有關{value}的故事吧！'

                update_chat_stage(chat_id, 1)
                update_chat_status(chat_id, 1)
        case 1:
            # Stage 1: Story Generation
            value = get_chat_value(chat_id)
            story = await generate_new_story(value)
            store_story_to_cache(chat_id, story)
            yield story

            update_chat_stage(chat_id, 2)
            update_chat_status(chat_id, 1)

        case 2:
            # Stage 2: Question-and-Answer Generation
            story = get_story_from_cache(chat_id)
            value = get_chat_value(chat_id)
            questions, answers = await generate_qa_pairs(story, value)
            store_question_answer_pairs(chat_id, questions, answers)

            yield '如果你看完故事，請告訴我，我會給你一些問題。'

            update_chat_stage(chat_id, 3)
            update_chat_status(chat_id, 0)

        case 3:
            # Stage 3: Showing question
            question = get_question(chat_id)
            if question:
                yield f'問題：{question}'

                update_chat_status(chat_id, 0)
            else:
                answer = get_answer(chat_id)
                yield f'答案：{answer}' if answer else ''

                update_chat_status(chat_id, 1)

            if not exist_question_cache_record(chat_id):
                update_chat_stage(chat_id, 4)
                update_chat_status(chat_id, 1)
        
        case 4:
            # Stage 4: Asking user about similar scenario 
            value = get_chat_value(chat_id)
            yield f'想必你已經對{value}有一點點了解。日常中有沒有發生什麼事和故事有關？'

            update_chat_stage(chat_id, 5)
            update_chat_status(chat_id, 0)
        
        case 5:
            # Stage 5: Generate similar scenario
            value = get_chat_value(chat_id)
            update_chat_stage(chat_id, 6)

            yield f"那我用一個類似的情景來考一考你吧！"
            yield generate_scenario(message, value)

            update_chat_status(chat_id, 0)

        case 6:
            # Stage 6: Scenario Response
            if get_user_message_count(chat_id, 6) > 3:
                update_chat_stage(chat_id, 7)

            records = get_stage_message(chat_id, stage)
            yield generate_scenario_persuasion(records)

            update_chat_status(chat_id, 0)
        
        case 7:
            # Stage 7: Scenario Feedback
            records = get_stage_message(chat_id, stage)
            yield generate_scenario_feedback(records)

            update_chat_stage(chat_id, 8)
            update_chat_status(chat_id, 1)
        
        case _:
            # Stage 8: Ended Conversation
            yield '如果你想認識其他價值觀或者故事，請創建新會話。'

            update_chat_status(chat_id, 0)


