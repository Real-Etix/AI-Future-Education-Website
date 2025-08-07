# backend/blueprints/__init__.py

# These class table definitions need to be imported in order to register foreign keys.
from .tables import *
from .llm_call import classify_llm
from .chat_api import chat_api
from .story_api import story_api
from .llm_prompt import preload_prompt