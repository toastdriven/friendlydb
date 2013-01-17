import redis
from friendlydb.user import FriendlyUser


class FriendlyDB(object):
    """
    The database of following/followers.
    """
    def __init__(self, host='localhost', port=6379, db=0, user_klass=None, separator=None):
        self.host = host
        self.port = port
        self.db = db
        self.user_klass = user_klass
        self.separator = separator
        self.conn = None
        self.is_setup = False

        if self.user_klass is None:
            self.user_klass = FriendlyUser

        self.setup()

    # Setup methods, to make sure the kit is sane.

    def setup(self):
        self.conn = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        self.is_setup = True

    # End-user methods!

    def clear(self):
        self.conn.flushdb()
        self.setup()
        return True

    def __getitem__(self, username):
        return self.user_klass(username, conn=self.conn, separator=self.separator)

    def delete_user(self, username):
        user = self[username]
        return user.delete()
