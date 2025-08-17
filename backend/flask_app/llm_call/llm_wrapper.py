# backend/flask_app/llm_call/llm_wrapper.py

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
        response  = ""
        async for text in llm_response(prompt, stream=True):
            print(text, end='', flush=True)
            response += text
        print()  # Ensure a newline at the end
        return response





# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    import csv
    import re
    def extract_chinese_between_chars(text, start, end=''):
        pattern = rf"{re.escape(start)}\s*([\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]+)\s*{re.escape(end)}"
        matches = re.findall(pattern, text, re.UNICODE)
        for i in range(len(matches)):
            matches[i] = matches[i][3:] if matches[i][:3] == start else matches[i]
        return matches
    
    id = 0
    existing_data = []
    try:
        with open('backend/database/scenario.csv', 'r', newline='', encoding='utf-8') as infile:
            reader = csv.DictReader(infile, quotechar='"')
            fieldnames = reader.fieldnames
            for row in reader:
                id += 1
                existing_data.append(row)
    except FileNotFoundError:
        fieldnames = ['id', '兩難','主題']
    for i in range(1):
        prompt = '''\
你是一名老師。請為學生建立一個關於可能違背承諾的兩難事件情景題，不要太簡單！以學生為主角，問題需要問學生會怎樣做，盡量貼近學生經驗，例如活動、清潔、學業、偶像等等，限制一個段落和問題。用詞語說主題除了承諾還有什麼。

例子（第三人稱）："""
兩難：{放入背景、承諾、兩難}。如果你是{輸入主角}，你會怎麼做？
主題：承諾、...
"""

例子（第二人稱）："""
兩難：{放入背景、承諾、兩難}。你會怎麼做？
主題：承諾、...
"""

兩難：

'''
        messages1 = [{'role': 'user', 'content': prompt}]
        response = asyncio.run(llm_response_stream(prompt))
        topic = extract_chinese_between_chars(response, '主題：')
        scenario = extract_chinese_between_chars(response, '兩難：')
        id += 1
        existing_data.append({'id': id,'兩難': scenario[0] if scenario else '', '主題': topic[0] if topic else ''})
    with open('backend/database/scenario.csv', 'w', newline='', encoding='utf-8') as outfile:
        csvWriter = csv.DictWriter(outfile, fieldnames=fieldnames, quotechar='"') # type: ignore
        csvWriter.writeheader()
        csvWriter.writerows(existing_data)
    # from tools import extract_chinese_between_chars
    # questions = extract_chinese_between_chars(result, '問題：', '')
    # answers = extract_chinese_between_chars(result, '答案：', '')
    # print(questions, answers)
    # print(re.compile(r'[\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]').findall('問題，'))