# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model.department import Department
from app.errors import AppError, InvalidParameterError, UserNotExistsError

LOG = log.get_logger()

FIELDS_DEPARTMENT = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 255
    }
}


def validate_department_create(req, res, resource, params):
    schema = {
        'name': FIELDS_DEPARTMENT['name']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией подразделения
class DepartmentCollection(BaseResource):
    """
    Handle for endpoint: /v1/departments/
    """

    @falcon.before(validate_department_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        department_req = req.media
        if department_req:
            name = department_req['name']
            department = Department(name=name)
            session.add(department)
            session.commit()
            data = {
                "id": str(department.id)
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        department_dbs = session.query(Department).all()
        if department_dbs:
            obj = {
                "items": [department.to_dict() for department in department_dbs]
            }
            self.on_success(res, obj)
        else:
            raise AppError()


# Работа с подразделением
class DepartmentItem(BaseResource):
    """
    Handle for endpoint: /v1/departments/{department_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, department_id):
        session = req.context['session']
        try:
            department_db = Department.find_one(session, department_id)
            self.on_success(res, department_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('department_id: %s' % department_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, department_id):
        session = req.context['session']
        department_req = req.media
        if department_req:
            try:
                session.query(Department).filter(Department.id == department_id). \
                    update({'name': department_req['name']})
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, department_id):
        session = req.context['session']
        try:
            session.query(Department).filter(Department.id == department_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
