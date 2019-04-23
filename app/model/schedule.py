# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer, ForeignKey, DateTime, Boolean
from app.utils import alchemy
from sqlalchemy.orm import relationship

from app.model import Base


# Таблица для хранения расписания врачей
class Schedule(Base):
    __tablename__ = 'schedule'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    date_start = Column(DateTime)
    date_end = Column(DateTime)
    doctor_id = Column(Integer, ForeignKey('doctor.id'))
    creator_id = Column(Integer, ForeignKey('user.id'))
    is_busy = Column(Boolean, default=False)

    doctor = relationship("Doctor", backref='schedule', primaryjoin="Schedule.doctor_id==Doctor.id")

    def to_dict(self):
        obj = {
            "id": self.id,
            "doctor": self.doctor.user.full_name,
            "date_start": alchemy.datetime_to_timestamp(self.date_start) * 1000,
            "date_end": alchemy.datetime_to_timestamp(self.date_end) * 1000,
        }
        return obj

    def to_dict_reseption(self):
        obj = {
            "id": self.id,
            "date_start": alchemy.datetime_to_timestamp(self.date_start) * 1000,
            "date_end": alchemy.datetime_to_timestamp(self.date_end) * 1000,
        }
        return obj

    def __repr__(self):
        return '<Schedule {}>'.format(self.doctor_id)

    FIELDS = {
        'id': int,
        'date_start': alchemy.datetime_to_timestamp,
        'date_end': alchemy.datetime_to_timestamp,
        'creator_id': int,
        'doctor_id': int,
    }

    FIELDS.update(Base.FIELDS)




#

