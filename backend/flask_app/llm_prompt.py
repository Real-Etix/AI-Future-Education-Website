# backend/blueprints/llm_prompt.py

import asyncio

from .tools import extract_chinese_between_chars, obtain_text_from_generator
from .tables import get_value_id, get_random_story, get_story, get_story_summary, store_story_summary
from .llm_call import classify_llm, story_llm
from .llm_call.llm_wrapper import llm_response

async def intent_classify(message) -> str:
    '''
    Determine the intent (desired value) of the message using LLM.
    '''

    # Remove characters with a translation table
    translation_table = dict.fromkeys(map(ord, '\r\n'), None)
    cleaned_message = message.translate(translation_table).strip()

    # Set the prompt to feed to LLM
    prompt = f'''<|start_header_id|>user<|end_header_id|>
        
分類用戶的意圖，意圖一定是：承諾、問候、沒有
如果不清楚，回答沒有。

用戶：{cleaned_message}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

意圖：'''
    
    # Obtain output from LLM and polish the result  
    generator = classify_llm.local_llm_completion(prompt, max_tokens=5, temperature=0)
    result = await obtain_text_from_generator(generator)
    intent = result.strip()
    return intent if intent else '沒有'

async def summarize_story(story):
    '''
    Summarize the text to smaller text for faster generation.
    TODO: Value should be used to generate a more specific summary.
    '''

    # Set the prompt to feed to LLM
    prompt = f'''總結以下故事。

{story}

總結：'''
    
    generator = llm_response(prompt)
    result = await obtain_text_from_generator(generator)
    polished_result = result.strip()
    return polished_result

async def generate_new_story(value):
    '''
    Generate a similar story with an example using LLM.
    '''
    if value:
        value_id = get_value_id(value)
        story_id = get_random_story(value_id)
        summary = get_story_summary(story_id)
        if not summary:
            _, story = get_story(story_id)
            summary = await summarize_story(story)
            store_story_summary(story_id, summary)
    
    prompt = f'''<|start_header_id|>user<|end_header_id|>
        
根據總結，創造二百字內的現代故事，關於{value}，不用說故事告訴我們什麼。

例子："""
總結：{summary}
"""<|eot_id|><|start_header_id|>assistant<|end_header_id|>

故事：'''
    
    async for text in story_llm.local_llm_completion(prompt, max_tokens=500, temperature=0.8, stream=True):
        yield text

async def generate_qa_pairs(story, value):
    '''
    Generate questions and answers based on the story using LLM.
    '''

    prompt = f'''\
根據以下的故事，問關於{value}的三條問題：

{story}

結構："""
問題：．．． 
答案：．．．
"""

問題：'''
    
    generator = llm_response(prompt, stream=False)
    result = await obtain_text_from_generator(generator)
    modified_result = '問題：' + result.strip()
    questions = extract_chinese_between_chars(modified_result, '問題：', '')
    answers = extract_chinese_between_chars(modified_result, '答案：', '')
    return questions, answers

async def generate_scenario(message, value) -> str:
    prompt = f'''\
你是一名老師。請為學生制造一個關於{value}的情景題。\
以學生為主角，問題需要問學生會怎樣做，假設學生可能會違反這個價值觀，限制一個段落和問題。
情景題可以和以下類似：
{message}

"""
結構：
情景題：．．．
"""

情景題：'''
    generator = llm_response(prompt, stream=True)
    result = await obtain_text_from_generator(generator)
    polished_result = result.strip()
    return polished_result

async def generate_scenario_persuasion(message_records: list) -> str:
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
    generator = llm_response(prompt)
    result = await obtain_text_from_generator(generator)
    modified_result = '老師：' + result.strip()
    response = extract_chinese_between_chars(modified_result, '老師：', '')
    return response[0] if response else ''

async def generate_scenario_feedback(message_records: list) -> str:
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
    generator = llm_response(prompt)
    result = await obtain_text_from_generator(generator)
    modified_result = '老師：' + result.strip()
    response = extract_chinese_between_chars(modified_result, '老師：', '')
    return response[0] if response else ''

def preload_prompt():
    '''
    This preloads the prompts to the LLM for faster inference later.
    '''
    print('Preloading prompts...')
    asyncio.run(intent_classify(''))
    print('Prompts preloaded.')