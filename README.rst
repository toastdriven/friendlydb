==========
FriendlyDB
==========

``friendlydb`` is a small & fast following/followers database written in
Python. It can be either used directly from your Python code or over HTTP
with small web API.

FriendlyDB isn't meant to be a full user system; it should be used to augment
an existing system to track relationships.


Usage
=====

Using FriendlyDB from Python looks like::

    from friendlydb.db import FriendlyDB

    # Give Friendly a directory to work in.
    fdb = FriendlyDB('/usr/data/friendly')

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

Using FriendlyDB from HTTP looks like::

    Coming soon.


Requirements
============

* Python 2.6+
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

* created 1,000,000 relationships between 10,000 users: 7.3 minutes
* avg time to fetch a user's followers: 0.0008 seconds
* never exceeding 40Mb of RAM RSS


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
:version: 0.2.2
:date: 2012-01-06
