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
from app.model import Role, ModulePermission, Module
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
    }
}


def validate_role_create(req, res, resource, params):
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


# Получить список прав для модуля
def module_permissions(session, module_id):
    query_permissions = session.query(ModulePermission) \
        .filter(ModulePermission.module_id == module_id).all()

    # Создаем пустой список, для формирования удобного формата
    permissions = []
    for d in sorted(query_permissions, key=lambda perm: perm.module_id):
        permissions.append({
            'name': d.name,
            'id': d.id,
            'method': d.method
        })

    return permissions


# Группировка модулей, для представления в настройках ролей.
def view_permissions_list(session):
    # Выбрать теги с категориями
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
        tmp_dict_methods = []
        for i in map(parent_drop, children):
            tmp_dict_methods.append({
                'label': i['label'],
                'id': i['id'],
                'children': module_permissions(session, i['id'])
            })
        temp['children'] = tmp_dict_methods
        result.append(temp)

    return result


# Работа с коллекцией ролей
class RoleCollection(BaseResource):
    """
    Точка входа: /v1/settings/roles
    Добавить новую роль
    """

    @falcon.before(auth_required)
    @falcon.before(validate_role_create)
    def on_post(self, req, res):
        session = req.context['session']
        role_req = req.media
        if role_req:
            role = Role()
            role.name = role_req['name']
            role.description = role_req['description']
            session.add(role)
            session.commit()
            self.on_success(res, str(role.id))
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        role_dbs = session.query(Role).all()
        if role_dbs:
            obj = [role.to_dict() for role in role_dbs]
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с определенной ролью пользователя
class RoleItem(BaseResource):
    """
    Точка входа: /v1/settings/role/{role_id}
    Вывод информации о роли, редактирование роли, удаление роли
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, role_id):
        session = req.context['session']
        try:
            role = session.query(Role).filter(Role.id == role_id).first()
            obj = role.to_dict()
            temp_select = []
            for d in role.permissions:
                temp_select.append(d.id)
            obj['permission_checked'] = temp_select
            obj['permission_items'] = view_permissions_list(session)
            self.on_success(res, obj)
        except NoResultFound:
            raise DataNotFount('Роль с идентификатором: %s не найдена' % role_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, role_id):
        session = req.context['session']
        role_req = req.media
        if role_req:
            try:
                role = Role.find_one(session, role_id)
                role.name = role_req['name']
                role.role_description = role_req['description']
                role.permissions.clear()
                for id in role_req['permission_checked']:
                    permission= ModulePermission.find_one(session, id)
                    if permission is not None:
                        # Add an association
                        role.permissions.append(permission)
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise InvalidParameterError(req.media)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, role_id):
        session = req.context['session']
        try:
            session.query(Role).filter(Role.id == role_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
