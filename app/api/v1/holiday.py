# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model.holiday import Holiday
from app.errors import AppError, InvalidParameterError, UserNotExistsError, DataNotFount
from datetime import datetime

LOG = log.get_logger()

FIELDS_HOLIDAY = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 90
    },
    'date': {
        'type': 'string',
        'required': True,
    }
}


def validate_department_create(req, res, resource, params):
    schema = {
        'name': FIELDS_HOLIDAY['name'],
        'date': FIELDS_HOLIDAY['date']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией праздничные дни
class HolidayCollection(BaseResource):
    """
    Handle for endpoint: /v1/holidays/
    """

    @falcon.before(validate_department_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        holiday_req = req.media
        if holiday_req:
            name = holiday_req['name']
            date = datetime.strptime(holiday_req['date'], "%d.%m.%Y")
            holiday = Holiday(date=date, name=name)
            session.add(holiday)
            session.commit()
            data = {
                "id": str(holiday.id)
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        holiday_dbs = session.query(Holiday).all()
        if holiday_dbs:
            obj = {
                "items": [holiday.to_dict() for holiday in holiday_dbs]
            }
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с подразделением
class HolidayItem(BaseResource):
    """
    Handle for endpoint: /v1/holiday/{holiday_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, holiday_id):
        session = req.context['session']
        try:
            department_db = Holiday.find_one(session, holiday_id)
            self.on_success(res, department_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('holiday_id: %s' % holiday_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, holiday_id):
        session = req.context['session']
        holiday_req = req.media
        if holiday_req:
            try:
                session.query(Holiday).filter(Holiday.id == holiday_id). \
                    update({'name': holiday_req['name'], 'date': datetime.strptime(holiday_req['date'], "%d-%m-%Y")})
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, holiday_id):
        session = req.context['session']
        try:
            session.query(Holiday).filter(Holiday.id == holiday_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
