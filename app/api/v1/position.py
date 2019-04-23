# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model.position import Position
from app.errors import AppError, InvalidParameterError, UserNotExistsError
LOG = log.get_logger()

FIELDS_POSITION = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 300
    }
}


def validate_position_create(req, res, resource, params):
    schema = {
        'name': FIELDS_POSITION['name']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией должности компании
class PositionCollection(BaseResource):
    """
    Handle for endpoint: /v1/positions/
    """

    @falcon.before(validate_position_create)
    def on_post(self, req, res):
        session = req.context['session']
        position_req = req.media
        if position_req:
            name = position_req['name']
            position = Position(name=name)
            session.add(position)
            session.commit()
            data = {
                "id": position.id
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        position_dbs = session.query(Position).all()
        if position_dbs:
            obj = {
                "items": [position.to_dict() for position in position_dbs]
            }
            self.on_success(res, obj)
        else:
            raise AppError()


# Работа с должностью
class PositionItem(BaseResource):
    """
    Handle for endpoint: /v1/position/{position_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, position_id):
        session = req.context['session']
        try:
            position_db = Position.find_one(session, position_id)
            self.on_success(res, position_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('position_id: %s' % position_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, position_id):
        session = req.context['session']
        position_req = req.media
        if position_req:
            try:
                session.query(Position).filter(Position.id == position_id). \
                    update({'name': position_req['name']})
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, position_id):
        session = req.context['session']
        try:
            session.query(Position).filter(Position.id == position_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
