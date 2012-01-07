# A small, stupid benchmark for friendlydb.
#
# v0.3.1
# ------
#
# Generating 10000 took 0.103417158127
# Building 1000000 relations took 455.301289082
# Checking 1000 users followers took 0.428857803345
#   mean: 0.000428096532822
#   min: 0.000310897827148
#   max: 0.000933885574341
#
# v0.2.1
# ------
#
# Generating 10000 took 0.106270074844
# Building 1000000 relations took 439.715919018
# Checking 1000 users followers took 0.83282494545
#   mean: 0.000831272602081
#   min: 0.000524997711182
#   max: 0.000524997711182 # FAIL - fixed in v0.3.1
#

from __future__ import print_function
import random
import shutil
import time
from friendlydb.db import FriendlyDB


# Config.
all_chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
data_dir = '/tmp/bench_friendly'
user_count = 10000
relation_count = 1000000
followers_check = 1000


# Go go go!
chars = [char for char in all_chars]
users = []
fdb = FriendlyDB(data_dir)


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
    shutil.rmtree(data_dir, ignore_errors=True)

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

    shutil.rmtree(data_dir, ignore_errors=True)
