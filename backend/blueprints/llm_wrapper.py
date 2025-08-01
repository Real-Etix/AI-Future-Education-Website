# backend/blueprints/llm_wrapper.py

import asyncio
from poe_api_wrapper import PoeApi

# This is grabbed from cookie, which will spend the points from which account the cookies are made from
# You can get some of these tokens (value) from F12 -> Applications -> Cookies in Windows
# https://poe.com
# ---- TODO ----
tokens = { 
    'p-b': '2voV9fwV39Qpwv39EZV99A%3D%3D', # cookie
    'p-lat': 'poe-chan116-8888-gadmiwnuappsufahzjxs', # cookie (poe-tchannel-channel)
    'formkey': '785c8e50c2021eb3dd9a222721a981c6', # generated when launch, but needed for passing challenge sometimes
    'cf_clearance': 'JRFlAXglxNjYZhDAh_8j8VRoWmE6QoM.Nyqg2kXd7Ao-1753972180-1.2.1.1-OpTix.f7fw4219EwDiJFnDGh4pUvvEuLzNH2UIRajyK6GQn2uhun9vlTovQ4f8UgEZqB50v.XQ48VdNX.CjHRjFA_9OxnI.jrYmxAs1iknf9bFESVQPWIV0PLNbUP70Akup8viSwM0n5K6H8Eg1jVVdI1SrovaxHW48GDUPiSlb9s_6B111AY6kMtv9qL2LFmS0JmBptwiamflFed_lF1V6mKf_ety0YmyOysalPMdE' # cookie
}

client = PoeApi(tokens=tokens)
chat_code = None
bot='capybara'

async def collect_response(response):
    '''
    Joins the response in character form to a string.
    '''
    global chat_code
    result = []
    for chunk in response:
        result.append(chunk['response'])
    chat_code = chunk['chatCode']
    message = ''.join(result)
    return message

async def llm_response(message):
    '''
    Send message to and receive response from Poe chatbot. 
    '''
    if chat_code:
        response = await collect_response(client.send_message(bot=bot, message=message, chatCode=chat_code))
    else:
        response = await collect_response(client.send_message(bot=bot, message=message))
    if chat_code:
        client.chat_break(bot, chatCode=chat_code)
    return response


# This is for testing purposes to see if the prompt work properly.
if __name__ == '__main__':
    prompts = ['你好嗎？', '今日幾號？','作一個關於承諾的故事，故事要二百字內。']
    for prompt in prompts:
        result = asyncio.run(llm_response(prompt))
        print([result])
    if chat_code:
        client.delete_chat(bot, chatCode=chat_code)
    # from tools import extract_chinese_between_chars
    # questions = extract_chinese_between_chars(result, '問題：', '')
    # answers = extract_chinese_between_chars(result, '答案：', '')
    # print(questions, answers)
    # print(re.compile(r'[\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]').findall('問題，'))