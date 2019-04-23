# -*- coding: utf-8 -*-
from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.model import Base


# Справочник Подразделения
class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(255), unique=True)
    user = relationship("User", uselist=False, back_populates="department")

    @classmethod
    def get_id(cls):
        return Department.id

    @classmethod
    def find_by_name(cls, session, name):
        return session.query(Department).filter(Department.name == name).first()

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Department {}>'.format(self.name)

    FIELDS = {
        'id': int,
        'name': str
    }
    FIELDS.update(Base.FIELDS)
