# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer

from app.model import Base


# Модель пациенты
class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    last_name = Column(String(90), nullable=True)  # Фамилия
    first_name = Column(String(40), nullable=True)  # Имя
    middle_name = Column(String(70), nullable=True)  # Отчество
    mobile = Column(String(80), nullable=True)  # Контактный номер мобильного телефона

    def __repr__(self):
        return "<Patient(last_name='%s', first_name='%s')>" % \
               (self.last_name, self.first_name)

    @classmethod
    def get_id(cls):
        return Patient.id

    def get_full_name(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.middle_name)

    def get_short_name(self):
        return '%s %s. %s.' % (self.last_name, self.first_name[0], self.middle_name[0])

    FIELDS = {
        'id': int,
        'last_name': str,
        'first_name': str,
        'mobile': str
    }

    FIELDS.update(Base.FIELDS)
