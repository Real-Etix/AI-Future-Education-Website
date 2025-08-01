# backend/blueprints/llm_prompt.py

import asyncio
from .llm_wrapper import llm_response
from .story_api import get_story_by_value
from .tools import extract_chinese_between_chars
from .tables.value import get_value_id

def intent_classify(message) -> str:
    '''
    Determine the intent (desired value) of the message using LLM.
    '''

    # Remove characters with a translation table
    translation_table = dict.fromkeys(map(ord, '\r\n'), None)
    cleaned_message = message.translate(translation_table)

    # Set the prompt to feed to LLM
    prompt = f'''\
從以下對話分析使用者的最多一個意圖，不用解釋為什麼：
- 承諾
- 堅毅

使用者： 我想知道什麼是諾言。
意圖： 承諾

使用者： 你是誰？
意圖： 沒有

使用者： {cleaned_message}
意圖：\
'''
    
    # Obtain output from LLM and polish the result  
    result = asyncio.run(llm_response(prompt))
    polished_result = result[3:].strip()
    return polished_result

def generate_new_story(value) -> str:
    '''
    Generate a similar story with an example using LLM.
    '''
    value_id = get_value_id(value)
    story = get_story_by_value(value_id)
    prompt = f'''\
創造有關{value}的類似故事，故事要二百字內，不用說這個故事告訴我們什麼：
例子：
{story}

故事：\
'''
    result = asyncio.run(llm_response(prompt))
    polished_result = result.strip()
    return polished_result

def generate_questions(story, value):
    '''
    Generate questions and answers based on the story using LLM.
    '''

    prompt = f'''\
根據以下的故事，問關於{value}的三條問題：

{story}

結構："""
問題： 你好嗎？ 
答案： 我很好。
"""

問題：\
'''
    result = asyncio.run(llm_response(prompt))
    modified_result = '問題：' + result.strip()
    questions = extract_chinese_between_chars(modified_result, '問題：', '')
    answers = extract_chinese_between_chars(modified_result, '答案：', '')
    return questions, answers

def generate_scenario(value) -> str:
    prompt = f'''\
你是一名老師。請為學生制造一個關於{value}的情景題。\
以學生為主角，問題需要問學生會怎樣做，假設學生可能會違反這個價值觀，限制一個段落和問題。
"""
結構：
情景題：．．．
"""
情景題：
    '''
    result = asyncio.run(llm_response(prompt))
    polished_result = result.strip()
    return polished_result

def generate_scenario_persuasion(message_records: list) -> str:
    '''
    Generate follow-up questions based on the conversation between user and chatbot.
    message_record should be a list of messages in the following structure:
    - message
    - isUser
    '''
    prompt = f'''\
你是一名老師，根據學生的回答作出回應。稱呼學生為學生。\
如果違反承諾，簡短引導學生跟隨承諾這個價值觀。\
如果跟隨承諾，簡短嘗試改變問題讓學生違反承諾。\
如果偏離問題，帶學生回到問題。

'''
    for message_record in message_records:
        message = message_record['message']
        role = '學生' if message_record['isUser'] else '老師'
        prompt += f'{role}: {message}\n'
    prompt += '老師：'
    result = asyncio.run(llm_response(prompt))
    modified_result = '老師：' + result.strip()
    response = extract_chinese_between_chars(modified_result, '老師：', '')
    return response[0] if response else ''

def generate_scenario_feedback(message_records: list) -> str:
    '''
    Generate feedback based on the conversation between user and chatbot.
    message_record should be a list of messages in the following structure:
    - message
    - isUser
    '''
    prompt = f'''\
你是一名老師，總結你和學生的對話，給學生關於承諾的回饋。

'''
    for message_record in message_records:
        message = message_record['message']
        role = '學生' if message_record['isUser'] else '老師'
        prompt += f'{role}: {message}\n'
    prompt += '老師：'
    result = asyncio.run(llm_response(prompt))
    modified_result = '老師：' + result.strip()
    response = extract_chinese_between_chars(modified_result, '老師：', '')
    return response[0] if response else ''
