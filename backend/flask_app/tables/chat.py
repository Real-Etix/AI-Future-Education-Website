# backend/blueprints/tables/chat.py

from sqlalchemy import select, update
from datetime import datetime, timezone
from .database import db

class Chat(db.Model):
    '''
    Define the structure of the chats table.
    '''

    __bind_key__ = 'chats_db' # Binds to the chat database
    __tablename__ = 'chats'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(128))
    value = db.Column(db.String(128))
    '''
    Status represents the current operation of chat.
    0: Waiting / Complete
    1: Pending response
    '''
    status = db.Column(db.Integer, nullable=False)

    '''
    Stage represents the different stages of the chat.
    0: Asking user what value or story to learn
    1: Story
    2: Generating questions and answer
    3: Showing Questions 
    4: Asking user about his similar scenario
    5: Generating similar scenario
    6: Scenario Response
    7: Scenario Feedback
    8: Ended Conversation
    '''
    stage = db.Column(db.Integer, nullable=False)
    last_updated = db.Column(db.String(30), nullable=False)

    messages = db.relationship('Message', backref='Chat', passive_deletes=True)
    question_link = db.relationship('QuestionCache', backref='Chat', passive_deletes=True)

    def __repr__(self):
        return '<Chat %r>' % self.name

def get_chat_name(chat_id: int):
    '''
    Get the chat name with corresponding chat id.
    '''
    return db.session.execute(
        select(Chat.name).filter_by(id=chat_id)
    ).scalar()

def get_chat_list(user_id: int) -> list:
    '''
    Get the chat list corresponding to the user id.
    The returned list contains:
    - id
    - name
    - lastUpdated
    '''
    result = db.session.execute(
        select(Chat.id, Chat.name, Chat.last_updated).filter_by(user_id = user_id)
    ).all()
    return [{'id': row[0], 'name': row[1], 'lastUpdated': row[2]} for row in result]

def get_chat_stage(chat_id: int):
    '''
    Get the current stage of the chat.
    '''
    return db.session.execute(
        select(Chat.stage).filter_by(id=chat_id)
    ).scalar()

def get_chat_status(chat_id: int):
    '''
    Get the current status of the chat.
    '''
    result = db.session.execute(
        select(Chat.status).filter_by(id=chat_id)
    ).scalar()
    return 'Pending' if result else 'Complete'

def get_chat_value(chat_id: int):
    '''
    Get the value of the chat.
    '''
    return db.session.execute(
        select(Chat.value).filter_by(id=chat_id)
    ).scalar()

def get_chat_last_updated(chat_id: int):
    '''
    Get the last updated time of the chat.
    '''
    return db.session.execute(
        select(Chat.last_updated).filter_by(id=chat_id)
    ).scalar()

def set_chat_value(chat_id: int, value: str|None):
    '''
    Set the value of specified chat.
    '''
    db.session.execute(
        update(Chat), [{'id': chat_id, 'value': value}]
    )
    db.session.commit()

def update_chat_status(chat_id: int, status: int):
    '''
    Update the stage of the chat.
    '''
    db.session.execute(
        update(Chat), [{'id': chat_id, 'status': status}]
    )
    db.session.commit()
    return 'Pending' if status else 'Complete'

def update_chat_stage(chat_id: int, stage: int):
    '''
    Update the stage of the chat.
    '''
    db.session.execute(
        update(Chat), [{'id': chat_id, 'stage': stage}]
    )
    db.session.commit()

def update_chat_last_updated(chat_id):
    '''
    Update the last updated time of the chat.
    '''
    update_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
    db.session.execute(
        update(Chat), [{'id': chat_id, 'last_updated': update_time}]
    )
    db.session.commit()

def append_chat(user_id: int, name: str, stage: int) -> int:
    '''
    Append the chat to the database.
    '''
    creation_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
    new_chat = Chat(user_id=user_id, name=name, status=0, stage=stage, last_updated=creation_time) # type: ignore
    db.session.add(new_chat)
    db.session.commit()
    return new_chat.id