# backend/blueprints/tables/story_value_link.py

from sqlalchemy import select, func
from .database import db

class StoryValueLink(db.Model):
    '''
    Define the structure of the stories_values table.
    This links the stories and values together.
    '''
    
    __tablename__ = 'stories_values'
    story_id = db.Column(db.Integer, db.ForeignKey('stories.id', ondelete='CASCADE'), primary_key=True, nullable=False)
    value_id = db.Column(db.Integer, db.ForeignKey('value_categories.id', ondelete='CASCADE'), primary_key=True, nullable=False)

    def __repr__(self):
        return '<Value %r-%r>' % (self.story_id, self.value_id)

def get_random_story(value_id):
    '''
    Get a story randomly that is about the specific value.
    '''
    return db.session.execute(
        select(StoryValueLink.story_id).filter_by(value_id=value_id).order_by(func.random())
    ).scalar()

def get_random_value(story_id):
    '''
    Get a value randomly that the story is about.
    '''
    return db.session.execute(
        select(StoryValueLink.value_id).filter_by(story_id=story_id).order_by(func.random())
    ).scalar()