""" CTF - models.py

This module contains the models for each table in the database
"""

from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Text, text
from sqlalchemy.orm import relationship

from ctf import db


class Categories(db.Model):
    """ A Category describes the type of Challenge. Challenges may have one Category.
    """

    __tablename__ = 'categories'

    name = Column(Text, primary_key=True)
    description = Column(Text, nullable=False)


class Difficulties(db.Model):
    """ Describes how difficult a Challenge is. Challenges may have one Difficulty.
    """

    __tablename__ = 'difficulties'

    name = Column(Text, primary_key=True)


class Challenges(db.Model):
    """ Challenges have a brief description, and then flags to be obtained!
    """

    __tablename__ = 'challenges'

    id = Column(Integer, primary_key=True)
    difficulty_name = Column(Text, ForeignKey('difficulties.name'), nullable=False, index=True)
    category_name = Column(Text, ForeignKey('categories.name'), nullable=False, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    tags = db.relationship('ChallengeTags', backref='challenges')
    category = relationship('Categories')
    difficulty = relationship('Difficulties')

    def __init__(self, difficulty: str, category: str, title: str, description: str):
        """
        Creates a Challenge

        :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
        :param category: Text description of the category. Must exist in Categories table.
        :param title: Title of the Challenge
        :param description: Description of the Challenge
        """
        self.difficulty = difficulty
        self.category = category
        self.title = title
        self.description = description

    @classmethod
    def create(cls, difficulty: str, category: str, title: str, description: str) -> dict:
        """
        Wraps the Challenge init method to immediately create and return a Challenge

        :param difficulty: Text description of the difficulty. Must exist in Difficulties table.
        :param category: Text description of the category. Must exist in Categories table.
        :param title: Title of the Challenge
        :param description: Description of the Challenge
        :return: The new Challenge
        """
        new_challenge = Challenges(difficulty, category, title, description)
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
            'tags': [tag.to_dict()['tag'] for tag in self.tags]
        }


class ChallengeTags(db.Model):
    """ Tags can describe aspects of a Challenge
    """

    __tablename__ = 'challenge_tags'

    challenge_id = Column(Integer, ForeignKey('challenges.id'),
                          primary_key=True, nullable=False, index=True)
    tag = Column(Text, primary_key=True, nullable=False)

    challenge = relationship('Challenges')

    def to_dict(self) -> dict:
        """
        :return: JSON serializable representation of a Challenge
        """
        return {
            'challenge_id': self.challenge_id,
            'tag': self.tag
        }


class Flags(db.Model):
    """ Flags are the objectives of a Challenge. Each has a point value and belongs to a Challenge
    """

    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True, server_default=text("nextval('flags_id_seq'::regclass)"))
    point_value = Column(SmallInteger, nullable=False)
    flag = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')


class Hints(db.Model):
    """Hints can be bought with points and give clues as to how a flag can be obtained
    """

    __tablename__ = 'hints'

    id = Column(Integer, primary_key=True, server_default=text("nextval('hints_id_seq'::regclass)"))
    cost = Column(SmallInteger, nullable=False)
    hint = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')


class Solved(db.Model):
    """This table name is dumb. It contains a list of which users have solved which flags.
    """

    __tablename__ = 'solved'

    flag_id = Column(ForeignKey('flags.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    flag = relationship('Flags')


class UsedHints(db.Model):
    """Contains a list of which users have purchased which keys
    """

    __tablename__ = 'used_hints'

    hint_id = Column(ForeignKey('hints.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    hint = relationship('Hints')
