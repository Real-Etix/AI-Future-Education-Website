# backend/blueprints/tables/story_cache.py

from sqlalchemy import select, update, delete
from .database import db

class StoryCache(db.Model):
    '''
    Define the structure of the story_cache table.
    The purpose is to temporary store the stories to be shared across.
    '''

    __bind_key__ = 'chats_db' # Binds to the chat database
    __tablename__ = 'story_cache'
    chat_id = db.Column(db.Integer, primary_key=True, nullable=False)
    story = db.Column(db.String(2048), nullable=False)

def exist_story_cache_record(chat_id):
    return db.session.execute(select(StoryCache.chat_id).where(StoryCache.chat_id == chat_id)).first() is not None

def get_story_from_cache(chat_id):
    '''
    Get the story from cache.
    '''
    return db.session.execute(
        select(StoryCache.story).filter_by(chat_id = chat_id)
    ).scalar()

def store_story_to_cache(chat_id, story):
    '''
    Store the story to cache.
    '''
    if exist_story_cache_record(chat_id):
        db.session.execute(update(StoryCache), [{'chat_id': chat_id, 'story': story}])
        db.session.commit()
    else:
        story_row = StoryCache(chat_id=chat_id, story=story) # type: ignore
        db.session.add(story_row)
        db.session.commit()

def clear_story_cache(chat_id):
    '''
    Clear the story in cache for given chat.
    '''
    db.session.execute(delete(StoryCache).where(StoryCache.chat_id == chat_id))
    db.session.commit()
