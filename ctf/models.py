""" CTF - models.py

This module contains the models for each table in the database
"""

from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Text
from sqlalchemy.orm import relationship

from ctf import db


class Categories(db.Model):
    """A Category describes the type of Challenge. Challenges may have one Category."""

    __tablename__ = 'categories'

    name = Column(Text, primary_key=True)
    description = Column(Text, nullable=False)

    def __init__(self, name: str, description: str):
        """
        Initialization function for a Category

        :param name: Name of the category
        :param description: Description of the category
        """
        self.name = name
        self.description = description

    @classmethod
    def create(cls, name: str, description: str) -> dict:
        """
        Wraps flask-sqlalchemy functions to immediately create a category

        :param name: Name of the category
        :param description: Description of the category
        :return: Dictionary representation of a Category
        """
        new_category = Categories(name, description)
        db.session.add(new_category)
        db.session.commit()
        return new_category.to_dict()

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Category
        """
        return {
            'name': self.name,
            'description': self.description
        }

    def delete(self):
        """
        Deletes this Category from the database
        """
        db.session.delete(self)
        db.session.commit()


class Difficulties(db.Model):
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
        new_difficulty = Difficulties(name)
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


class Challenges(db.Model):
    """Challenges have a brief description, and then flags to be obtained!"""

    __tablename__ = 'challenges'

    id = Column(Integer, primary_key=True)
    difficulty_name = Column(ForeignKey('difficulties.name'), nullable=False, index=True)
    category_name = Column(ForeignKey('categories.name'), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    author = Column(Text, nullable=False)
    submitter = Column(Text, nullable=False)

    tags = db.relationship('ChallengeTags', backref='challenges')
    category = relationship('Categories')
    difficulty = relationship('Difficulties')
    flags = db.relationship('Flags', backref='challenges')

    def __init__(self, title: str, description: str, author: str,
                 submitter: str, difficulty: str, category: str):
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

    @classmethod
    def create(cls, title: str, description: str, author: str, submitter: str, difficulty: str,
               category: str) -> dict:
        """
        Wraps some flask-sqlalchemy functions to immediately commit new Challenge to the database


        :param title: Title of the Challenge
        :param description: Description of the Challenge
        :param author: The person who created this challenge
        :param submitter: The account that submitted this challenge
        :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
        :param category: Text description of the category. Must exist in Categories table.
        :return: The new Challenge
        """
        new_challenge = Challenges(title, description, author, submitter, difficulty, category)
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
            'submitter': self.submitter
        }

    def delete(self):
        """
        Deletes this challenge from the database
        """
        db.session.delete(self)
        db.session.commit()


class ChallengeTags(db.Model):
    """Tags can describe aspects of a Challenge"""

    __tablename__ = 'challenge_tags'

    challenge_id = Column(Integer, ForeignKey('challenges.id'),
                          primary_key=True, nullable=False, index=True)
    tag = Column(Text, primary_key=True, nullable=False)

    challenge = relationship('Challenges')

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
        new_tag = ChallengeTags(challenge_id, tag)
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


class Flags(db.Model):
    """Flags are the objectives of a Challenge. Each has a point value and belongs to a Challenge"""

    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True)
    point_value = Column(SmallInteger, nullable=False)
    flag = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')

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
        new_flag = Flags(point_value, flag, challenge_id)
        db.session.add(new_flag)
        db.session.commit()
        return new_flag.to_dict()

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



class Hints(db.Model):
    """Hints can be bought with points and give clues as to how a flag can be obtained"""

    __tablename__ = 'hints'

    id = Column(Integer, primary_key=True)
    cost = Column(SmallInteger, nullable=False)
    hint = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')


class Solved(db.Model):
    """This table name is dumb. It contains a list of which users have solved which flags."""

    __tablename__ = 'solved'

    flag_id = Column(ForeignKey('flags.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    flag = relationship('Flags')


class UsedHints(db.Model):
    """Contains a list of which users have purchased which keys"""

    __tablename__ = 'used_hints'

    hint_id = Column(ForeignKey('hints.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    hint = relationship('Hints')
