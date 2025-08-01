# backend/blueprints/tables/user.py

from sqlalchemy import select
from datetime import datetime, timezone
from .database import db

class User(db.Model):
    '''
    Define the structure of the users table.
    '''

    __bind_key__ = 'chats_db' # Binds to the chat database
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100))
    created_at = db.Column(db.String(30), nullable=False)

    chat = db.relationship('Chat', backref='User', passive_deletes=True)

    def __repr__(self):
        return '<User %r>' % self.name

def add_user(name):
    '''
    Add the user with the given name to the database.
    '''
    creation_time = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + 'Z'
    new_user = User(name=name, last_updated=creation_time) # type: ignore
    db.session.add(new_user)
    db.session.commit()
    return new_user.id

if __name__ == '__main__':
    add_user('admin')