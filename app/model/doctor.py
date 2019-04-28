# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.utils import alchemy

from app.model import Base


# Модель специализация врачей
class DoctorSpecialization(Base):
    __tablename__ = 'doctor_specialization'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(120), nullable=False)

    def __repr__(self):
        return "<DoctorSpecialization(name='%s')>" % \
               (self.name)

    @classmethod
    def get_id(cls):
        return DoctorSpecialization.id

    FIELDS = {
        'id': int,
        'name': str,
    }

    FIELDS.update(Base.FIELDS)


# Модель список врачей ведущих прием
class Doctor(Base):
    __tablename__ = 'doctor'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    doctor_specialization_id = Column(Integer, ForeignKey('doctor_specialization.id'))
    creator_id = Column(Integer, ForeignKey('user.id'))
    color = Column(String(30), nullable=True)

    user = relationship("User", backref='doctor', primaryjoin="Doctor.user_id==User.id")
    creator = relationship("User", backref='creator', primaryjoin="Doctor.creator_id==User.id")
    specialization = relationship("DoctorSpecialization", foreign_keys=[doctor_specialization_id])

    def __repr__(self):
        return "<Doctor(user_id='%s', doctor_pecialization_id='%s', creator_id='%s')>" % \
               (self.user_id, self.doctor_specialization_id, self.creator_id)

    @classmethod
    def get_id(cls):
        return Doctor.id

    def get_full_name(self):
        return '%s' % self.user.full_name

    def get_short_name(self):
        return '%s' % self.user.short_name

    def to_dict(self):
        obj = {
            "id": self.id,
            "specialization": self.specialization.name,
            "doctor": self.user.full_name,
            "doctorShortName": self.user.short_name,
            "creator": self.creator.short_name,
            "created": alchemy.datetime_to_timestamp(self.created) * 1000,
        }
        return obj

    FIELDS = {
        'id': int,
        'user_id': int,
        'doctor_specialization_id': int,
        'creator': int
    }

    FIELDS.update(Base.FIELDS)
