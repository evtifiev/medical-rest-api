# -*- coding: utf-8 -*-

import falcon
import functools

from app import log
from app import config
from app.middleware import AuthHandler, JSONTranslator, DatabaseSessionManager
from app.database import db_session, init_session

from app.api.common import base
from app.api.v1 import user, role, module, menu, department, position, doctor, holiday, patient, schedule, visit
from app.errors import AppError
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware

cors = CORS(allow_origins_list=['http://127.0.0.1:8080', 'http://localhost:8080', 'http://localhost:8008',
                                'http://127.0.0.1:5000', 'http://lk.gb38.ru','*'], allow_all_headers=True,
            allow_all_methods=True, allow_credentials_all_origins=True)

LOG = log.get_logger()


class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info('API Server is starting')

        self.add_route('/', base.BaseResource())
        # Endpoint "Пользователи"
        self.add_route('/v1/users', user.UserCollection())
        self.add_route('/v1/user/{user_id:int}', user.UserItem())
        self.add_route('/v1/auth/signin', user.Signin())
        self.add_route('/v1/auth/register', user.Auth())
        self.add_route('/v1/auth/signout', user.Auth())
        self.add_route('/v1/auth', user.Auth())
        # Endpoint "Роли"
        self.add_route('/v1/roles', role.RoleCollection())
        self.add_route('/v1/role/{role_id:int}', role.RoleItem())
        # Endpoint "Меню"
        self.add_route('/v1/menus', menu.MenuCollection())
        self.add_route('/v1/menu/{menu_id:int}', menu.MenuItem())
        # Endpoint "Должности"
        self.add_route('/v1/positions', position.PositionCollection())
        self.add_route('/v1/position/{position_id:int}', position.PositionItem())
        # Endpoint "Подразделения"
        self.add_route('/v1/departments', department.DepartmentCollection())
        self.add_route('/v1/department/{department_id:int}', department.DepartmentItem())
        # Endpoint "Модули и Разрешения"
        self.add_route('/v1/modules', module.ModuleCollection())
        self.add_route('/v1/module/{module_id:int}', module.ModuleItem())
        self.add_route('/v1/permissions', module.ModulePermissionCollection())
        self.add_route('/v1/permission/{permission_id}', module.ModulePermissionItem())

        # Endpoint "Врачи и специализации"
        self.add_route('/v1/doctors', doctor.DoctorCollection())
        self.add_route('/v1/doctor/{doctor_id:int}', doctor.DoctorItem())
        self.add_route('/v1/specializations', doctor.DoctorSpecializationCollection())
        self.add_route('/v1/specialization/{doctor_specialization_id}', doctor.DoctorSpecializationItem())

        # Endpoint "Выходные и праздничные дни"
        self.add_route('/v1/holidays', holiday.HolidayCollection())
        self.add_route('/v1/holiday/{holiday_id:int}', holiday.HolidayItem())

        # Endpoint "Пациенты"
        self.add_route('/v1/patients', patient.PatientCollection())
        self.add_route('/v1/patient/{patient_id:int}', patient.PatientItem())

        # Endpoint "Расписание"
        self.add_route('/v1/schedules', schedule.ScheduleCollection())
        # Endpoint "Запись на прием"
        self.add_route('/v1/visits', visit.VisitCollection())


        self.add_error_handler(AppError, AppError.handle)


init_session()
middleware = [AuthHandler(), JSONTranslator(), DatabaseSessionManager(db_session), cors.middleware,
              MultipartMiddleware()]
application = App(middleware=middleware)

if __name__ == "__main__":
    from wsgiref import simple_server

    httpd = simple_server.make_server('127.0.0.1', 5000, application)
    httpd.serve_forever()
