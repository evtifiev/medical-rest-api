# -*- coding: utf-8 -*-

from sqlalchemy import Column, Table
from sqlalchemy import String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from app.model import Base

role_has_permission_table = Table('role_has_module_permission', Base.metadata,
                                  Column('role_id', Integer, ForeignKey('role.id', ondelete='CASCADE')),
                                  Column('module_permission_id', Integer, ForeignKey('module_permission.id',
                                                                                     ondelete='CASCADE'))
                                  )

menu_has_module_table = Table('menu_has_module', Base.metadata,
                              Column('menu_id', Integer, ForeignKey('menu.id', ondelete='CASCADE')),
                              Column('module_id', Integer, ForeignKey('module.id', ondelete='CASCADE'))
                              )


# Группы разрешений, указывают на модули
class Module(Base):
    __tablename__ = 'module'
    id = Column(Integer, primary_key=True)
    name = Column(String(90), nullable=False)
    parent_id = Column(Integer, ForeignKey('module.id'))
    url = Column(String(90), nullable=False)

    permission = relationship("ModulePermission")

    def __repr__(self):
        return "<Module (name='%s', url='%s', parent_id='%s')>" % \
               (self.name, self.url, self.parent_id)

    @classmethod
    def get_id(cls):
        return Module.id

    FIELDS = {
        'id': int,
        'name': str,
        'url': str,
        'parent_id': int
    }

    FIELDS.update(Base.FIELDS)


class ModulePermission(Base):
    __tablename__ = 'module_permission'
    id = Column(Integer, primary_key=True)
    module_id = Column(Integer, ForeignKey('module.id'))
    name = Column(String(90), nullable=False)
    url = Column(String(90), nullable=False)
    method = Column(String(10), nullable=False)

    def __repr__(self):
        return "<ModulePermission(name='%s')>" % \
               self.name

    @classmethod
    def get_id(cls):
        return ModulePermission.id

    FIELDS = {
        'id': int,
        'module_id': int,
        'name': str,
        'method': str,
        'url': str,
        'value': str
    }

    FIELDS.update(Base.FIELDS)