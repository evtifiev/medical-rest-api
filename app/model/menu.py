# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, Integer
from sqlalchemy.orm import relationship

from app.model import Base
from app.model.module import menu_has_module_table


# Модель меню пользователей
class Menu(Base):
    __tablename__ = 'menu'
    id = Column(Integer, primary_key=True)
    name = Column(String(90), nullable=False)
    description = Column(String(255), nullable=False)

    # Обратная ссылка на наименование модуля
    modules = relationship("Module", secondary=menu_has_module_table)
    # Обратная ссылка на пользователя
    user = relationship("User", uselist=False, back_populates="menu")

    def __repr__(self):
        return "<Menu(name='%s', description='%s')>" % \
               (self.name, self.description)

    @classmethod
    def get_id(cls):
        return Menu.id

    FIELDS = {
        'id': int,
        'name': str,
        'description': str
    }

    FIELDS.update(Base.FIELDS)
