# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship

from app.model import Base


# Модель Должности
class Position(Base):
    __tablename__ = 'position'
    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True)  # Название должности
    user = relationship("User", uselist=False, back_populates="position")

    @classmethod
    def get_id(cls):
        return Position.id

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(Position).filter(Position.name == name).first()

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Position {}>'.format(self.name)

    FIELDS = {
        'id': int,
        'name': str
    }

    FIELDS.update(Base.FIELDS)
