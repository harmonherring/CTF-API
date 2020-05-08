# coding: utf-8
from sqlalchemy import Column, ForeignKey, Integer, SmallInteger, Text, text
from sqlalchemy.orm import relationship

from ctf import db


class Categories(db.Model):
    __tablename__ = 'categories'

    name = Column(Text, primary_key=True)
    description = Column(Text, nullable=False)


class Difficulties(db.Model):
    __tablename__ = 'difficulties'

    name = Column(Text, primary_key=True)


class Challenges(db.Model):
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
        self.difficulty = difficulty
        self.category = category
        self.title = title
        self.description = description

    @classmethod
    def create(cls, difficulty: str, category: str, title: str, description: str) -> dict:
        new_challenge = Challenges(difficulty, category, title, description)
        db.session.add(new_challenge)
        db.session.commit()
        return new_challenge.to_dict()

    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'difficulty': self.difficulty_name,
            'category': self.category_name,
            'title': self.title,
            'description': self.description,
            'tags': [tag.to_dict()['tag'] for tag in self.tags]
        }


class ChallengeTags(db.Model):
    __tablename__ = 'challenge_tags'

    challenge_id = Column(Integer, ForeignKey('challenges.id'), primary_key=True, nullable=False, index=True)
    tag = Column(Text, primary_key=True, nullable=False)

    challenge = relationship('Challenges')

    def to_dict(self) -> dict:
        return {
            'challenge_id': self.challenge_id,
            'tag': self.tag
        }


class Flags(db.Model):
    __tablename__ = 'flags'

    id = Column(Integer, primary_key=True, server_default=text("nextval('flags_id_seq'::regclass)"))
    point_value = Column(SmallInteger, nullable=False)
    flag = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')


class Hints(db.Model):
    __tablename__ = 'hints'

    id = Column(Integer, primary_key=True, server_default=text("nextval('hints_id_seq'::regclass)"))
    cost = Column(SmallInteger, nullable=False)
    hint = Column(Text, nullable=False)
    challenge_id = Column(ForeignKey('challenges.id'), nullable=False, index=True)

    challenge = relationship('Challenges')


class Solved(db.Model):
    __tablename__ = 'solved'

    flag_id = Column(ForeignKey('flags.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    flag = relationship('Flags')


class UsedHints(db.Model):
    __tablename__ = 'used_hints'

    hint_id = Column(ForeignKey('hints.id'), primary_key=True, nullable=False, index=True)
    username = Column(Text, primary_key=True, nullable=False)

    hint = relationship('Hints')
