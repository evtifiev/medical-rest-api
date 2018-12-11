# -*- coding: utf-8 -*-

import falcon
from app.errors import UnauthorizedError
from app.model.user import User


def auth_required(req, res, resource, params):
    if req.context['auth_user'] is None:
        raise UnauthorizedError()


def user_info(req, res, resource, param):
    if req.context['auth_user']:
        session = req.context['session']
        user = User.find_by_numeric_id(session, req.context['auth_user'])
        req.context['user'] = user.auth_permission()
    else:
        raise UnauthorizedError()