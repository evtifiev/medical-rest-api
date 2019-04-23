# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer, DateTime

from app.model import Base
from app.utils import alchemy
from datetime import datetime


# Модель праздничные дни
class Holiday(Base):
    __tablename__ = 'holiday'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    date = Column(DateTime)  # Дата поаздника
    name = Column(String(90), nullable=True)  # Наименование праздника

    def __repr__(self):
        return "<Holiday(name='%s')>" % \
               (self.name)

    @classmethod
    def get_id(cls):
        return Holiday.id

    def to_dict(self):
        obj = {
            "id": self.id,
            "name": self.name,
            "date": datetime.strftime(self.date, "%d.%m.%Y"),
            "created": alchemy.datetime_to_timestamp(self.created)
        }

        return obj



    FIELDS = {
        'id': int,
        'date': alchemy.datetime_to_timestamp,
        'name': str,
    }

    FIELDS.update(Base.FIELDS)
