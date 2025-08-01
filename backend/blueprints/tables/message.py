# backend/blueprints/tables/message.py

from sqlalchemy import select, func, and_
from datetime import datetime, timezone
from .database import db

class Message(db.Model):
    '''
    Define the structure of the chat_messages table.
    '''

    __bind_key__ = 'chats_db' # Binds to the chat database
    __tablename__ = 'chat_messages'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    chat_id = db.Column(db.Integer, db.ForeignKey('chats.id', ondelete='CASCADE'), nullable=False)
    stage = db.Column(db.Integer)
    message = db.Column(db.String(1024))
    created_at = db.Column(db.String(30), nullable=False)
    sent_by_user = db.Column(db.Integer, db.CheckConstraint('sent_by_user IN (0,1)'), nullable=False)

    def __repr__(self):
        return 'Message: %r' % self.message

def get_message(message_id: int):
    '''
    Get the message with corrresponding id.
    '''
    return db.session.execute(
        select(Message.message).filter_by(id = message_id)
    ).scalar()

def get_last_message(chat_id: int):
    '''
    Get the latest message of the chat. 
    '''
    result = db.session.execute(
        select(Message.message).filter_by(chat_id = chat_id).order_by(Message.created_at.desc())
    ).scalar()
    return result if result else ''

def get_message_list(chat_id: int) -> list:
    '''
    Get the message list of the chat.
    The returned list contains:
    - message
    - createdAt
    - isUser
    '''
    result = db.session.execute(
        select(Message.message, Message.created_at, Message.sent_by_user).filter_by(chat_id = chat_id).order_by(Message.created_at.asc())
    ).all()
    return [{'message': row[0], 'createdAt': row[1],'isUser': row[2]} for row in result]

def get_user_message_count(chat_id: int, stage: int):
    '''
    Get the number of user messages in the specific stage.
    '''
    result = db.session.execute(
        select(Message.chat_id, func.count()).filter_by(stage = stage, sent_by_user = 1).group_by(Message.chat_id).having(Message.chat_id == chat_id)
    ).first()
    return result[1] if result else 0

def get_stage_message(chat_id: int, stage: int) -> list:
    '''
    Get the messages of specifc stage.
    The returned list contains:
    - message
    - isUser
    '''
    result = db.session.execute(
        select(Message.message, Message.sent_by_user).filter_by(chat_id = chat_id, stage = stage).order_by(Message.created_at.asc())
    )
    return [{'message': row[0], 'isUser': row[1]} for row in result]

def append_message(chat_id: int, stage: int | None, message: str, is_user: int):
    '''
    Add the message to the database with the corresponding chat.
    '''
    creation_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
    new_message = Message(chat_id=chat_id, stage=stage, message=message, created_at=creation_time, sent_by_user=is_user) # type: ignore
    db.session.add(new_message)
    db.session.commit()
    return new_message.id, creation_time