import logging
import uuid
import hashlib
import hmac


class Session(object):
    """Session storage
    """
    def __init__(self, cache, request_handler):
        self.cache = cache
        self.request_handler = request_handler
        self.prefix = 'adminSession:'

    def get(self):
        uid = self.request_handler.get_secure_cookie('uid')
        session_id = self.request_handler.get_secure_cookie('sid')
        hmac_key = self.request_handler.get_secure_cookie('verification')

        if uid and session_id and hmac_key:
            session_id = session_id.decode('utf-8')
            hmac_key = hmac_key.decode('utf-8')

            secret = self.cache.get(self.prefix + uid.decode('utf-8'))
            if not secret:
                return None
            check_hmac_key = self.generate_hmac(secret.decode('utf-8'), session_id)
            if hmac_key == check_hmac_key:
                return uid
        return None

    def set(self, uid, expires=1):
        secret = uuid.uuid4().hex
        session_id = self.generate_sid(secret)
        hmac_key = self.generate_hmac(secret, session_id)
        self.cache.setex(self.prefix+str(uid), 900, secret)  # set cache
        self.request_handler.set_secure_cookie('uid', str(uid))  # set cookie
        self.request_handler.set_secure_cookie('sid', session_id)
        self.request_handler.set_secure_cookie('verification', hmac_key)

    def destroy(self):
        uid = self.request_handler.get_secure_cookie('uid')
        if uid:
            self.cache.delete(self.prefix + str(uid))
        self.request_handler.clear_cookie('uid')
        self.request_handler.clear_cookie('sid')
        self.request_handler.clear_cookie('verification')

    def generate_sid(self, secret):
        """
        :param salt: str
        :param secret: str
        :return str
        """
        salt = uuid.uuid4().hex.encode('utf-8')
        secret = secret.encode('utf-8')
        return hashlib.sha512(secret + salt).hexdigest()

    def generate_hmac(self, secret, session_id):
        """
        :param sercet: str
        :param session_id: str
        """
        session_id = session_id.encode('utf-8')
        secret = secret.encode('utf-8')
        return hmac.new(session_id, secret, hashlib.sha512).hexdigest()
