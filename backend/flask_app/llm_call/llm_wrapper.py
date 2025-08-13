# backend/blueprints/llm_call/llm_wrapper.py

import os, openai
import asyncio
import time

from dotenv import load_dotenv
load_dotenv()

client = None
bot = 'GPT-4o-mini'

async def llm_response(prompt, stream=False):
    '''
    Send message to and receive response from Poe chatbot. 
    '''

    global client
    if isinstance(prompt, list):
        # If prompt is a list, it is a message list
        messages = prompt
    else:
        # If prompt is a string, it is a single message
        messages = [{'role': 'user', 'content': prompt}]
    if not client:
        client = openai.OpenAI(
            api_key = os.getenv('POE_API_KEY'),   # Obtain this API from Poe and store it in .env file
            base_url = 'https://api.poe.com/v1'
        )
    response = client.chat.completions.create(
        model="GPT-4o-mini", # or other models (Claude-Sonnet-4, Gemini-2.5-Pro, Llama-3.1-405B, Grok-4..)
        messages = messages, # type: ignore
        stream=stream
    )
    if stream:
        for chunk in response:
            yield chunk.choices[0].delta.content if chunk.choices[0].delta.content else ''
    else:
        yield response.choices[0].message.content if response.choices[0].message.content else ''

async def llm_response_stream(prompt):
        async for text in llm_response(prompt, stream=True):
            print(text, end='', flush=True)
        print()  # Ensure a newline at the end





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    time1 = 0.0
    time2 = 0.0
    test_random_message = ['Test', "你好嗎？", "你在做什麼?", "嗯？", "Who are you?"]
    for i in range(5):
        prompt = f'''\
你要從回答中分析使用者的意圖。意圖可能是
- 承諾
- 問候
- 沒有

例子：
使用者： 我想知道什麼是諾言。
意圖： 承諾
使用者： 你是誰？
意圖： 問候
"""

使用者：{test_random_message[i]}
意圖：'''
        messages1 = [{'role': 'user', 'content': prompt}]
        print('1:', test_random_message[i], ':')
        start_time = time.time()
        asyncio.run(llm_response_stream(prompt))
        time1 += time.time() - start_time
        print(time.time() - start_time)
        messages2 = [{
            'role': 'system', 'content': '你是一名意圖分析員。',
            'role': 'user', 'content': f'''\
你要從回答中分析使用者的意圖。意圖可能是
- 承諾
- 問候
- 沒有

例子：
使用者： 我想知道什麼是諾言。
意圖： 承諾
使用者： 你是誰？
意圖： 問候
"""

使用者：{test_random_message[i]}
意圖：'''
        }]
        print('2:', test_random_message[i], ':')
        start_time = time.time()
        asyncio.run(llm_response_stream(messages2))
        time2 += time.time() - start_time
        print(time.time() - start_time)
    print('Prompt 1 time:', time1)
    print('Prompt 2 time:', time2)
    # from tools import extract_chinese_between_chars
    # questions = extract_chinese_between_chars(result, '問題：', '')
    # answers = extract_chinese_between_chars(result, '答案：', '')
    # print(questions, answers)
    # print(re.compile(r'[\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]').findall('問題，'))