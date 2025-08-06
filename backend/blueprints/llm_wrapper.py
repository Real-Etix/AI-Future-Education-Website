import os, openai
import asyncio
import time

from dotenv import load_dotenv
load_dotenv()

client = openai.OpenAI(
    api_key = os.getenv('POE_API_KEY'),   # Obtain this API from Poe and store it in .env file
    base_url = 'https://api.poe.com/v1'
)
bot = 'GPT-4o-mini'

async def llm_response(prompt):
    '''
    Send message to and receive response from Poe chatbot. 
    '''
    messages = [{'role': 'user', 'content': prompt}]
    response = client.chat.completions.create(
        model="GPT-4o-mini", # or other models (Claude-Sonnet-4, Gemini-2.5-Pro, Llama-3.1-405B, Grok-4..)
        messages = messages, # type: ignore
    )
    return response.choices[0].message.content if response.choices[0].message.content else ''





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    time1 = 0.0
    time2 = 0.0
    test_random_message = ['Test', "你好嗎？", "你在做什麼?", "嗯？", "Who are you?"]
    for i in range(5):
        test = [{
            'role': 'system', 'content': '你是一名測試員。',
            'role': 'user', 'content': '''假設你是想學習承諾的使用者，問一個和承諾有關的問題測試意圖分析員。

            例子： 
            使用者： 我想知道什麼是諾言

            使用者：
            '''
        }]
        test_message1 = asyncio.run(llm_response(test))
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

{test_message1}
意圖：'''
        messages1 = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        result = asyncio.run(llm_response(messages1))
        print('1:', test_message1, '->', result)
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
{test_message1}
意圖：\
'''
        }]
        start_time = time.time()
        result = asyncio.run(llm_response(messages2))
        print('2:', test_message1, '->', result)
        time2 += time.time() - start_time
        print(time.time() - start_time)
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
{test_random_message[i]}
意圖：'''
        messages1 = [{'role': 'user', 'content': prompt}]
        start_time = time.time()
        result = asyncio.run(llm_response(messages1))
        print('1:', test_random_message[i], '->', result)
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
{test_random_message[i]}
意圖：'''
        }]
        start_time = time.time()
        result = asyncio.run(llm_response(messages2))
        print('2:', test_random_message[i], '->', result)
        time2 += time.time() - start_time
        print(time.time() - start_time)
    print('Prompt 1 time:', time1)
    print('Prompt 2 time:', time2)
    # from tools import extract_chinese_between_chars
    # questions = extract_chinese_between_chars(result, '問題：', '')
    # answers = extract_chinese_between_chars(result, '答案：', '')
    # print(questions, answers)
    # print(re.compile(r'[\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]').findall('問題，'))