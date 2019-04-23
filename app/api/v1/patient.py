# -*- coding: utf-8 -*-
import falcon

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.model.patient import Patient
from app.errors import AppError, InvalidParameterError, UserNotExistsError, DataNotFount
from datetime import datetime

LOG = log.get_logger()

FIELDS_PATIENT = {
    'last_name': {
        'type': 'string',
        'required': True,
        'minlength': 2,
        'maxlength': 90
    },
    'first_name': {
        'type': 'string',
        'required': False,
    },
    'mobile': {
        'type': 'string',
        'required': False,
    },
    'source_of_financing': {
        'type': 'integer',
        'required': False,
    },
}


def validate_department_create(req, res, resource, params):
    schema = {
        'last_name': FIELDS_PATIENT['last_name'],
        'first_name': FIELDS_PATIENT['first_name'],
        'mobile': FIELDS_PATIENT['mobile'],
        'source_of_financing': FIELDS_PATIENT['source_of_financing']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией пациенты
class PatientCollection(BaseResource):
    """
    Handle for endpoint: /v1/patients/
    """

    @falcon.before(validate_department_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        patient_req = req.media
        if patient_req:
            last_name = patient_req['last_name']
            first_name = patient_req['first_name']
            mobile = patient_req['first_name']
            source_of_financing = patient_req['source_of_financing']
            patient = Patient(first_name=first_name, last_name=last_name, mobile=mobile, source_of_financing=source_of_financing)
            session.add(patient)
            session.commit()
            data = {
                "id": str(patient.id)
            }
            self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        holiday_dbs = session.query(Patient).all()
        if holiday_dbs:
            obj = {
                "items": [patient.to_dict() for patient in holiday_dbs]
            }
            self.on_success(res, obj)
        else:
            raise DataNotFount()


# Работа с пациентом
class PatientItem(BaseResource):
    """
    Handle for endpoint: /v1/patient/{patient_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, patient_id):
        session = req.context['session']
        try:
            department_db = Patient.find_one(session, patient_id)
            self.on_success(res, department_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('patient_id: %s' % patient_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, patient_id):
        session = req.context['session']
        patient_req = req.media
        if patient_req:
            try:
                session.query(Patient).filter(Patient.id == patient_id). \
                    update({
                    'last_name': patient_req['last_name'],
                    'first_name': patient_req['first_name'],
                    'mobile': patient_req['mobile'],
                    'source_of_financing': patient_req['source_of_financing'],
                })
                session.commit()
                self.on_success(res)
            except IntegrityError:
                raise AppError()
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, patient_id):
        session = req.context['session']
        try:
            session.query(Patient).filter(Patient.id == patient_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)
