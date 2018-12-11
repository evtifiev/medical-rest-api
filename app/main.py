# -*- coding: utf-8 -*-

import falcon
import functools

from app import log
from app import config
from app.middleware import AuthHandler, JSONTranslator, DatabaseSessionManager
from app.database import db_session, init_session

from app.api.common import base
from app.api.v1 import user, role, module, menu
from app.errors import AppError
from falcon_cors import CORS
from falcon_multipart.middleware import MultipartMiddleware

cors = CORS(allow_origins_list=['http://127.0.0.1:8080', 'http://localhost:8080', 'http://localhost:8008',
                                'http://127.0.0.1:5000', '*'], allow_all_headers=True,
            allow_all_methods=True, allow_credentials_all_origins=True)

LOG = log.get_logger()


class App(falcon.API):
    def __init__(self, *args, **kwargs):
        super(App, self).__init__(*args, **kwargs)
        LOG.info('API Server is starting')

        self.add_route('/', base.BaseResource())
        # Endpoint "Пользователи"
        self.add_route('/v1/settings/users', user.UserCollection())
        self.add_route('/v1/settings/user/{user_id:int}', user.UserItem())
        self.add_route('/v1/auth/signin', user.Signin())
        self.add_route('/v1/auth/register', user.Auth())
        self.add_route('/v1/auth/signout', user.Auth())
        self.add_route('/v1/auth', user.Auth())
        # Endpoint "Роли"
        self.add_route('/v1/settings/roles', role.RoleCollection())
        self.add_route('/v1/settings/role/{role_id:int}', role.RoleItem())
        # Endpoint "Меню"
        self.add_route('/v1/settings/menus', menu.MenuCollection())
        self.add_route('/v1/settings/menu/{menu_id:int}', menu.MenuItem())
        # Endpoint "Модули и Разрешения"
        self.add_route('/v1/settings/modules', module.ModuleCollection())
        self.add_route('/v1/settings/module/{module_id:int}', module.ModuleItem())
        self.add_route('/v1/settings/module/permissions', module.ModulePermissionCollection())
        self.add_route('/v1/settings/module/permission/{permission_id}', module.ModulePermissionItem())

        self.add_error_handler(AppError, AppError.handle)


init_session()
middleware = [AuthHandler(), JSONTranslator(), DatabaseSessionManager(db_session), cors.middleware,
              MultipartMiddleware()]
application = App(middleware=middleware)

if __name__ == "__main__":
    from wsgiref import simple_server

    httpd = simple_server.make_server('127.0.0.1', 5000, application)
    httpd.serve_forever()
