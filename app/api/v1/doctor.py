# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model.doctor import DoctorSpecialization, Doctor
from app.errors import AppError, InvalidParameterError, UserNotExistsError, DataNotFount

LOG = log.get_logger()
FIELDS_DOCTOR_SPECIALIZATION = {
    'name': {
        'type': 'string',
        'required': True,
        'minlength': 3,
        'maxlength': 120
    }
}
FIELDS_DOCTOR = {
    'user_id': {
        'type': 'integer',
        'required': True
    },
    'doctor_specialization_id': {
        'type': 'integer',
        'required': True
    }
}


def validate_doctor_specialization_create(req, res, resource, params):
    schema = {
        'name': FIELDS_DOCTOR_SPECIALIZATION['name']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


def validate_doctor_create(req, res, resource, params):
    schema = {
        'user_id': FIELDS_DOCTOR['user_id'],
        'doctor_specialization_id': FIELDS_DOCTOR['user_id']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией специализации врачей
class DoctorSpecializationCollection(BaseResource):
    """
    Handle for endpoint: /v1/specializations
    """

    @falcon.before(validate_doctor_specialization_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        doctor_specialization = req.media
        if doctor_specialization:
            name = doctor_specialization['name']
            specialization = DoctorSpecialization(name=name)
            session.add(specialization)
            session.commit()
            data = {
                "id": str(specialization.id)
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        doctor_specialization_dbs = session.query(DoctorSpecialization).all()
        if doctor_specialization_dbs:
            obj = {
                "items": [doctor_specialization.to_dict() for doctor_specialization in doctor_specialization_dbs]
            }
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с специализацией доктора
class DoctorSpecializationItem(BaseResource):
    """
    Handle for endpoint: /v1/specialization/{doctor_specialization_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, doctor_specialization_id):
        session = req.context['session']
        try:
            doctor_specialization_db = DoctorSpecialization.find_one(session, doctor_specialization_id)
            self.on_success(res, doctor_specialization_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('doctor_specialization_id: %s' % doctor_specialization_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, doctor_specialization_id):
        session = req.context['session']
        doctor_specialization_req = req.media
        if doctor_specialization_req:
            try:
                session.query(DoctorSpecialization).filter(DoctorSpecialization.id == doctor_specialization_id). \
                    update({'name': doctor_specialization_req['name']})
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, doctor_specialization_id):
        session = req.context['session']
        try:
            session.query(DoctorSpecialization).filter(DoctorSpecialization.id == doctor_specialization_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)


# Работа с коллекцией доктор
class DoctorCollection(BaseResource):
    """
    Handle for endpoint: /v1/doctors/
    """

    @falcon.before(validate_doctor_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        doctor_req = req.media
        if doctor_req:
            user_id = doctor_req['user_id']
            doctor_specialization_id = doctor_req['doctor_specialization_id']
            creator = req.context['user']
            doctor = Doctor(user_id=user_id, doctor_specialization_id=doctor_specialization_id, creator_id=creator)
            session.add(doctor)
            session.commit()
            data = {
                "id": str(doctor.id)
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        doctor_dbs = session.query(Doctor).all()
        if doctor_dbs:
            obj = {
                "items": [doctor.to_dict() for doctor in doctor_dbs]
            }
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с достором
class DoctorItem(BaseResource):
    """
    Handle for endpoint: /v1/doctor/{doctor_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, doctor_id):
        session = req.context['session']
        try:
            doctor_db = Doctor.find_one(session, doctor_id)
            self.on_success(res, doctor_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('doctor_id: %s' % doctor_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, doctor_id):
        session = req.context['session']
        doctor_req = req.media
        if doctor_req:
            try:
                session.query(Doctor).filter(Doctor.id == doctor_id). \
                    update({
                    'user_id': doctor_req['user_id'],
                    'doctor_specialization_id': doctor_req['doctor_specialization_id'],
                    'creator_id': req.context['user']
                })
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, doctor_id):
        session = req.context['session']
        try:
            session.query(Doctor).filter(Doctor.id == doctor_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
