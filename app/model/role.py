# -*- coding: utf-8 -*-
import uuid

from sqlalchemy import Column
from sqlalchemy import String, Boolean, Integer
from sqlalchemy.orm import relationship

from app.model import Base
from app.model.module import role_has_permission_table


# Модель Роли
class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)
    name = Column(String(90), nullable=False)
    description = Column(String(255), nullable=False)
    default = Column(Boolean, default=False)
    visible = Column(Boolean, default=True)
    deleted = Column(Boolean, default=False)

    permissions = relationship("ModulePermission", secondary=role_has_permission_table)
    # Обратная ссылка на пользователя
    user = relationship("User", uselist=False, back_populates="role")

    def __repr__(self):
        return "<Role(role_name='%s', level='%s', role_description='%s', default='%s', visible='%s', deleted='%s')>" % \
               (self.name, self.description, self.default, self.visible, self.deleted)

    @classmethod
    def get_id(cls):
        return Role.id

    FIELDS = {
        'id': int,
        'name': str,
        'description': str,
        'default': bool,
        'visible': bool,
        'deleted': bool
    }

    FIELDS.update(Base.FIELDS)