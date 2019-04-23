# -*- coding: utf-8 -*-
import falcon
import datetime

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.functions import func
from sqlalchemy import and_, or_
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.utils.calendar_shedule import generate
from app.utils import alchemy
from app.model.schedule import Schedule
from app.model.holiday import Holiday
from app.model.doctor import Doctor
from app.model.user import User
from app.errors import AppError, InvalidParameterError, UserNotExistsError, DataNotFount

LOG = log.get_logger()

FIELDS_SCHEDULE = {
    'date_one': {
        'type': 'string',
        'required': False,
    },
    'dates': {
        'type': 'list',
        'required': False,
    },
    'doctor': {
        'type': 'integer',
        'required': True,
    },
    'startTime': {
        'type': 'string',
        'required': True,
    },
    'endTime': {
        'type': 'string',
        'required': True,
    },
    'resource': {
        'type': 'string',
        'required': False,
    },
    'period': {
        'type': 'boolean',
        'required': True,
    },
    'workdays': {
        'type': 'list',
        'required': True,
    },
    'interval': {
        'type': 'integer',
        'required': True,
    }
}


def validate_department_create(req, res, resource, params):
    schema = {
        'date_one': FIELDS_SCHEDULE['date_one'],
        'dates': FIELDS_SCHEDULE['dates'],
        'doctor': FIELDS_SCHEDULE['doctor'],
        'startTime': FIELDS_SCHEDULE['startTime'],
        'endTime': FIELDS_SCHEDULE['endTime'],
        'interval': FIELDS_SCHEDULE['interval'],
        'period': FIELDS_SCHEDULE['period'],
        'workdays': FIELDS_SCHEDULE['workdays'],
        'resource': FIELDS_SCHEDULE['resource'],
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.context)


# Работа с коллекцией подразделения
class ScheduleCollection(BaseResource):
    """
    Handle for endpoint: /v1/departments/
    """

    @falcon.before(validate_department_create)
    @falcon.before(auth_required)
    def on_post(self, req, res):
        session = req.context['session']
        schedule_req = req.media
        if schedule_req:
            """
            'date_one': FIELDS_SCHEDULE['date_one'],
        'dates': FIELDS_SCHEDULE['dates'],
        'doctor': FIELDS_SCHEDULE['doctor'],
        'startTime': FIELDS_SCHEDULE['startTime'],
        'endTime': FIELDS_SCHEDULE['endTime'],
        'interval': FIELDS_SCHEDULE['interval'],
        'period': FIELDS_SCHEDULE['period'],
        'workdays': FIELDS_SCHEDULE['workdays'],
        'resource': FIELDS_SCHEDULE['resource'],
            """
            if schedule_req['period']:
                dates = schedule_req['dates']
                date_start = dates[0]
                date_end = dates[1]
            else:
                date_start = schedule_req['date_one']
                date_end = None

            start_time = schedule_req['startTime']
            end_time = schedule_req['endTime']
            interval = schedule_req['interval']
            doctor = schedule_req['doctor']
            workdays = schedule_req['workdays']
            holidays_dbs = session.query(Holiday.date).filter(
                func.extract('year', Holiday.date) == datetime.datetime.today().year).all()
            if holidays_dbs:
                try:
                    generate(start_date=date_start, end_date=date_end, holidays_list=holidays_dbs,
                             start_time=start_time,
                             end_time=end_time, workdays_list=workdays,
                             interval=interval, doctor=doctor, creator=req.context['user'], session=session)
                    data = {
                        "message": "Расписание успешно добавлено"
                    }
                    self.on_success(res, data=data)
                except:
                    self.on_error(res, data={})
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        # subq = (session.query(
        #     Schedule.doctor_id, func.min(Schedule.date_end).label('date_start'), func.max(Schedule.date_end).label('date_end'),
        # ).group_by(Schedule.doctor_id).order_by(
        #     func.max(Schedule.date_end).desc())).subquery()
        #
        # schedules = (session.query(Doctor.user_id, subq, User.last_name, User.first_name, User.middle_name).
        #        join(subq, and_(Doctor.id == subq.c.doctor_id)).join(User, and_(Doctor.user_id == User.id))
        #        ).all()
        #
        # if schedules:
        #     obj = {
        #         "items": [{
        #             "doctor": schedule[4] + ' ' + schedule[5] + ' ' + schedule[6],
        #             "date_start": alchemy.datetime_to_timestamp(schedule[2]),
        #             "date_end": alchemy.datetime_to_timestamp(schedule[3])
        #         } for schedule in schedules]
        #     }
        if req.get_param_as_bool('doctor_id'):
            if req.params['doctor_id'] and req.params['date']:
                day = datetime.datetime.strptime(req.params['date'], "%d.%m.%Y")
                schedule_dbs = session.query(Schedule).filter(
                    and_(Schedule.date_start >= day, Schedule.date_start < day + datetime.timedelta(days=1),
                         Schedule.is_busy == False, Schedule.doctor_id == int(req.params['doctor_id']))).all()
                obj = {"items": [schedule.to_dict_reseption() for schedule in schedule_dbs]}
        else:
            obj = {
                "items": []
            }
        # if (req.get_param_as_bool('ll')):  # Long list
        #     current_time = datetime.datetime.utcnow()
        #     one_mount = current_time + datetime.timedelta(weeks=4)
        #     schedule_dbs = session.query(Schedule).filter(
        #         and_(Schedule.date_start < one_mount, Schedule.is_busy == False)).all()
        #     obj = {"items": [schedule.to_dict() for schedule in schedule_dbs]}

        if req.get_param_as_bool('all'):
                subq = (session.query(
                    Schedule.doctor_id, func.min(Schedule.date_end).label('date_start'),
                    func.max(Schedule.date_end).label('date_end'),
                ).group_by(Schedule.doctor_id).order_by(
                    func.max(Schedule.date_end).desc())).subquery()

                schedules = (session.query(Doctor.user_id, subq, User.last_name, User.first_name, User.middle_name).
                             join(subq, and_(Doctor.id == subq.c.doctor_id)).join(User, and_(Doctor.user_id == User.id))
                             ).all()

                if schedules:
                    obj = {
                        "items": [{
                            "doctor": schedule[4] + ' ' + schedule[5] + ' ' + schedule[6],
                            "date_start": alchemy.datetime_to_timestamp(schedule[2]),
                            "date_end": alchemy.datetime_to_timestamp(schedule[3])
                        } for schedule in schedules]
                    }

        if len(obj.get('items')):
            self.on_success(res, obj)
        else:
            raise DataNotFount()

# Работа с подразделением
# class ScheduleItem(BaseResource):
#     """
#     Handle for endpoint: /v1/departments/{department_id}
#     """
#
#     @falcon.before(auth_required)
#     def on_get(self, req, res, department_id):
#         session = req.context['session']
#         try:
#             department_db = Schedule.find_one(session, department_id)
#             self.on_success(res, department_db.to_dict())
#         except NoResultFound:
#             raise UserNotExistsError('department_id: %s' % department_id)
#
#     @falcon.before(auth_required)
#     def on_put(self, req, res, department_id):
#         session = req.context['session']
#         department_req = req.media
#         if department_req:
#             try:
#                 session.query(Schedule).filter(Schedule.id == department_id). \
#                     update({'name': department_req['name']})
#                 session.commit()
#                 self.on_success(res)
#             except IntegrityError:
#                 raise AppError()
#         else:
#             raise InvalidParameterError(req.media)
#
#     @falcon.before(auth_required)
#     def on_delete(self, req, res, department_id):
#         session = req.context['session']
#         try:
#             session.query(Schedule).filter(Schedule.id == department_id).delete()
#             self.on_success(res)
#         except NoResultFound:
#             raise InvalidParameterError(req.media)
