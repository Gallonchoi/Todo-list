import uuid
import hashlib
import os
import redis
import sqlite3
import logging

import tornado.web
from tornado.ioloop import IOLoop
from tornado.options import define, options, parse_command_line

import session


define('port', default=8000, help="run on the given port", type=int)


class Cache(object):
    def __init__(self):
        DB_HOST = 'localhost'
        DB_PORT = 6379
        self._cache = redis.StrictRedis(host=DB_HOST, port=DB_PORT, db=0)

    @property
    def cache(self):
        return self._cache


class UserModel(object):
    def __init__(self, db):
        self.db = db

    def get_by_username(self, username):
        c = self.db.cursor()
        param = (username, )
        c.execute("SELECT * FROM users WHERE username = ?", param)
        return c.fetchone()

    def register(self, username, password):
        user = self.get_by_username(username)
        if user:
            return {'success': False, 'msg': 'Duplicated username'}
        else:
            p_hash, p_salt = self.encrypt_password(password)
            c = self.db.cursor()
            c.execute("INSERT INTO users VALUES ('%s', '%s', '%s')" % (username, p_hash, p_salt))
            self.db.commit()
            return {'success': True, 'username': username}

    def login(self, username, password):
        user = self.get_by_username(username)
        if not user:
            return {'success': False, 'msg': 'User not found'}
        elif self.check_password(password, user['password_hash'], user['password_salt']):
            return {'success': True, 'user': user}
        else:
            return {'success': False, 'msg': 'Incorrect password'}

    def encrypt_password(self, password):
        if type(password) is str:
            p_salt = uuid.uuid4().hex
            p_hash = hashlib.sha512(password.encode('utf-8') + p_salt.encode('utf-8')).hexdigest()
        else:
            p_salt = p_hash = None
        return p_hash, p_salt

    def check_password(self, password, p_hash, p_salt):
        return hashlib.sha512(password.encode('utf-8')+p_salt.encode('utf-8')).hexdigest() == p_hash



class BaseHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.cache = self.settings.get('cache').cache
        self.db = self.settings.get('db')
        self.db.row_factory = sqlite3.Row
        self.user_model = UserModel(self.db)
        self.session = session.Session(self.cache, self)
        self.xsrf_token

    def get_current_user(self):
        username = self.session.get()
        user = self.user_model.get_by_username(username)
        if not user:
            self.session.destroy()
        return user


class HomeHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render('home.html', user=self.get_current_user())


class RegisterHandler(BaseHandler):
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        user = self.user_model.register(username, password)
        if user['success'] is True:
            self.session.set(user['username'])
        self.redirect('/')


class AuthLoginHandler(BaseHandler):
    def get(self):
        if self.get_current_user():
            self.redirect('/')
        else:
            self.render('login.html')

    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        user = self.user_model.login(username, password)
        if user['success'] is True:
            self.session.set(username)
        self.redirect('/')


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/', HomeHandler),
            (r'/user/login/?', AuthLoginHandler),
            (r'/user/signup/?', RegisterHandler)
        ]
        ROOT_PATH = os.path.dirname(__file__)
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            login_url="/user/login",
            template_path=os.path.join(ROOT_PATH, 'template'),
            static_path=os.path.join(ROOT_PATH, 'static'),
            xsrf_cookies=True,
            debug=True,
            cache=Cache(),
            db=sqlite3.connect('todo.db')
        )
        tornado.web.Application.__init__(self, handlers, **settings)


def main():
    parse_command_line()
    logging.info("Development server is running at http://127.0.0.1:%s" % options.port)
    logging.info("Quit the server with CONTROL-C")
    application = Application()
    application.listen(options.port)
    IOLoop.instance().start()


if __name__ == '__main__':
    main()