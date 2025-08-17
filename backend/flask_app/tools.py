# backend/flask_app/tools.py

import re

def extract_chinese_between_chars(text, start, end=''):
    """
    Extracts Chinese characters between two specified Chinese characters.

    Args:
        text (str): The input string.
        start (str): The starting Chinese character.
        end (str): The ending Chinese character.

    Returns:
        list: A list of strings containing the extracted Chinese characters.
    """
    pattern = rf"{re.escape(start)}\s*([\u3000-\u303F\u4E00-\u9FFF\uFF00-\uFFEF]+)\s*{re.escape(end)}"
    matches = re.findall(pattern, text, re.UNICODE)
    for i in range(len(matches)):
        matches[i] = matches[i][3:] if matches[i][:3] == start else matches[i]
    return matches

async def obtain_text_from_generator(generator):
    """
    Collects text from an asynchronous generator.

    Args:
        generator (async generator): The asynchronous generator to collect text from.

    Returns:
        str: The collected text.
    """
    collected_text = []
    async for text in generator:
        collected_text.append(text)
    return ''.join(collected_text)

async def async_gen_to_coroutine(async_gen):
    """
    Converts an asynchronous generator to a coroutine that returns a list of items.

    Args:
        async_gen (async generator): The asynchronous generator to convert.

    Returns:
        coroutine: A coroutine that returns a list of items from the asynchronous generator.
    """
    return [item async for item in async_gen]