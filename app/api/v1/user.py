# - * - coding: utf-8 -*-

import re
import falcon
import base64

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from cerberus import Validator
from cerberus.errors import ValidationError

from app import log
from app.api.common import BaseResource
from app.utils.hooks import auth_required
from app.utils.auth import encrypt_token, hash_password, verify_password, uuid, decrypt_token
from app.model import User, Menu, Role, Position, Department
from app.errors import AppError, InvalidParameterError, UserNotExistsError, PasswordNotMatch

LOG = log.get_logger()

FIELDS = {
    'username': {
        'type': 'string',
        'required': True,
        'minlength': 4,
        'maxlength': 60
    },
    'password': {
        'type': 'string',
        'regex': '[0-9a-zA-Z]\w{3,14}',
        'required': True,
        'minlength': 8,
        'maxlength': 64
    },
    'last_name': {
        'type': 'string',
        'required': False,
        'minlength': 0,
        'maxlength': 90
    },
    'first_name': {
        'type': 'string',
        'required': False,
        'minlength': 0,
        'maxlength': 40
    },
    'middle_name': {
        'type': 'string',
        'required': False,
        'minlength': 0,
        'maxlength': 40
    },
    'email': {
        'type': 'string',
        'regex': '[a-zA-Z0-9._-]+@(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,4}',
        'required': True,
        'maxlength': 320
    },
    'email_password': {
        'type': 'string',
        'required': False,
        'minlength': 0,
        'maxlength': 120
    },
    'mobile': {
        'type': 'string',
        'required': True,
        'min': 11,
        'max': 30
    },
    'phone': {
        'type': 'string',
        'required': True,
        'min': 3,
        'max': 30
    },
    'info': {
        'type': 'dict',
        'required': False
    },
    'blocked': {
        'type': 'boolean',
        'required': False
    },
    'role_id': {
        'type': 'integer',
        'required': True
    },
    'menu_id': {
        'type': 'integer',
        'required': True
    },
    'department_id': {
        'type': 'integer',
        'required': True
    },
    'position_id': {
        'type': 'integer',
        'required': True
    },
}


def validate_user_create(req, res, resource, params):
    schema = {
        'username': FIELDS['username'],
        'password': FIELDS['password'],
        'last_name': FIELDS['last_name'],
        'first_name': FIELDS['first_name'],
        'middle_name': FIELDS['middle_name'],
        'email': FIELDS['email'],
        'email_password': FIELDS['email_password'],
        'mobile': FIELDS['mobile'],
        'phone': FIELDS['phone'],
        'info': FIELDS['info'],
        'blocked': FIELDS['blocked'],
        'menu_id': FIELDS['menu_id'],
        'role_id': FIELDS['role_id'],
        'department_id': FIELDS['department_id'],
        'position_id': FIELDS['position_id'],
    }

    v = Validator(schema)
    try:
        if not v.validate(req.media):
            raise InvalidParameterError(v.errors)
    except ValidationError:
        raise InvalidParameterError('Invalid Request %s' % req.media)


class UserCollection(BaseResource):
    """
    Handle for endpoint: /v1/settings/users
    Add new user from user cabinet
    """

    # @falcon.before(auth_required)
    @falcon.before(validate_user_create)
    def on_post(self, req, res):
        session = req.context['session']
        user_req = req.media
        if user_req:
            user = User()
            user.username = user_req['username']
            user.password = hash_password(user_req['password']).decode('utf-8')
            user.last_name = user_req['last_name'] if 'last_name' in user_req else None
            user.first_name = user_req['first_name'] if 'first_name' in user_req else None
            user.middle_name = user_req['middle_name'] if 'middle_name' in user_req else None
            user.email = user_req['email']
            user.email_password = user_req['email_password']
            user.mobile = user_req['mobile']
            user.phone = user_req['phone']
            user.info = user_req['info'] if 'info' in user_req else None
            user.blocked = user_req['blocked'] if 'blocked' in user_req else None
            sid = uuid()
            user.numeric_id = sid
            user.token = encrypt_token(sid).decode('utf-8')
            menu = Menu.find_one(session, user_req['menu_id'])
            role = Role.find_one(session, user_req['role_id'])
            department = Department.find_one(session, user_req['department_id'])
            position = Position.find_one(session, user_req['position_id'])
            user.role_id = role.id
            user.menu_id = menu.id
            user.department_id = department.id
            user.position_id = position.id
            session.add(user)
            session.commit()
            self.on_success(res, user.get_token())
        else:
            raise InvalidParameterError(req.context['data'])

    @falcon.before(auth_required)
    def on_get(self, req, res):
        session = req.context['session']
        user_dbs = session.query(User).all()
        if user_dbs:
            obj = [user.to_dict_all() for user in user_dbs]
            self.on_success(res, obj)
        else:
            raise AppError()


class UserItem(BaseResource):
    """
    Handle for endpoint: /v1/setting/users/{user_id}
    """

    @falcon.before(auth_required)
    def on_get(self, req, res, user_id):
        session = req.context['session']
        try:
            user_db = User.find_one(session, user_id)
            self.on_success(res, user_db.to_dict_all())
        except NoResultFound:
            raise UserNotExistsError('user id: %s' % user_id)

    @falcon.before(auth_required)
    def on_put(self, req, res, user_id):
        session = req.context['session']
        user_req = req.media
        if user_req:
            try:
                session.query(User).filter(User.id == user_id). \
                    update({
                    'username': user_req['username'],
                    'last_name': user_req['last_name'] if 'last_name' in user_req else None,
                    'first_name': user_req['first_name'] if 'first_name' in user_req else None,
                    'middle_name': user_req['middle_name'] if 'middle_name' in user_req else None,
                    'email': user_req['email'],
                    'email_password': user_req['email_password'],
                    'mobile': user_req['mobile'],
                    'phone': user_req['phone'],
                    'blocked': user_req['blocked'] if 'blocked' in user_req else None,
                    'role_id': user_req['role_id'],
                    'menu_id': user_req['menu_id'],
                    'department_id': user_req['department_id'],
                    'position_id': user_req['position_id'],
                    'info': user_req['info'] if 'info' in user_req else None})
                session.commit()

                self.on_success(res)
            except IntegrityError:
                raise InvalidParameterError(req.media)
        else:
            raise InvalidParameterError(req.media)

    @falcon.before(auth_required)
    def on_delete(self, req, res, user_id):
        session = req.context['session']
        try:

            session.query(User).filter(User.id == user_id).delete()
            self.on_success(res)
        except NoResultFound:
            raise InvalidParameterError(req.media)


class Signin(BaseResource):
    def on_get(self, req, res):
        session = req.context['session']
        token = req.get_param('token')
        try:
            user_db = User.find_by_numeric_id(session, str(int(decrypt_token(token))))
            if not user_db.blocked:
                self.on_success(res, user_db.auth_info())
                # self.on_success(res, user_db.to_test_one())
            else:
                raise UserNotExistsError('Токен заблокирован. Обратитесь к администратору.')
        except NoResultFound:
            raise UserNotExistsError('Пользователь: не найден. Проверьте правильность ввода данных.')


class Auth(BaseResource):
    """
    Handle for endpoint: /v1/users/auth
    """
    LOGIN = ''
    RESETPW = 'resetpw'
    REGISTER = 'register'
    SINGOUT = 'signout'

    def on_post(self, req, res):
        cmd = re.split('\\W+', req.path)[-1:][0]
        if cmd == Auth.RESETPW:
            self.process_resetpw(req, res)
        elif cmd == Auth.SINGOUT:
            self.process_signout(req, res)
        elif cmd == Auth.REGISTER:
            self.process_register(req, res)
        else:
            self.process_login(req, res)

    # Авторизация пользователя
    def process_login(self, req, res):
        data = req.context['data']
        username = data['username']
        password = base64.b64decode(data['password']).decode("utf-8")
        session = req.context['session']
        try:
            user_db = User.find_by_username(session, username)
            if verify_password(password, user_db.password.encode('utf-8')):
                if not user_db.blocked:
                    self.on_success(res, user_db.get_token())
                else:
                    # TODO: Дописать обработчики если токен заблокирован
                    raise UserNotExistsError('Доступ в систему заблокирован. Обратитесь к администратору.')
            else:
                raise PasswordNotMatch('Неверный пароль для пользователя: %s' % username)
        except NoResultFound:
            raise UserNotExistsError('Пользователь: %s не найден. Проверьте правильность ввода данных.' % username)

    def process_signout(self, req, res):
        self.on_success(res)

    # Регистрация нового пользователя, через форму регистрации
    def process_register(self, req, res):
        session = req.context['session']
        user_req = req.context['data']
        if user_req:
            user = User()
            user.username = user_req['username']
            user.email = user_req['email']
            user.password = hash_password(user_req['password']).decode('utf-8')
            user.phone = user_req['phone']
            user.info = user_req['info'] if 'info' in user_req else None
            user.blocked = False
            user.menu_id = user_req['menu_id']
            user.role_id = user_req['role_id']
            user.position_id = user_req['position_id']
            user.department_id = user_req['department_id']
            sid = uuid()
            user.numeric_id = sid
            user.token = encrypt_token(sid).decode('utf-8')
            session.add(user)
            session.commit()
            self.on_success(res, user.get_token())
        else:
            raise InvalidParameterError(req.context['data'])

    @falcon.before(auth_required)
    def process_resetpw(self, req, res):
        pass
