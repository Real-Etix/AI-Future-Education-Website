# backend/append_story.py

# This file is for testing on adding a story with specified values.
# The database consists of 3 tables: stories, value_categories, stories_values
# stories table stores the individual stories.
# value_categories table stores different values or other categories.
# stories_values table links the stories with the values together.
import sqlite3


DATABASE = 'database/stories.db'
def append_story(title: str, story: str, values: list, img_link = 'template-pic.jpeg'):
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cursor = db.cursor()
    cursor.execute(
        'INSERT OR IGNORE INTO stories (title, story, img_link) VALUES (?, ?, ?)',
        (title, story, img_link)
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


# title = "季札贈劍"
# story = '''春秋時期，吳國貴族季札出使拜訪徐國。徐國國君在接待季札時，看到了他佩帶的寶劍，流露出喜愛之情。細心的季札看出徐國國君的心意，但作為吳國使節，他到各諸侯國拜訪時不能沒有寶劍作配飾，這是一種外交禮儀，他不能不遵守，有辱自己的使命。於是季札向他承諾，完成出使後，必定把寶劍送給徐國國君。 
# 過了一段時間，季札終於完成出使任務，回程時途經徐國，他想去拜訪徐國國君，以贈送寶劍，卻驚訝發現徐國國君已死。季札感到十分遺憾，萬分悲痛地來到徐國國君墓前祭奠。祭奠完畢，他解下身上的寶劍，把它掛在墓旁的樹上。這時，侍從疑惑地問，為甚麼徐國國君已死，季札仍要留下珍貴的寶劍呢？季札解釋，當時他已承諾給徐國國君贈劍，不能因為徐國國君已死，就違背自己的諾言。'''
# values = ['承諾']
title = 'Story 5'
story = title
values = ['承諾']
append_story(title, story, values)