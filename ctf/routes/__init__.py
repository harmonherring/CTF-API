""" CTF - routes/__init__.py

Contains imported routes to be easily imported by the core of the application
"""

from .categories import categories_bp as categories
from .difficulties import difficulties_bp as difficulties
from .challenges import challenges_bp as challenges
from .tags import tags_bp as tags
from .solved import solved_bp as solved
from .flags import flags_bp as flags
