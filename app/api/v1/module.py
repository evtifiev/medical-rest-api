# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model import ModulePermission, Module
from app.errors import DataNotFount, InvalidParameterError

LOG = log.get_logger()

MODULE_FIELDS = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 60
    },
    'parent_id': {
        'type': 'integer',
        'required': False
    },
    'url': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 90
    }
}

MODULE_PERMISSION_FIELDS = {
    'module_id': {
        'type': 'integer',
        'required': True
    },
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 90
    },
    'url': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 90
    },
    'method': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 10
    },
    'value': {
        'type': 'string',
        'required': False
    }
}


def validate_module_create(req, res, resource, params):
    schema = {
        'parent_id': MODULE_FIELDS['parent_id'],
        'name': MODULE_FIELDS['name'],
        'url': MODULE_FIELDS['url']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Неверный запрос %s' % req.media)


def validate_module_permission_create(req, res, resource, params):
    schema = {
        'module_id': MODULE_PERMISSION_FIELDS['module_id'],
        'name': MODULE_PERMISSION_FIELDS['name'],
        'url': MODULE_PERMISSION_FIELDS['url'],
        'method': MODULE_PERMISSION_FIELDS['method'],
        'value': MODULE_PERMISSION_FIELDS['value'],
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Неверный запрос %s' % req.media)


class ModuleCollection(BaseResource):
    """
    Точка входа: /v1/settings/modules
    Добавление нового модуля
    """

    @falcon.before(auth_required)
    @falcon.before(validate_module_create)
    def on_post(self, req, res):
        session = req.context['session']
        module_req = req.media
        if module_req:
            module = Module()
            module.name = module_req['name']
            module.url = module_req['url']
            module.parent_id = module_req['parent_id'] if 'parent_id' in module_req else None
            session.add(module)
            session.commit()
            self.on_success(res, str(module.id))
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        module_dbs = session.query(Module).all()
        if module_dbs:
            obj = [module.to_dict() for module in module_dbs]
            self.on_success(res, obj)
        else:
            raise DataNotFount("Модуль не найдены")


# Работа с определенной модулем
class ModuleItem(BaseResource):
    """
    Точка входа: /v1/settings/module/{module_id}
    Вывод информации о модуле, редактирование группы, удаление группы
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, module_id):
        session = req.context['session']
        try:
            module = session.query(Module).filter(Module.id == module_id).first()
            self.on_success(res, module.to_dict())
        except NoResultFound:
            raise DataNotFount('Модуль с идентификатором: %s не найдена' % module_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, module_id):
        session = req.context['session']
        module_req = req.media
        if module_req:
            try:
                session.query(Module).filter(Module.id == module_id). \
                    update({
                        'parent_id': module_req['parent_id'] if 'parent_id' in module_req else None,
                        'name': module_req['name'],
                        'url': module_req['url'],
                })
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise InvalidParameterError(req.media)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, module_id):
        session = req.context['session']
        try:
            session.query(Module).filter(Module.id == module_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)


class ModulePermissionCollection(BaseResource):
    """
    Точка входа: /v1/settings/module/permissions
    Добавление политик к определенному модулю
    """

    @falcon.before(auth_required)
    @falcon.before(validate_module_permission_create)
    def on_post(self, req, res):
        session = req.context['session']
        module_permission_req = req.media
        if module_permission_req:
            module_permission = ModulePermission()
            module_permission.module_id = module_permission_req['module_id']
            module_permission.name = module_permission_req['name']
            module_permission.url = module_permission_req['url']
            module_permission.method = module_permission_req['method']
            module_permission.value = module_permission_req['value']
            session.add(module_permission)
            session.commit()
            self.on_success(res, module_permission.id)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        module_permission_dbs = session.query(ModulePermission).all()
        if module_permission_dbs:
            obj = [module_permission.to_dict() for module_permission in module_permission_dbs]
            self.on_success(res, obj)
        else:
            raise DataNotFount("Политики не найдены")


# Работа с определенной политикой модуля
class ModulePermissionItem(BaseResource):
    """
    Точка входа: /v1/settings/module/permissions/{permission_id}
    Вывод информации о политике, редактирование политики, удаление политики
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, permission_id):
        session = req.context['session']
        try:
            module_permission = session.query(ModulePermission).filter(ModulePermission.id == permission_id).first()
            self.on_success(res, module_permission.to_dict())
        except NoResultFound:
            raise DataNotFount('Политика с идентификатором: %s не найдена' % permission_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, permission_id):
        session = req.context['session']
        permission_req = req.media
        if permission_req:
            try:
                session.query(ModulePermission).filter(ModulePermission.id == permission_id). \
                    update({
                     'module_id': permission_req['module_id'],
                     'name': permission_req['name'],
                     'url': permission_req['url'],
                     'method': permission_req['method'],
                     'value': permission_req['value'],
                })
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise InvalidParameterError(req.media)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, permission_id):
        session = req.context['session']
        try:
            session.query(ModulePermission).filter(ModulePermission.id == permission_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
