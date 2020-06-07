""" CTF - models.py

This module contains the models for each table in the database
"""
from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Text, DateTime, Boolean
from sqlalchemy.orm import relationship

from ctf import db


class Category(db.Model):
    """A Category describes the type of Challenge. Challenges may have one Category."""

    __tablename__ = 'categories'

    name = Column(Text, primary_key=True)
    description = Column(Text, nullable=False)
    upload_required = Column(Boolean)

    def __init__(self, name: str, description: str, upload_required: bool):
        """
        Initialization function for a Category

        :param name: Name of the category
        :param description: Description of the category
        """
        self.name = name
        self.description = description
        self.upload_required = upload_required

    @classmethod
    def create(cls, name: str, description: str, upload_required: bool) -> dict:
        """
        Wraps flask-sqlalchemy functions to immediately create a category

        :param name: Name of the category
        :param description: Description of the category
        :return: Dictionary representation of a Category
        """
        new_category = Category(name, description, upload_required)
        db.session.add(new_category)
        db.session.commit()
        return new_category.to_dict()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Category
        """
        return {
            'name': self.name,
            'description': self.description,
            'upload_required': bool(self.upload_required)
        }

    def delete(self):
        """
        Deletes this Category from the database
        """
        db.session.delete(self)
        db.session.commit()


class Difficulty(db.Model):
    """Describes how difficult a Challenge is. Challenges may have one Difficulty."""

    __tablename__ = 'difficulties'

    name = Column(Text, primary_key=True)

    def __init__(self, name: str):
        """
        Initializes a Difficulty
        """
        self.name = name

    @classmethod
    def create(cls, name: str) -> dict:
        """
        Wrapper to immediately put new Difficulty into database
        """
        new_difficulty = Difficulty(name)
        db.session.add(new_difficulty)
        db.session.commit()
        return new_difficulty.to_dict()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Difficulty
        """
        return {
            'name': self.name
        }

    def delete(self):
        """
        Deletes this Difficulty from the database
        """
        db.session.delete(self)
        db.session.commit()


class Challenge(db.Model):
    """Challenges have a brief description, and then flags to be obtained!"""

    __tablename__ = 'challenges'

    id = Column(Integer, primary_key=True)
    difficulty_name = Column(ForeignKey('difficulties.name'), nullable=False, index=True)
    category_name = Column(ForeignKey('categories.name'), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    submitter = Column(Text, nullable=False)
    filename = Column(Text)
    ts = Column(DateTime, default=datetime.utcnow().isoformat)

    tags = db.relationship('ChallengeTag', backref='challenges')
    category = relationship('Category')
    difficulty = relationship('Difficulty')
    flags = db.relationship('Flag', backref='challenges')

    def __init__(self, title: str, description: str, author: str,
                 submitter: str, difficulty: str, category: str, filename: str = None):
        """
        Creates a Challenge

        :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
        :param category: Text description of the category. Must exist in Categories table.
        :param title: Title of the Challenge
        :param description: Description of the Challenge
        """
        self.title = title
        self.description = description
        self.author = author
        self.submitter = submitter
        self.difficulty = difficulty
        self.category = category
        self.filename = filename

    @classmethod
    def create(cls, title: str, description: str, author: str, submitter: str, difficulty: str,
               category: str, filename: str = None) -> dict:
        """
        Wraps some flask-sqlalchemy functions to immediately commit new Challenge to the database


        :param title: Title of the Challenge
        :param description: Description of the Challenge
        :param author: The person who created this challenge
        :param submitter: The account that submitted this challenge
        :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
        :param category: Text description of the category. Must exist in Categories table.
        :param filename: Name of the file associated with this Challenge
        :return: The new Challenge
        """
        new_challenge = Challenge(title, description, author, submitter, difficulty, category,
                                  filename)
        db.session.add(new_challenge)
        db.session.commit()
        return new_challenge.to_dict()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Challenge
        """
        return {
            'id': self.id,
            'difficulty': self.difficulty_name,
            'category': self.category_name,
            'title': self.title,
            'description': self.description,
            'tags': [tag.to_dict()['tag'] for tag in self.tags],
            'author': self.author,
            'submitter': self.submitter,
            'ts': self.ts,
            'filename': self.filename
        }

    def delete(self):
        """
        Deletes this challenge from the database
        """
        db.session.delete(self)
        db.session.commit()


class ChallengeTag(db.Model):
    """Tags can describe aspects of a Challenge"""

    __tablename__ = 'challenge_tags'

    challenge_id = Column(Integer, ForeignKey('challenges.id'),
                          primary_key=True, nullable=False, index=True)
    tag = Column(Text, primary_key=True, nullable=False)

    challenge = relationship('Challenge')

    def __init__(self, challenge_id: int, tag: str):
        """
        Initializes a ChallengeTag
        """
        self.challenge_id = challenge_id
        self.tag = tag

    @classmethod
    def create(cls, challenge_id: int, tag: str) -> dict:
        """
        Immediately commits new ChallengeTag to the database
        """
        new_tag = ChallengeTag(challenge_id, tag)
        db.session.add(new_tag)
        db.session.commit()
        return new_tag.to_dict()

    def delete(self):
        """
        Deletes this instance of ChallengeTag from the database
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Challenge
        """
        return {
            'challenge_id': self.challenge_id,
            'tag': self.tag
        }


class Flag(db.Model):
    """Flags are the objectives of a Challenge. Each has a point value and belongs to a Challenge"""

    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True)
    point_value = Column(SmallInteger, nullable=False)
    flag = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenge')
    hints = relationship('Hint')
    solved = relationship('Solved')

    def __init__(self, point_value: int, flag: str, challenge_id: int):
        """
        Create a Flag

        :param point_value: The points to be awarded to those who solve the flag
        :param flag: The flag's data, to be solved by the user
        :param challenge_id: The ID this flag corresponds to
        """
        self.point_value = point_value
        self.flag = flag
        self.challenge_id = challenge_id

    @classmethod
    def create(cls, point_value: int, flag: str, challenge_id: int) -> dict:
        """
        Wraps some flask-sqlalchemy functions to immediately commit the new flag to the database

        :param point_value: The points to be awarded to those who solve the flag
        :param flag: The flag's data, to be solved by the user
        :param challenge_id: The ID this flag corresponds to
        """
        new_flag = Flag(point_value, flag, challenge_id)
        db.session.add(new_flag)
        db.session.commit()
        return new_flag.to_dict()

    def delete(self):
        """
        Removes this instance of Flag from the database
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Flag
        """

        return {
            'id': self.id,
            'point_value': self.point_value,
            'flag': self.flag,
            'challenge_id': self.challenge_id
        }


class Hint(db.Model):
    """Hints can be bought with points and give clues as to how a flag can be obtained"""

    __tablename__ = 'hints'

    id = Column(Integer, primary_key=True)
    cost = Column(SmallInteger, nullable=False)
    hint = Column(Text, nullable=False)
    flag_id = Column(ForeignKey('flags.id'), nullable=False, index=True)

    flag = relationship('Flag')

    def __init__(self, cost: int, hint: str, flag_id: int):
        """
        Initializes a hint
        """
        self.cost = cost
        self.hint = hint
        self.flag_id = flag_id

    @classmethod
    def create(cls, cost: int, hint: str, flag_id: int) -> dict:
        """
        Create new hint and immediately commit it to the database
        """
        new_hint = Hint(cost, hint, flag_id)
        db.session.add(new_hint)
        db.session.commit()
        return new_hint.to_dict()

    def delete(self):
        """
        Removes this instance of hint from the database
        """
        db.session.delete(self)
        db.session.commit()

    def to_dict(self) -> dict:
        """
        :return: A JSON serializable representation of a hint
        """
        return {
            'id': self.id,
            'cost': self.cost,
            'hint': self.hint,
            'flag_id': self.flag_id
        }


class Solved(db.Model):
    """This table name is dumb. It contains a list of which users have solved which flags."""

    __tablename__ = 'solved'

    flag_id = Column(ForeignKey('flags.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    flag = relationship('Flag')

    def __init__(self, flag_id: int, username: str):
        """
        Initializes a Solved relationship

        :param flag_id: The ID of the flag that's been solved
        :param username: The username of the person who solved the flag
        """
        self.flag_id = flag_id
        self.username = username

    @classmethod
    def create(cls, flag_id: int, username: str):
        """
        Immediately creates a Solved relationship and commits it to the database

        :param flag_id: The ID of the flag that's been solved
        :param username: The username of the person who solved the flag
        """
        new_solved = Solved(flag_id, username)
        db.session.add(new_solved)
        db.session.commit()
        return new_solved.to_dict()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Solved relationship
        """
        return {
            'flag_id': self.flag_id,
            'username': self.username
        }

    def delete(self):
        """
        Deletes this instance of a Solved relationship and commits that to the database
        """
        db.session.delete(self)
        db.session.commit()


class UsedHint(db.Model):
    """Contains a list of which users have purchased which keys"""

    __tablename__ = 'used_hints'

    hint_id = Column(ForeignKey('hints.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    hint = relationship('Hint')

    def __init__(self, hint_id: int, username: str):
        """
        Initializes a new used hint relation

        :param hint_id: ID of hint that this relation belongs to
        :param username: The username of the person who purchased the hint
        """
        self.hint_id = hint_id
        self.username = username

    @classmethod
    def create(cls, hint_id: int, username: str):
        """
        Creates and immediately inserts UsedHint into database

        :param hint_id: ID of hint that this relation belongs to
        :param username: The username of the person who purchased the hint
        """
        new_used_hint = UsedHint(hint_id, username)
        db.session.add(new_used_hint)
        db.session.commit()
        return new_used_hint

    def to_dict(self) -> dict:
        """
        :return: A JSON serializable representation of a UsedHint
        """
        return {
            'hint_id': self.hint_id,
            'username': self.username
        }
