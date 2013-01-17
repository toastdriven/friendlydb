import datetime
import redis
import time
from friendlydb import SEPARATOR


class FriendlyUser(object):
    def __init__(self, username, conn=None, separator=None):
        self.username = username
        self.conn = conn
        self.separator = separator

        if self.separator is None:
            self.separator = SEPARATOR

        self.is_setup = False

    def setup(self):
        if self.conn is None:
            self.conn = redis.StrictRedis(host='localhost', port=6379, db=0)

        self.is_setup = True

    def __repr__(self):
        username = self.username

        if isinstance(self.username, unicode):
            username = username.encode('utf-8')

        return "<%s %s>" % (self.__class__.__name__, username)

    def generate_key(self, username, key_type):
        return self.separator.join([username, key_type])

    def convert_time_to_datetime(self, the_time):
        return datetime.datetime.fromtimestamp(the_time.time())

    def current_time_score(self):
        return int(time.time())

    # End-user methods!

    def following(self, with_dates=False):
        following = []

        for follow_info in self.conn.zrevrange(self.generate_key(self.username, 'following'), 0, -1, withscores=True):
            if not with_dates:
                following.append(follow_info[0])
            else:
                following.append({
                    'username': follow_info[0],
                    'followed_on': self.convert_time_to_datetime(follow_info[1]),
                })

        return following

    def followers(self, with_dates=False):
        followers = []

        for follow_info in self.conn.zrevrange(self.generate_key(self.username, 'followers'), 0, -1, withscores=True):
            if not with_dates:
                followers.append(follow_info[0])
            else:
                followers.append({
                    'username': follow_info[0],
                    'followed_on': self.convert_time_to_datetime(follow_info[1]),
                })

        return followers

    def follow(self, username):
        if self.username == username:
            return False

        # Add to our following.
        key = self.generate_key(self.username,'following')
        time_score = self.current_time_score()
        self.conn.zadd(key, time_score, username)

        # Make sure the change is reflected in their followers.
        key = self.generate_key(username,'followers')
        time_score = self.current_time_score()
        self.conn.zadd(key, time_score, self.username)

        return True

    def unfollow(self, username):
        if self.username == username:
            return False

        # Remove from our following.
        key = self.generate_key(self.username,'following')
        self.conn.zrem(key, username)

        # Make sure the change is reflected in their followers.
        key = self.generate_key(username,'followers')
        self.conn.zrem(key, self.username)

        return True

    def is_following(self, username):
        following = self.following()
        return username in following

    def is_followed_by(self, username):
        followers = self.followers()
        return username in followers

    def friends(self):
        following = set(self.following())
        followers = set(self.followers())
        return following.intersection(followers)

    def delete(self):
        following = self.following()
        followers = self.followers()

        for follow in following:
            self.unfollow(follow)

        for follower in followers:
            other = self.__class__(follower, conn=self.conn, separator=self.separator)
            other.unfollow(self.username)

        # Finally, remove the keys.
        self.conn.delete(self.generate_key(self.username, 'following'))
        self.conn.delete(self.generate_key(self.username, 'followers'))

        return True
