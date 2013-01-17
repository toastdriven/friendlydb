import redis
import unittest2
from friendlydb import SEPARATOR
from friendlydb.db import FriendlyDB
from friendlydb.user import FriendlyUser


class FriendlyTestCase(unittest2.TestCase):
    def setUp(self):
        super(FriendlyTestCase, self).setUp()
        self.host = 'localhost'
        self.port = 6379
        self.db = 0

        self.conn = redis.StrictRedis(host=self.host, port=self.port, db=self.db)
        self.conn.flushdb()

    def tearDown(self):
        self.conn.flushdb()
        super(FriendlyTestCase, self).tearDown()


class FriendlyUserTestCase(FriendlyTestCase):
    def setUp(self):
        super(FriendlyUserTestCase, self).setUp()
        # For all the tests that aren't init/setup/caching-related...
        self.daniel = FriendlyUser('daniel', conn=self.conn)
        self.alice = FriendlyUser('alice', conn=self.conn)
        self.bob = FriendlyUser('bob', conn=self.conn)
        self.joe = FriendlyUser('joe', conn=self.conn)

    def test_init(self):
        fuser = FriendlyUser('daniellindsley', conn=self.conn)
        self.assertEqual(fuser.username, 'daniellindsley')
        self.assertEqual(fuser.conn, self.conn)
        self.assertEqual(fuser.separator, SEPARATOR)
        self.assertFalse(fuser.is_setup)

    def test_setup(self):
        fuser = FriendlyUser('daniellindsley', conn=self.conn)
        self.assertFalse(fuser.is_setup)

        fuser.setup()
        self.assertTrue(fuser.is_setup)

    def test_follow(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))

        daniel_following = self.daniel.following()
        self.assertEqual(daniel_following, ['joe', 'bob', 'alice'])

        alice_following = self.alice.following()
        self.assertEqual(alice_following, ['daniel'])

    def test_cant_follow_self(self):
        self.assertFalse(self.daniel.follow('daniel'))
        self.assertFalse(self.daniel.unfollow('daniel'))

    def test_unfollow(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.daniel.unfollow('bob'))
        self.assertTrue(self.daniel.unfollow('joe'))
        self.assertTrue(self.daniel.follow('bob'))

        # Make sure it worked.
        daniel_following = self.daniel.following()
        self.assertEqual(daniel_following, ['bob', 'alice'])

        # Make sure the follow/unfollow/follow worked right.
        bob_followers = self.bob.followers()
        self.assertEqual(bob_followers, ['daniel'])

        joe_followers = self.joe.followers()
        self.assertEqual(joe_followers, [])

    def test_followed(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.bob.follow('daniel'))

        daniel_followers = self.daniel.followers()
        self.assertEqual(daniel_followers, ['bob', 'alice'])

        alice_followers = self.alice.followers()
        self.assertEqual(alice_followers, ['daniel'])

    def test_is_following(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.bob.follow('daniel'))

        self.assertTrue(self.daniel.is_following('alice'))
        self.assertTrue(self.daniel.is_following('bob'))
        self.assertTrue(self.daniel.is_following('joe'))
        self.assertTrue(self.alice.is_following('daniel'))
        self.assertFalse(self.bob.is_following('joe'))
        self.assertFalse(self.joe.is_following('daniel'))

    def test_is_followed_by(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.bob.follow('daniel'))

        self.assertTrue(self.daniel.is_followed_by('alice'))
        self.assertTrue(self.daniel.is_followed_by('bob'))
        self.assertFalse(self.daniel.is_followed_by('joe'))
        self.assertTrue(self.alice.is_followed_by('daniel'))
        self.assertFalse(self.bob.is_followed_by('joe'))
        self.assertFalse(self.joe.is_followed_by('bob'))

    def test_delete(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.alice.follow('bob'))
        self.assertTrue(self.bob.follow('daniel'))

        # Make sure it worked.
        daniel_following = self.daniel.following()
        self.assertEqual(daniel_following, ['joe', 'bob', 'alice'])
        alice_followers = self.alice.followers()
        self.assertEqual(alice_followers, ['daniel'])
        alice_following = self.alice.following()
        self.assertEqual(alice_following, ['daniel', 'bob'])

        # Kaboom!
        self.daniel.delete()

        alice_followers = self.alice.followers()
        self.assertEqual(alice_followers, [])
        alice_following = self.alice.following()
        self.assertEqual(alice_following, ['bob'])

    def test_friends(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.alice.follow('bob'))
        self.assertTrue(self.bob.follow('daniel'))

        mutual_1 = self.daniel.friends()
        self.assertEqual(mutual_1, set(['bob', 'alice']))
        mutual_2 = self.alice.friends()
        self.assertEqual(mutual_2, set(['daniel']))


class FriendlyDBTestCase(FriendlyTestCase):
    def test_init(self):
        fdb = FriendlyDB(host=self.host, port=self.port, db=self.db)
        self.assertEqual(fdb.host, self.host)
        self.assertEqual(fdb.port, self.port)
        self.assertEqual(fdb.db, self.db)
        self.assertEqual(fdb.user_klass, FriendlyUser)
        self.assertEqual(fdb.separator, None)
        self.assertTrue(fdb.is_setup)

    def test_get_user(self):
        fdb = FriendlyDB(host=self.host, port=self.port, db=self.db)
        daniel = fdb['daniel']
        self.assertTrue(isinstance(daniel, FriendlyUser))
        self.assertEqual(daniel.username, 'daniel')

    def test_clear(self):
        fdb = FriendlyDB(host=self.host, port=self.port, db=self.db)
        daniel = fdb['daniel']
        daniel_key = daniel.generate_key(daniel.username, 'following')

        self.assertFalse(self.conn.zrange(daniel_key, 0, -1))
        daniel.follow('alice')
        self.assertTrue(self.conn.zrange(daniel_key, 0, -1))

        self.assertTrue(fdb.clear())
        self.assertFalse(self.conn.zrange(daniel_key, 0, -1))

    def test_delete_user(self):
        fdb = FriendlyDB(host=self.host, port=self.port, db=self.db)
        daniel = fdb['daniel']
        alice = fdb['alice']

        daniel.follow('alice')
        alice.follow('daniel')
        alice.follow('bob')

        self.assertEqual(daniel.following(), ['alice'])
        self.assertEqual(alice.following(), ['daniel', 'bob'])
        self.assertEqual(alice.followers(), ['daniel'])

        fdb.delete_user('alice')

        self.assertEqual(daniel.following(), [])
