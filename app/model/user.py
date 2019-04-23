# -*- coding: utf-8 -*-

from sqlalchemy import Column
from sqlalchemy import String, ForeignKey, Integer, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

from app.model import Base
from app.config import UUID_LEN
from app.utils import alchemy


# Модель пользователя, сотрудника
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, unique=True, nullable=False, primary_key=True)  # Уникальный идентификатор пользователя
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

    def get_full_name(self):
        return '%s %s %s' % (self.last_name, self.first_name, self.middle_name)

    def get_short_name(self):
        return '%s %s. %s.' % (self.last_name, self.first_name[0], self.middle_name[0])

    @property
    def full_name(self):
        return self.get_full_name()

    @property
    def short_name(self):
        return self.get_short_name()

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
                    "id": menu.id,
                    "name": menu.name,
                    "parent_id": menu.parent_id if bool(menu.parent_id) else "null",
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
                    "id": permission.id,
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
            "id": str(self.id),
            "name": str(self.last_name) + " " + str(self.first_name) + " ",
            "email": self.email,
            "position": self.position.name,
            "menus": self.view_menu(self.menu.modules),
            "resources": self.view_resources(self.role.permissions),
            # "resources": [
            #     {
            #         "id": "1",
            #         "name": "账号-获取",
            #         "summary": '',
            #         "url": "/accounts",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "2",
            #         "name": "账号-删除",
            #         "summary": '',
            #         "url": "/account/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "3",
            #         "name": "账号-修改",
            #         "summary": '',
            #         "url": "/account/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "4",
            #         "name": "账号-分配角色",
            #         "summary": '',
            #         "url": "/account/*/roles",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "5",
            #         "name": "角色-获取",
            #         "summary": '',
            #         "url": "/roles",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "6",
            #         "name": "角色-删除",
            #         "summary": '',
            #         "url": "/role/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "7",
            #         "name": "角色-修改",
            #         "summary": '',
            #         "url": "/role/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "8",
            #         "name": "角色-添加",
            #         "summary": '',
            #         "url": "/role",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "9",
            #         "name": "登录",
            #         "summary": '',
            #         "url": "/signin",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "10",
            #         "name": "登录",
            #         "summary": '',
            #         "url": "/signin",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "11",
            #         "name": "Авторизация",
            #         "summary": '',
            #         "url": "/auth/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "12",
            #         "name": "Модули",
            #         "summary": '',
            #         "url": "/modules",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "13",
            #         "name": "Модули добавление",
            #         "summary": '',
            #         "url": "/modules",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "14",
            #         "name": "Модули просмотр",
            #         "summary": '',
            #         "url": "/module/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "15",
            #         "name": "Модули редактирование",
            #         "summary": '',
            #         "url": "/module/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "16",
            #         "name": "Модули удаление",
            #         "summary": '',
            #         "url": "/module/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "17",
            #         "name": "Модули разрешения",
            #         "summary": '',
            #         "url": "/permissions",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "18",
            #         "name": "Модули разрешение добавление 5",
            #         "summary": '',
            #         "url": "/permissions",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "19",
            #         "name": "Модули разрешение просмотр",
            #         "summary": '',
            #         "url": "/permission/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "20",
            #         "name": "Модули разрешение редактирование",
            #         "summary": '',
            #         "url": "/permission/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "21",
            #         "name": "Модули разрешение удаление",
            #         "summary": '',
            #         "url": "/permission/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "22",
            #         "name": "Список подразделений",
            #         "summary": '',
            #         "url": "/departments",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "23",
            #         "name": "Список подразделений добавить",
            #         "summary": '',
            #         "url": "/departments",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "24",
            #         "name": "Просмотр информации о подразделении",
            #         "summary": '',
            #         "url": "/department/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "25",
            #         "name": "Редактирование подразделения",
            #         "summary": '',
            #         "url": "/department/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "26",
            #         "name": "Удаление подразделения",
            #         "summary": '',
            #         "url": "/department/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "27",
            #         "name": "Список должностей",
            #         "summary": '',
            #         "url": "/positions",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "28",
            #         "name": "Список должностей добавить",
            #         "summary": '',
            #         "url": "/positions",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "29",
            #         "name": "Просмотр информации о должности",
            #         "summary": '',
            #         "url": "/position/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "30",
            #         "name": "Редактирование должности",
            #         "summary": '',
            #         "url": "/position/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "31",
            #         "name": "Удаление должности",
            #         "summary": '',
            #         "url": "/position/**",
            #         "method": "DELETE"
            #     },
            #     # sdfaa
            #     {
            #         "id": "32",
            #         "name": "Список меню",
            #         "summary": '',
            #         "url": "/menus",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "33",
            #         "name": "Добавить меню",
            #         "summary": '',
            #         "url": "/menus",
            #         "method": "POST"
            #     },
            #     {
            #         "id": "34",
            #         "name": "Просмотр информации о меню",
            #         "summary": '',
            #         "url": "/menu/**",
            #         "method": "GET"
            #     },
            #     {
            #         "id": "35",
            #         "name": "Редактирование меню",
            #         "summary": '',
            #         "url": "/menu/**",
            #         "method": "PUT"
            #     },
            #     {
            #         "id": "36",
            #         "name": "Удаление menu",
            #         "summary": '',
            #         "url": "/menu/**",
            #         "method": "DELETE"
            #     },
            #     {
            #         "id": "34",
            #         "name": "Просмотр информации о роли",
            #         "summary": '',
            #         "url": "/role/**",
            #         "method": "GET"
            #     },
            #
            # ],
            # "menus": [
            #     {
            #         "id": "1",
            #         "name": "Настройки",
            #         "parent_id": '',
            #         "route": "settings",
            #         "summary": ''
            #     },
            #     {
            #         "id": "2",
            #         "name": "Роли",
            #         "parent_id": '1',
            #         "route": "roles",
            #         "summary": ''
            #     },
            #     {
            #         "id": "3",
            #         "name": "Пользователи",
            #         "parent_id": '1',
            #         "route": "accounts",
            #         "summary": ''
            #     },
            #     {
            #         "id": "4",
            #         "name": "Меню",
            #         "parent_id": '1',
            #         "route": "menu",
            #         "summary": ''
            #     },
            #     {
            #         "id": "5",
            #         "name": "Подразделения",
            #         "parent_id": '1',
            #         "route": "departments",
            #         "summary": ''
            #     },
            #     {
            #         "id": "6",
            #         "name": "Должности",
            #         "parent_id": '1',
            #         "route": "positions",
            #         "summary": ''
            #     },
            #     {
            #         "id": "8",
            #         "name": "AKO",
            #         "parent_id": '',
            #         "route": "ako",
            #         "summary": ''
            #     },
            #     {
            #         "id": "9",
            #         "name": "Поддержка",
            #         "parent_id": '',
            #         "route": "tickets",
            #         "summary": ''
            #     },
            #     {
            #         "id": "10",
            #         "name": "Телефонный справочник",
            #         "parent_id": '',
            #         "route": "telephony",
            #         "summary": ''
            #     },
            #     {
            #         "id": "11",
            #         "name": "Расписание",
            #         "parent_id": '8',
            #         "route": "schedule",
            #         "summary": ''
            #     },
            #     {
            #         "id": "12",
            #         "name": "Расписание",
            #         "parent_id": '8',
            #         "route": "reception",
            #         "summary": ''
            #     },
            #     {
            #         "id": "13",
            #         "name": "Врачи",
            #         "parent_id": '8',
            #         "route": "doctors",
            #         "summary": ''
            #     },
            #     {
            #         "id": "14",
            #         "name": "Выходные",
            #         "parent_id": '1',
            #         "route": "holidays",
            #         "summary": ''
            #     },
            #     {
            #         "id": "15",
            #         "name": "Список модулей",
            #         "parent_id": '1',
            #         "route": "modules",
            #         "summary": ''
            #     },
            #     {
            #         "id": "16",
            #         "name": "Разрешения модулей",
            #         "parent_id": '1',
            #         "route": "permissions",
            #         "summary": ''
            #     }
            #
            # ]
            #"company": self.staffs[0].company.to_dict() if bool(self.staffs) else '',
            #"person": self.staffs[0].to_dict() if bool(self.staffs) else ''
        }
        return user

    # Вывод информации при авторизации пользователя
    def auth_permission(self):
        user = {
            "id": str(self.id),
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
            'email_password': self.email_password,
            "fio": str(self.last_name) + " " + str(self.first_name) + " " + self.middle_name,
            'last_name': self.last_name,
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            "position": self.position.name,
            'phone': self.phone,
            'mobile': self.mobile,
            'role_id': self.role_id,
            'menu_id': self.menu_id,
            'position_id': self.menu_id,
            'department_id': self.menu_id,
        }
        return user

    def dict_users_list(self):
        user = {
            'id': self.id,
            "fio": str(self.last_name) + " " + str(self.first_name) + " " + self.middle_name,
        }
        return user

    FIELDS = {
        'id': int,
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