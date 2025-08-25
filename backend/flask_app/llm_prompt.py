# backend/flask_app/llm_prompt.py

import asyncio

from .tools import extract_chinese_between_chars, extract_chinese_words_between_chars, obtain_text_from_generator
from .tables import get_value_id, get_random_story, get_story, get_story_summary, store_story_summary
from .llm_call import local_llm, llm_response, retrieval_llm

async def intent_classify(message, max_tokens=5, preload_mode=False):
    '''
    Determine the intent (desired value) of the message using LLM.
    '''

    # Remove characters with a translation table
    translation_table = dict.fromkeys(map(ord, '\r\n'), None)
    cleaned_message = message.translate(translation_table).strip()

    # Set the prompt to feed to LLM
    prompt = f'''<|start_header_id|>user<|end_header_id|>
        
分類用戶的意圖，意圖一定是：＜承諾、問候、沒有＞。如果不清楚，回答沒有。

用戶：{cleaned_message}

意圖：<|eot_id|><|start_header_id|>assistant<|end_header_id|>

'''
    
    # Obtain output from LLM and polish the result  
    if preload_mode:
        local_llm.create_state(prompt, file='intent.pkl', max_tokens=1, temperature=0, top_k=0, top_p=1.0)
        return ''
    else:
        generator = local_llm.local_llm_completion(prompt, max_tokens=max_tokens, temperature=0, top_k=0, top_p=1.0, state_file='intent.pkl')
        result = await obtain_text_from_generator(generator)
        intent = extract_chinese_words_between_chars(result, '')
        return intent[0] if intent else '沒有'

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

async def generate_new_story(value, max_tokens=500, preload_mode=False):
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
    else:
        summary = ''

    # Although our original purpose is to generate a story with less than 500 words,
    # It turns out that we need to tell the LLM that the story needs to not be greater than 200
    # in order to guarantee that the story will almost never reach 500 words.
    prompt = f'''<|start_header_id|>user<|end_header_id|>
        
受以下故事為靈感，寫一篇不超過二百字的中文故事，不要涉及歷史、犯罪、鬥爭或愛情。敘事要簡潔明瞭，聚焦在獨特的人物、豐富的情節和新穎的場景，避免以勸告、結論或道德教訓的方式結束。主體必須有關實行{value}。

靈感：{summary}

故事：<|eot_id|><|start_header_id|>assistant<|end_header_id|>

'''
    
    if preload_mode:
        local_llm.create_state(prompt, 'story.pkl', max_tokens=1, temperature=0.8, top_k=0, top_p=1.0, min_p=0.1)
        yield ''
    else:
        async for text in local_llm.local_llm_completion(prompt, stream=True, max_tokens=max_tokens, temperature=0.8, top_k=0, top_p=1.0, min_p=0.1, state_file='story.pkl'):
            yield text

async def generate_qa_pairs(story, value, max_tokens=500, preload_mode=False):
    '''
    Generate questions and answers based on the story using LLM.
    '''
    story = story.replace("\r\n\r\n", "\r\n").replace("\n\n", "\n")

    prompt = f'''<|start_header_id|>user<|end_header_id|>

產生三個問答對，與故事人物、事件或如何遵循價值觀有關。

輸出結構："""
問題：＜輸入問題＞
答案：＜輸入答案＞
"""

故事（價值觀：{value}）：{story}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

問題：'''
    
    if preload_mode:
        local_llm.create_state(prompt, 'qa.pkl', max_tokens=1, temperature=0.8, top_k=0, top_p=1.0, min_p=0.1)
        return '', ''
    else:
        generator = local_llm.local_llm_completion(prompt, max_tokens=max_tokens, temperature=0.8, top_k=0, top_p=1.0, min_p=0.1, state_file='qa.pkl')
        result = await obtain_text_from_generator(generator)
        modified_result = '問題：' + result.strip()
        questions = extract_chinese_between_chars(modified_result, '問題：', '')
        answers = extract_chinese_between_chars(modified_result, '答案：', '')
        return questions, answers

async def generate_scenario(message, max_tokens=500, preload_mode=False):
    '''
    Generate a scenario based on the retrieved scenario by comparing the message with those from the vector database.
    Note that it is possible that the LLM can generate the same as retrieved one. It is expected.
    '''
    if not preload_mode:
        scenario, theme = retrieval_llm.obtain_most_similar(message)
    else:
        scenario, theme = '', ''
    prompt = f'''<|start_header_id|>user<|end_header_id|>

輕微改動一次以下原文人物和設定，讓情景更加新穎，但不要涉及歷史、犯罪、鬥爭或愛情。保留原意，選擇要明確一個合乎一個不合乎價值觀，不要說改動了什麼。原文主題是{theme}

原文：{scenario}

改動後：<|eot_id|><|start_header_id|>assistant<|end_header_id|>

'''
    if preload_mode:
        local_llm.create_state(prompt, 'scenario.pkl', max_tokens=1, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1)
        yield ''
    else:
        async for text in local_llm.local_llm_completion(prompt, stream=True, max_tokens=max_tokens, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1, state_file='scenario.pkl'):
            yield text

async def generate_scenario_persuasion(message_records: list, value, max_tokens=500, preload_mode=False):
    '''
    Generate follow-up questions based on the conversation between user and chatbot.
    message_record should be a list of messages in the following structure:
    - message
    - isUser
    '''
    prompt = f'''<|start_header_id|>user<|end_header_id|>

你是一名老師，根據學生的選擇符不符合價值觀作出一句短回應，讓學生回答。\
如果符合，簡單稱讚，之後問一個假設違反價值觀後果問題。\
如果不符合，溫柔說明違反的後果，引導學生更換選擇，不要壓力。\
如果偏離問題，帶回問題。價值觀為{value}。

'''
    for message_record in message_records:
        message = message_record['message']
        role = '學生' if message_record['isUser'] else '老師'
        prompt += f'{role}: {message}\n'
    prompt += '老師：<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
    if preload_mode:
        local_llm.create_state(prompt, 'persausion.pkl', max_tokens=1, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1)
        yield ''
    else:
        async for text in local_llm.local_llm_completion(prompt, stream=True, max_tokens=max_tokens, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1, state_file='persausion.pkl'):
            yield text

async def generate_scenario_feedback(message_records: list, value, max_tokens=500, preload_mode=False):
    '''
    Generate feedback based on the conversation between user and chatbot.
    message_record should be a list of messages in the following structure:
    - message
    - isUser
    '''
    prompt = f'''<|start_header_id|>user<|end_header_id|>

你是一名老師，根據你和學生的對話，以學生為第二人稱簡單總結，說說其他時候如何運用{value}。

'''
    for message_record in message_records:
        message = message_record['message']
        role = '學生' if message_record['isUser'] else '老師'
        prompt += f'{role}: {message}\n'
    prompt += '老師：<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n'
    if preload_mode:
        local_llm.create_state(prompt, 'feedback.pkl', max_tokens=1, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1)
        yield ''
    else:
        async for text in local_llm.local_llm_completion(prompt, stream=True, max_tokens=max_tokens, temperature=0.5, top_k=0, top_p=0.9, min_p=0.1, state_file='feedback.pkl'):
            yield text

async def preload_prompt():
    '''
    This preloads the prompts to the LLM for faster inference later.
    '''
    print('Preloading prompts...')
    print('Intent classification preloading...')
    await intent_classify('', 1, True)
    print('Story generation preloading...')
    [_ async for _ in generate_new_story('', 1, True)]
    print('QA generation preloading...')
    await generate_qa_pairs('', '', 1, True)
    print('Scenario generation preloading...')
    [_ async for _ in generate_scenario('', 1, True)]
    print('Scenario persuasion preloading...')
    [_ async for _ in generate_scenario_persuasion([], '', 1, True)]
    print('Scenario feedback preloading...')
    [_ async for _ in generate_scenario_feedback([], '', 1, True)]
    print('Prompts preloaded.')