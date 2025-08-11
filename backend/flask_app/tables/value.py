# backend/blueprints/tables/value.py

from sqlalchemy import select
from .database import db

class Value(db.Model):
    '''
    Define the structure of the value_categories table.
    This stores all the values.
    '''

    __tablename__ = 'value_categories'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(128), unique=True, nullable=False)
    description = db.Column(db.String(2048))
    
    link = db.relationship('StoryValueLink', backref='Value', passive_deletes=True)

    def __repr__(self):
        return '<Value %r>' % self.name

def get_value(value_id: int|None):
    '''
    Get the value with corresponding value id.
    '''
    result = db.session.execute(
        select(Value.name).filter_by(id=value_id)
    ).scalar()
    return result

def get_value_id(value_name: str):
    '''
    Get the value id with corresponding value name.
    '''
    result = db.session.execute(
        select(Value.id).filter_by(name=value_name)
    ).scalar()
    return result