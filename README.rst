==========
FriendlyDB
==========

``friendlydb`` is a small & fast following/followers database written in
Python. It can be either used directly from your Python code or over HTTP
with small web API.

FriendlyDB isn't meant to be a full user system; it should be used to augment
an existing system to track relationships.


WARNING
=======

Starting with v2.0.0, FriendlyDB is **NOT** backward-compatible with v0.4.0 &
before. Prior to v2.0.0, data was stored on the filesystem, but in v2.0.0 &
later, data is stored in Redis.

It was rewritten to use Redis for several reasons:

* Better performance
* Less wear/tear on hard disks
* Simpler code

However, this does mean you will need to run your own version of the Redis
server (2.6.4+ recommended).

See below if you need to migrate from an older install to v2.0.0.


Usage
=====

Using FriendlyDB from Python looks like::

    from friendlydb.db import FriendlyDB

    # Start using the DB (assumes Redis default host/port/db).
    fdb = FriendlyDB()
    # Alternatively, ``fdb = FriendlyDB(host='127.0.0.2', port=7100, db=3)``

    # Grab a user by their username.
    daniel = fdb['daniel']

    # Follow a couple users.
    daniel.follow('alice')
    daniel.follow('bob')
    daniel.follow('joe')

    # Check the following.
    daniel.following()
    # Returns:
    # [
    #     'alice',
    #     'bob',
    #     'joe',
    # ]

    # Check joe's followers.
    fdb['joe'].followers()
    # Returns:
    # [
    #     'daniel',
    # ]

    # Unfollow.
    daniel.unfollow('bob')

    # Check the following.
    daniel.following()
    # Returns:
    # [
    #     'alice',
    #     'joe',
    # ]

    # Dust off & nuke everything from orbit.
    fdb.clear()

Using FriendlyDB from HTTP looks like (all trailing slashes are optional)::

    # In one shell, start the server.
    python friendlydb/server.py -d /tmp/friendly

    # From another, run some URLs.
    curl -X GET http://127.0.0.1:8008/
    # {"version": "0.3.0"}

    curl -X GET http://127.0.0.1:8008/daniel/
    # {"username": "daniel", "following": [], "followers": []}

    curl -X POST http://127.0.0.1:8008/daniel/follow/alice/
    # {"username": "daniel", "other_username": "alice", "followed": true}
    curl -X POST http://127.0.0.1:8008/daniel/follow/bob/
    # {"username": "daniel", "other_username": "bob", "followed": true}
    curl -X POST http://127.0.0.1:8008/daniel/follow/joe/
    # {"username": "daniel", "other_username": "joe", "followed": true}

    curl -X POST http://127.0.0.1:8008/daniel/unfollow/joe/
    # {"username": "daniel", "other_username": "joe", "unfollowed": true}

    curl -X GET http://127.0.0.1:8008/daniel/
    # {"username": "daniel", "following": ["alice", "bob"], "followers": []}

    curl -X GET http://127.0.0.1:8008/daniel/is_following/alice/
    # {"username": "daniel", "other_username": "alice", "is_following": true}

    curl -X GET http://127.0.0.1:8008/alice/is_followed_by/daniel/
    # {"username": "alice", "other_username": "daniel", "is_followed_by": true}

    curl -X GET http://127.0.0.1:8008/alice/is_followed_by/joe/
    # {"username": "alice", "other_username": "joe", "is_followed_by": false}


Requirements
============

* Python 2.6+ or Python 3.3+
* redis.py >= 2.7.2
* (Optional) gevent for the HTTP server
* (Optional) unittest2 for running tests


Installation
============

Using pip, you can install it with ``pip install friendlydb``.


Performance
===========

You can scope out FriendlyDB's performance for yourself by running the
included ``benchmark.py`` script.

In tests on a 2011 MacBook Pro (i7), the benchmark script demonstrated:

* created 1,000,000 relationships between 10,000 users: 179 seconds (~2.5X faster than 0.4.0)
* avg time to fetch a user's followers: 0.0016 seconds
* never exceeding 41Mb of RAM RSS


Migrating from v0.4.0 to 2.0.0
==============================

First, install & run the Redis server.

Second, run ``pip install redis>=2.7.2``.

To migrate your data, the easiest way is to leave your old install of FriendlyDB
in place (using the HTTP server), create a new install w/ Redis, then run
code like::

    import requests
    import json
    # The new version.
    from friendlydb import FriendlyDB

    old_url = 'http://127.0.0.1:8008/'
    fdb = FriendlyDB()

    for username in users:
        user = fdb[username]

        # Following.
        resp = requests.get("{0}/{1}/following/".format(old_url, username))
        data = json.loads(resp.content)

        for f_username in data.get("following", []):
            user.follow(f_username)

You should create your own script & verify your data post-migration. No promises
are made about the effectiveness/accuracy of the above code.


Running Tests
=============

``friendlydb`` is maintained with passing tests at all times. Simply run::

    python -m unittest2 tests


Contributions
=============

In order for a contribution to be considered for merging, it must meet the
following requirements:

* Patch cleanly solves the problem
* Added test coverage (now passing) to expose the bug & check for regression
* If the behavior affects end-users, there must be docs on the changes
* The patch/tests must be compatibly licensed with New BSD

The best way to submit contributions is by forking the project on Github,
applying your changes *on a new branch*, pushing those changes back to GH &
submitting a pull request through the GitHub interface.


License
=======

New BSD license.

:author: Daniel Lindsley
:version: 2.0.0
:date: 2013-01-17
