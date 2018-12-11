# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from app.model import Base
from app.config import UUID_LEN
from app.utils import alchemy


# Модель пользователя, сотрудника
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор пользователя
    username = Column(String(60), nullable=False, unique=True)  # Имя пользователя, для входа
    password = Column(String(80), nullable=False)  # Пароль
    last_name = Column(String(90), nullable=True)  # Фамилия
    first_name = Column(String(40), nullable=True)  # Имя
    middle_name = Column(String(40), nullable=True)  # Отчество
    email = Column(String(90), unique=True, nullable=False)  # Контактный email
    email_password = Column(String(120), nullable=True)  # Пароль электронной почты
    mobile = Column(String(80), nullable=True)  # Контактный номер мобильного телефона
    phone = Column(String(120), nullable=True)  # Служебный номер
    info = Column(JSONB, nullable=True)  # Дополнительная информация

    blocked = Column(Boolean, default=False)  # Текущий статус пользователя
    numeric_id = Column(String(UUID_LEN), nullable=False)
    token = Column(String(255), nullable=False)  # Секретный токен

    # Ссылка на роль
    role_id = Column(Integer, ForeignKey('role.id'), nullable=True)
    role = relationship("Role", back_populates="user")
    # Ссылка на меню
    menu_id = Column(Integer, ForeignKey('menu.id'), nullable=True)
    menu = relationship("Menu", back_populates="user")

    # Ссылка на подразделение
    department_id = Column(Integer, ForeignKey('department.id'), nullable=True)
    department = relationship("Department", back_populates="user")

    # Ссылка на должность
    position_id = Column(Integer, ForeignKey('position.id'), nullable=True)
    position = relationship("Position", back_populates="user")

    def __repr__(self):
        return "<User(name='%s', email='%s', token='%s', info='%s')>" % \
               (self.username, self.email, self.token, self.info)

    @classmethod
    def get_id(cls):
        return User.id

    @classmethod
    def find_by_email(cls, session, email):
        return session.query(User).filter(User.email == email).one()

    @classmethod
    def find_by_username(cls, session, username):
        return session.query(User).filter(User.username == username).one()

    @classmethod
    def find_by_numeric_id(cls, session, numeric_id):
        return session.query(cls).filter(cls.numeric_id == numeric_id).one()

    def to_dict_one(self):
        user = {
            "username": self.username,
            "last_name": self.last_name,
            "first_name": self.first_name,
            "middle_name": self.middle_name,
            "email": self.email,
            "created": alchemy.datetime_to_timestamp(self.created) * 1000,
            "modified": alchemy.datetime_to_timestamp(self.modified) * 1000,
            "info": self.info,
        }
        return user

    @staticmethod
    def view_menu(menus):
        list_menu = []
        for menu in menus:
            list_menu.append(
                {
                    "id": str(menu.id),
                    "name": menu.name,
                    "parent_id": str(menu.parent_id) if bool(menu.parent_id) else "null",
                    "route": menu.url,
                    "summary": "null"
                }
            )
        return list_menu

    @staticmethod
    def view_resources(permissions):
        list_resources = []
        for permission in permissions:
            list_resources.append(
                {
                    "id": str(permission.id),
                    "name": permission.name,
                    "url": permission.url,
                    "method": permission.method,
                    "summary": "null"
                }
            )
        return list_resources

    @staticmethod
    def view_permissions(permissions):
        list_permissions = []
        for permission in permissions:
            if permission.value is not None:
                list_permissions.append(permission.value)
        return list_permissions

    # Вывод информации при авторизации пользователя
    def auth_info(self):
        user = {
            "id": self.id,
            "name": str(self.last_name) + " " + str(self.first_name) + " ",
            "email": self.email,
            #"menus": self.view_menu(self.menu.modules),
            #"resources": self.view_resources(self.role.permissions),
            "resources": [
                {
                    "id": "2c9180895e172348015e1740805d000d",
                    "name": "账号-获取",
                    "summary": '',
                    "url": "/accounts",
                    "method": "GET"
                },
                {
                    "id": "2c9180895e172348015e1740c30f000e",
                    "name": "账号-删除",
                    "summary": '',
                    "url": "/account/**",
                    "method": "DELETE"
                },
                {
                    "id": "2c9180895e172348015e1741148a000f",
                    "name": "账号-修改",
                    "summary": '',
                    "url": "/account/**",
                    "method": "PUT"
                },
                {
                    "id": "2c9180895e172348015e1840b98f0013",
                    "name": "账号-分配角色",
                    "summary": '',
                    "url": "/account/*/roles",
                    "method": "POST"
                },
                {
                    "id": "2c9180895e172348015e173cd55f0009",
                    "name": "角色-获取",
                    "summary": '',
                    "url": "/roles",
                    "method": "GET"
                },
                {
                    "id": "2c9180895e172348015e173e83ac000a",
                    "name": "角色-删除",
                    "summary": '',
                    "url": "/role/**",
                    "method": "DELETE"
                },
                {
                    "id": "2c9180895e172348015e173eb9a4000b",
                    "name": "角色-修改",
                    "summary": '',
                    "url": "/role/**",
                    "method": "PUT"
                },
                {
                    "id": "2c9180895e172348015e173f2fcc000c",
                    "name": "角色-添加",
                    "summary": '',
                    "url": "/role",
                    "method": "POST"
                },
                {
                    "id": "4028811a5e1820d9015e1824acf20000",
                    "name": "登录",
                    "summary": '',
                    "url": "/signin",
                    "method": "GET"
                },
                {
                    "id": "4028811a5e1820d9015e1824acf20000",
                    "name": "登录",
                    "summary": '',
                    "url": "/signin",
                    "method": "GET"
                },
                {
                    "id": "4028811a5e1820d9015dsds824acf20000",
                    "name": "Авторизация",
                    "summary": '',
                    "url": "/auth/**",
                    "method": "GET"
                }
            ],
            "menus": [
                {
                    "id": "1",
                    "name": "Настройки",
                    "parent_id": '',
                    "route": "settings",
                    "summary": ''
                },
                {
                    "id": "2",
                    "name": "Роли",
                    "parent_id": '1',
                    "route": "roles",
                    "summary": ''
                },
                {
                    "id": "3",
                    "name": "Пользователи",
                    "parent_id": '1',
                    "route": "accounts",
                    "summary": ''
                },
                {
                    "id": "4",
                    "name": "Меню",
                    "parent_id": '1',
                    "route": "menu",
                    "summary": ''
                },
                {
                    "id": "5",
                    "name": "Подразделения",
                    "parent_id": '1',
                    "route": "departments",
                    "summary": ''
                },
                {
                    "id": "6",
                    "name": "Должности",
                    "parent_id": '1',
                    "route": "positions",
                    "summary": ''
                },
                {
                    "id": "8",
                    "name": "Расписание",
                    "parent_id": '',
                    "route": "schedule",
                    "summary": ''
                },
                {
                    "id": "9",
                    "name": "Заявки",
                    "parent_id": '',
                    "route": "applications",
                    "summary": ''
                },
                {
                    "id": "10",
                    "name": "Телефонный справочник",
                    "parent_id": '',
                    "route": "telephony",
                    "summary": ''
                },

            ]
            #"company": self.staffs[0].company.to_dict() if bool(self.staffs) else '',
            #"person": self.staffs[0].to_dict() if bool(self.staffs) else ''
        }
        return user

    # Вывод информации при авторизации пользователя
    def auth_permission(self):
        user = {
            "id": self.id,
            "permissions": self.view_permissions(self.role.permissions)
        }
        return user

    def get_token(self):
        data = {"token": self.token}
        return data

    def to_dict_all(self):
        user = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'token': self.token,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'phone': self.phone,
            'role_id': self.role_id,
            'menu_id': self.menu_id,
            'status': str(self.status.code),
            'company_id': self.staffs[0].company_id if bool(self.staffs) else '',
            'company_person_id': self.staffs[0].id if bool(self.staffs) else '',
        }
        return user

    FIELDS = {
        'id': str,
        'username': str,
        'email': str,
        'info': alchemy.passby,
        'token': str,
        'last_name': str,
        'first_name': str,
        'middle_name': str,
        'phone': str,
        'role_id': int,
        'menu_id': int
    }

    FIELDS.update(Base.FIELDS)