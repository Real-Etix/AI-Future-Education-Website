# backend/blueprints/tables/database.py

from flask_sqlalchemy import SQLAlchemy

# This file mainly stores the database object to be shared across files
db = SQLAlchemy()