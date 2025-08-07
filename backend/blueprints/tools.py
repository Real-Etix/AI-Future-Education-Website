# backend/blueprints/tools.py

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