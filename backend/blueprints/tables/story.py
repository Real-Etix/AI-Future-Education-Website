# backend/blueprints/tables/story.py

from sqlalchemy import select
from .database import db

class Story(db.Model):
    '''
    Define the structure of the stories table.
    '''

    __tablename__ = 'stories'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    title = db.Column(db.String(50))
    story = db.Column(db.String(2048))
    author = db.Column(db.String(128))
    img_link = db.Column(db.String(256))

    link = db.relationship('StoryValueLink', backref='Story', passive_deletes=True)

    def __repr__(self):
        return '<Story %r>' % self.title

def get_story(story_id):
    '''
    Get the story with corresponding story id.
    '''
    return db.session.execute(
        select(Story.title, Story.story).filter_by(id=story_id)
    ).one()

def get_story_list():
    '''
    Get the list of all stories.
    '''
    return db.session.execute(
        select(Story.id, Story.title, Story.img_link)
    ).all()