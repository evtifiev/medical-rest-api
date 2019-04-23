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
from app.model.visit import Visit
from app.model.schedule import Schedule
from app.errors import AppError, InvalidParameterError, UserNotExistsError, DataNotFount
from datetime import datetime, timedelta
from sqlalchemy import and_

LOG = log.get_logger()


FIELDS_VISIT = {
    'last_name': {
        'type': 'string',
        'required': True,
        'minlength': 2,
        'maxlength': 90
    },
    'first_name': {
        'type': 'string',
        'required': True,
        'minlength': 2,
        'maxlength': 40
    },
    'middle_name': {
        'type': 'string',
        'required': True,
        'minlength': 2,
        'maxlength': 70
    },
    'mobile': {
        'type': 'string',
        'required': True,
    },
    'schedule_id': {
        'type': 'integer',
        'required': True,
    },
    'doctor_id': {
        'type': 'integer',
        'required': True,
    },
    'source_of_financing': {
        'type': 'integer',
        'required': False,
    },
}


def validate_visit_create(req, res, resource, params):
    schema = {
        'last_name': FIELDS_VISIT['last_name'],
        'first_name': FIELDS_VISIT['first_name'],
        'middle_name': FIELDS_VISIT['middle_name'],
        'schedule_id': FIELDS_VISIT['schedule_id'],
        'doctor_id': FIELDS_VISIT['doctor_id'],
        'mobile': FIELDS_VISIT['mobile'],
        'source_of_financing': FIELDS_VISIT['source_of_financing']
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


class VisitCollection(BaseResource):
    """
    Handle for endpoint: /v1/visitors/
    """

    @falcon.before(validate_visit_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        visit_req = req.media
        if visit_req:
            patient = Patient()
            patient.first_name = visit_req['first_name']
            patient.last_name = visit_req['last_name']
            patient.middle_name = visit_req['middle_name']
            patient.mobile = visit_req['mobile']
            session.add(patient)
            session.commit()

            if patient.id:
                visit = Visit()
                visit.patient_id = patient.id
                visit.creator_id = req.context['user']
                visit.doctor_id = visit_req['doctor_id']
                visit.schedule_id = visit_req['schedule_id']
                visit.source_of_financing = visit_req['source_of_financing']

                session.add(visit)

                # TODO: Добавить выбивание графика в Schedule
                session.query(Schedule).filter(Schedule.id == visit_req['schedule_id']).update({
                    'is_busy': True
                })
                session.commit()
                data = {
                    "id": str(visit.id)
                }
                self.on_success(res, data=data)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        """
            title     : 'visit2',
            start     : '2019-04-18 10:00',
            end       : '2019-04-18 10:20',
            backgroundColor  : 'orange',
            borderColor: 'orange',
        :param req:
        :param res:
        :return:
        """
        session = req.context['session']
        param = req.params
        if param:
            date_start = datetime.fromtimestamp(int(param['date_start']) / 1000.0).strftime('%Y-%m-%d')
            date_end = datetime.fromtimestamp(int(param['date_end']) / 1000.0).strftime('%Y-%m-%d')
        else:
            date_start = datetime.now().strftime('%Y-%m-%d')
            date_end = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        visit_dbs = session.query(Visit).join(Schedule).filter(and_(Schedule.date_start >= date_start, Schedule.date_end <= date_end)).all()
        if visit_dbs:
            obj = {
                "items": [visit.to_dict() for visit in visit_dbs]
            }
            self.on_success(res, obj)
        else:
            raise DataNotFount()


class VisitItem(BaseResource):
    """
    Handle for endpoint: /v1/visit/{visit_id}

    """

    @falcon.before(auth_required)
    def on_get(self, req, res, visit_id):
        session = req.context['session']
        try:
            department_db = Patient.find_one(session, visit_id)
            self.on_success(res, department_db.to_dict())
        except NoResultFound:
            raise UserNotExistsError('visit_id: %s' % visit_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, visit_id):
        session = req.context['session']
        patient_req = req.media
        if patient_req:
            try:
                session.query(Patient).filter(Patient.id == visit_id). \
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
    def on_delete(self, req, res, visit_id):
        session = req.context['session']
        try:
            session.query(Patient).filter(Patient.id == visit_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)



