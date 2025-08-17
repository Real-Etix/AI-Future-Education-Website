# backend/append_story.py

# This file is for testing on adding a story with specified values.
# The database consists of 3 tables: stories, value_categories, stories_values
# stories table stores the individual stories.
# value_categories table stores different values or other categories.
# stories_values table links the stories with the values together.
import sqlite3
import asyncio
from flask_app.llm_prompt import summarize_story


DATABASE = 'backend/database/stories.db'
def append_story(title: str, story: str, values: list, img_link = 'template-pic.jpeg'):
    summary = asyncio.run(summarize_story(story))
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(
        '''
        INSERT INTO stories (title, story, summary, img_link) VALUES (?, ?, ?, ?) 
        ON CONFLICT(title, story) DO UPDATE SET summary = excluded.summary
        ''',
        (title, story, summary, img_link)
    )
    cursor.execute(
        'SELECT id FROM stories WHERE title = ? AND story = ?',
        (title, story)
    )
    story_id = cursor.fetchone()[0]
    for value in values:
        cursor.execute(
            'INSERT OR IGNORE INTO value_categories (name) VALUES (?)',
            (value,)
        )
        cursor.execute(
            'SELECT id FROM value_categories WHERE name = ?',
            (value,)
        )
        value_id = cursor.fetchone()[0]
        cursor.execute(
            'INSERT OR IGNORE INTO stories_values VALUES (?, ?)',
            (story_id, value_id,)
        )
        db.commit()


title = "承諾的力量"
story = ''.join([
        "在一個寧靜的小村莊裡，住著一位名叫小雨的女孩。她和母親相依為",
        "命，母親常常告訴她：「承諾就像一朵花，需要精心呵護。」小雨深",
        "知這句話的意義，於是立志要成為一個守信的人。\n\n",
        "有一天，村莊裡的老奶奶生病了，村民們都忙著自己的事，沒有人願",
        "意去照顧她。小雨心裡想起了母親的話，決定去幫助老奶奶。她每天",
        "下午都會帶著食物，陪伴老奶奶聊天，讓她不再孤單。\n\n",
        "隨著時間的推移，老奶奶的健康逐漸好轉，村民們也開始注意到小雨",
        "的付出。他們紛紛向小雨請教，如何才能像她一樣守信。小雨微笑著",
        "說：「只要心中有承諾，就會有力量去實踐。」\n\n",
        "一天，老奶奶感謝小雨，送她一朵自己親手編織的花朵，並說：「這",
        "是我對你承諾的回報，永遠記住，真誠的心能夠改變世界。」小雨接",
        "過花朵，心裡充滿了暖意。\n\n",
        "從那以後，小雨更加堅定了自己的信念，無論是對朋友還是對家人，",
        "她都始終如一地履行著自己的承諾。小村莊的每個人都因此變得更加",
        "團結，因為小雨的故事告訴他們，承諾的力量無遠弗屆。"
    ])
values = ['承諾']
append_story(title, story, values)