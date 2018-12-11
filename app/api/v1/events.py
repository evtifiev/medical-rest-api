# -*- coding: utf-8 -*-
import falcon
import itertools
import operator

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model import Menu, Module
from app.errors import InvalidParameterError, DataNotFount

LOG = log.get_logger()

FIELDS = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 90
    },
    'description': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 255
    },
    'start': {
        'type': 'datetime',
        'mindatetime': '00:00:00',
        'timezone': "Moscow"
    }
}


# Группировка меню, для представления в настройках разрешений меню.
def view_items_menu(session):
    try:
        menu = session.query(Module).all()

        tmp_dic_children = []  # Список для формирования потомком
        tmp_dict_parent = []  # Список для формирование родителей
        result = []  # Результирующий список
        for d in menu:
            if bool(d.parent_id):
                tmp_dic_children.append({
                    'parent_id': d.parent_id,
                    'label': d.name,
                    'id': d.id
                })
            else:
                tmp_dict_parent.append({
                    'id': d.id,
                    'label': d.name
                })

        # Функция для удаления идентификатора родителя в наследниках
        def parent_drop(d):
            del d['parent_id']
            return d

        # Формируем результат для вывода группировки по родителю
        for parent, children in itertools.groupby(sorted(tmp_dic_children, key=operator.itemgetter('parent_id')),
                                                  operator.itemgetter('parent_id')):
            temp = next(item for item in tmp_dict_parent if item["id"] == parent)
            temp['children'] = [i for i in map(parent_drop, children)]
            result.append(temp)
    except DataNotFount:
        result = []

    return result


# Валидация и проверка при создании меню
def validate_menu_create(req, res, resource, params):
    schema = {
        'name': FIELDS['name'],
        'description': FIELDS['description'],
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Неверный запрос %s' % req.media)


# Работа с коллекцией menu
class MenuCollection(BaseResource):
    """
    Точка входа: /v1/settings/menus
    Добавить новое меню
    """

    @falcon.before(auth_required)
    @falcon.before(validate_menu_create)
    def on_post(self, req, res):
        session = req.context['session']
        menu_req = req.media
        if menu_req:
            menu = Menu()
            menu.name = menu_req['name']
            menu.description = menu_req['description']
            session.add(menu)
            session.commit()
            self.on_success(res, str(menu.id))
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        menu_dbs = session.query(Menu).all()
        if menu_dbs:
            obj = [menu.to_dict() for menu in menu_dbs]
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с определенной набором меню
class MenuItem(BaseResource):
    """
    Точка входа: /v1/settings/menu/{menu_id}
    Вывод информации о меню, редактирование меню, удаление меню
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, menu_id):
        session = req.context['session']
        try:
            menu = session.query(Menu).filter(Menu.id == menu_id).first()
            obj = menu.to_dict()
            temp_select = []
            for d in menu.modules:
                temp_select.append(d.id)
            obj['menu_checked'] = temp_select
            obj['menu_items'] = view_items_menu(session)
            self.on_success(res, obj)
        except NoResultFound:
            raise DataNotFount('Меню с идентификатором: %s не найдено' % menu_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, menu_id):
        session = req.context['session']
        menu_req = req.media
        if menu_req:
            try:
                menu = Menu.find_one(session, menu_id)
                menu.name = menu_req['name']
                menu.description = menu_req['description']
                menu.modules.clear()
                for id in menu_req['menu_checked']:
                    module = Module.find_one(session, id)
                    if module is not None:
                        # Add an association
                        menu.modules.append(module)
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise InvalidParameterError(req.media)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, menu_id):
        session = req.context['session']
        try:
            session.query(Menu).filter(Menu.id == menu_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
