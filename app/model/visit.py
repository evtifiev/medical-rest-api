# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import Integer, ForeignKey, String
from sqlalchemy_utils import ChoiceType
from sqlalchemy.orm import relationship

from app.model import Base
from enum import Enum


class FinancingType(Enum):
    oms = 1
    dms = 2
    pay = 3


FinancingType.oms.label = 'ОМС'
FinancingType.dms.label = 'ДМС'
FinancingType.pay.label = 'Платный'


class Visit(Base):
    __tablename__ = 'visit'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    creator_id = Column(Integer, ForeignKey('user.id'))  # Кто добавил
    schedule_id = Column(Integer, ForeignKey('schedule.id'))  # Идентификатор расписания
    patient_id = Column(Integer, ForeignKey('patient.id'))  # Идентификатор пациента
    doctor_id = Column(Integer, ForeignKey('doctor.id'))  # Идентификатор доктора
    source_of_financing = Column(ChoiceType(FinancingType, impl=Integer()))  # Источник финансирования
    comment = Column(String(500), nullable=True)  # Комментарий визита внутренний

    schedule = relationship("Schedule")
    doctor = relationship("Doctor")
    patient = relationship("Patient")

    def __repr__(self):
        return "<Visit(id='%d')>" % (self.id)

    def to_dict(self):
        obj = {
            'id': self.id,
            'title': '   ' + str(self.source_of_financing.label) + '     Пациент:  ' + self.patient.get_full_name() + '   Тел: ' + self.patient.mobile + ' Врач: ' + self.doctor.get_short_name(),
            'start': f'{self.schedule.date_start:%Y-%m-%d %H:%M}',
            'end': f'{self.schedule.date_end:%Y-%m-%d %H:%M}',
            'backgroundColor': self.doctor.color,
            'borderColor': self.doctor.color,
        }
        return obj

    FIELDS = {
        'id': int,
        'creator_id': int,
        'schedule_id': int,
        'patient_id': int,
        'doctor_id': int
    }

    FIELDS.update(Base.FIELDS)
