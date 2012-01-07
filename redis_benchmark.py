# A small, stupid Redis benchmark for friendlydb.
#
# v0.3.1
# ------
#
# Generating 10000 took 0.108589887619
# Building 1000000 relations took 144.261595011
# Checking 1000 users followers took 0.111661195755
#   mean: 0.000110897779465
#   min: 9.70363616943e-05
#   max: 0.000331878662109

from __future__ import print_function
import random
import redis
import shutil
import time
from friendlydb.db import FriendlyDB
from friendlydb.user import FriendlyUser


# Config.
all_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
data_dir = '/tmp/bench_redis_friendly'
user_count = 10000
relation_count = 1000000
followers_check = 1000


# Go go go!
chars = [char for char in all_chars]
users = []
conn = redis.StrictRedis(host='localhost', port=6379, db=15)


class RedisFriendlyUser(FriendlyUser):
    def __init__(self, *args, **kwargs):
        global conn
        super(RedisFriendlyUser, self).__init__(*args, **kwargs)
        self.conn = conn

    def setup(self):
        # Don't do any of the usual file stuff.
        self.is_setup = True

    def follow(self, username):
        self.conn.sadd("%s_following" % self.username, username)
        self.conn.sadd("%s_followers" % username, self.username)

    def unfollow(self, username):
        self.conn.srem("%s_following" % self.username, username)
        self.conn.srem("%s_followers" % username, self.username)

    def following(self):
        return self.conn.smembers("%s_following" % self.username)

    def followers(self):
        return self.conn.smembers("%s_followers" % self.username)

    def is_following(self, username):
        return self.conn.sismember("%s_following" % self.username, username)

    def is_followed_by(self, username):
        return self.conn.sismember("%s_followers" % self.username, username)


fdb = FriendlyDB(data_dir, user_klass=RedisFriendlyUser)


def time_taken(func):
    start = time.time()
    func()
    return time.time() - start


def generate_users():
    # Generate enough usernames to matter.
    for i in range(0, user_count):
        users.append(''.join(random.sample(chars, random.randint(6, 12))))


def build_relations():
    for i in range(0, relation_count):
        username_1 = random.choice(users)
        username_2 = random.choice(users)
        user = fdb[username_1]

        if random.randint(0, 4) < 3:
            user.follow(username_2)
        else:
            user.unfollow(username_2)


def check_followers():
    times = []
    results = {}
    overall_start = time.time()

    for i in range(0, followers_check):
        start = time.time()

        user = fdb[random.choice(users)]
        user.followers()

        end = time.time()
        times.append(end - start)

    overall_end = time.time()
    results['overall_time'] = overall_end - overall_start

    # Calculate mean/min/max.
    results['mean_time'] = sum(times) / len(times)
    results['min_time'] = min(times)
    results['max_time'] = max(times)
    return results


if __name__ == '__main__':
    conn.flushdb()

    print('Running benchmark...')
    print('  User Count: %s' % user_count)
    print('  Relation Count: %s' % relation_count)
    print('  Followers Check Count: %s' % followers_check)

    print('')
    print('')
    print('')
    print('Generating users...')
    print("Generating %s took %s" % (user_count, time_taken(generate_users)))
    print('')
    print('Building relations...')
    print("Building %s relations took %s" % (relation_count, time_taken(build_relations)))
    print('')

    print('Checking followers...')
    results = check_followers()
    print("Checking %s users followers took %s" % (followers_check, results['overall_time']))
    print("  mean: %s" % results['mean_time'])
    print("  min: %s" % results['min_time'])
    print("  max: %s" % results['max_time'])

    conn.flushdb()
