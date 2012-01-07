import json
import os
import shutil
import unittest2
from friendlydb import __version__, HASH_WIDTH, SEPARATOR, ADDED, DELETED
from friendlydb.db import FriendlyDB
from friendlydb.exceptions import FriendlyDBError, StorageError, ConfigError
from friendlydb.user import FriendlyUser


class FriendlyTestCase(unittest2.TestCase):
    def setUp(self):
        super(FriendlyTestCase, self).setUp()
        self.data_dir = '/tmp/test_friendly'

    def tearDown(self):
        shutil.rmtree(self.data_dir, ignore_errors=True)
        super(FriendlyTestCase, self).tearDown()


class FriendlyUserTestCase(FriendlyTestCase):
    def setUp(self):
        super(FriendlyUserTestCase, self).setUp()
        # For all the tests that aren't init/setup/caching-related...
        self.daniel = FriendlyUser('daniel', self.data_dir)
        self.alice = FriendlyUser('alice', self.data_dir)
        self.bob = FriendlyUser('bob', self.data_dir)
        self.joe = FriendlyUser('joe', self.data_dir)

    def test_init(self):
        self.assertFalse(os.path.exists(self.data_dir))

        fuser = FriendlyUser('daniellindsley', self.data_dir)
        self.assertEqual(fuser.username, 'daniellindsley')
        self.assertEqual(fuser.data_directory, self.data_dir)
        self.assertEqual(fuser.hash_width, HASH_WIDTH)
        self.assertEqual(fuser.separator, SEPARATOR)
        self.assertEqual(fuser.added, ADDED)
        self.assertEqual(fuser.deleted, DELETED)
        self.assertEqual(fuser.user_hash, '0163d1')
        self.assertEqual(fuser.full_path, '/tmp/test_friendly/0163d1')
        self.assertFalse(fuser.is_setup)
        self.assertEqual(fuser._following, None)
        self.assertEqual(fuser._followers, None)

        # Test bad options.
        self.assertRaises(ConfigError, FriendlyUser, 'daniellindsley', self.data_dir, hash_width=-1)
        self.assertRaises(ConfigError, FriendlyUser, 'daniellindsley', self.data_dir, hash_width=0)
        self.assertRaises(ConfigError, FriendlyUser, 'daniellindsley', self.data_dir, hash_width=33)
        self.assertRaises(ConfigError, FriendlyUser, 'daniellindsley', self.data_dir, separator='')

    def test_setup(self):
        fuser = FriendlyUser('daniellindsley', self.data_dir)
        self.assertFalse(os.path.exists(fuser.full_path))
        self.assertFalse(fuser.is_setup)

        fuser.setup()
        self.assertTrue(os.path.exists(fuser.full_path))
        self.assertTrue(fuser.is_setup)

    def test_following_path(self):
        self.assertEqual(self.daniel.following_path(), '/tmp/test_friendly/aa47f8/following')
        self.assertEqual(self.alice.following_path(), '/tmp/test_friendly/6384e2/following')
        self.assertEqual(self.bob.following_path(), '/tmp/test_friendly/9f9d51/following')
        self.assertEqual(self.joe.following_path(), '/tmp/test_friendly/8ff324/following')

    def test_followers_path(self):
        self.assertEqual(self.daniel.followers_path(), '/tmp/test_friendly/aa47f8/followers')
        self.assertEqual(self.alice.followers_path(), '/tmp/test_friendly/6384e2/followers')
        self.assertEqual(self.bob.followers_path(), '/tmp/test_friendly/9f9d51/followers')
        self.assertEqual(self.joe.followers_path(), '/tmp/test_friendly/8ff324/followers')

    def test_follow(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))

        self.assertEqual(self.daniel._following, None)
        daniel_following = self.daniel.following()
        self.assertEqual(daniel_following, ['alice', 'bob', 'joe'])
        self.assertEqual(self.daniel._following, ['alice', 'bob', 'joe'])

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
        self.assertEqual(daniel_following, ['alice', 'bob'])

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

        self.assertEqual(self.daniel._followers, None)
        daniel_followers = self.daniel.followers()
        self.assertEqual(daniel_followers, ['alice', 'bob'])
        self.assertEqual(self.daniel._followers, ['alice', 'bob'])

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

    def test_following_history(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.bob.follow('daniel'))
        self.assertTrue(self.daniel.unfollow('bob'))
        self.assertTrue(self.daniel.unfollow('joe'))
        self.assertTrue(self.daniel.follow('bob'))

        history = self.daniel.following_history()
        self.assertEqual(len(history[0]), 3)
        self.assertEqual([(bits[0], bits[1]) for bits in history], [('Added', 'alice'), ('Added', 'bob'), ('Added', 'joe'), ('Deleted', 'bob'), ('Deleted', 'joe'), ('Added', 'bob')])

    def test_followers_history(self):
        self.assertTrue(self.daniel.follow('alice'))
        self.assertTrue(self.daniel.follow('bob'))
        self.assertTrue(self.daniel.follow('joe'))
        self.assertTrue(self.alice.follow('daniel'))
        self.assertTrue(self.alice.follow('bob'))
        self.assertTrue(self.bob.follow('daniel'))
        self.assertTrue(self.daniel.unfollow('bob'))
        self.assertTrue(self.daniel.unfollow('joe'))
        self.assertTrue(self.daniel.follow('bob'))

        history = self.bob.followers_history()
        self.assertEqual(len(history[0]), 3)
        self.assertEqual([(bits[0], bits[1]) for bits in history], [('Added', 'daniel'), ('Added', 'alice'), ('Deleted', 'daniel'), ('Added', 'daniel')])


class FriendlyDBTestCase(FriendlyTestCase):
    def test_init(self):
        self.assertFalse(os.path.exists(self.data_dir))

        fdb = FriendlyDB(data_directory=self.data_dir)
        self.assertEqual(fdb.data_directory, self.data_dir)
        self.assertEqual(fdb.hash_width, HASH_WIDTH)
        self.assertEqual(fdb.separator, SEPARATOR)
        self.assertEqual(fdb.user_klass, FriendlyUser)
        self.assertTrue(fdb.is_setup)
        self.assertTrue(os.path.exists(self.data_dir))
        self.assertTrue(os.path.exists(os.path.join(self.data_dir, 'config.json')))

    def test_bad_init(self):
        # Test non-directory
        try:
            os.unlink('/tmp/no_wai')
        except:
            pass

        with open('/tmp/no_wai', 'w') as no_wai:
            no_wai.write('')

        self.assertRaises(StorageError, FriendlyDB, data_directory='/tmp/no_wai')
        os.unlink('/tmp/no_wai')

        # Test outdated config
        shutil.rmtree('/tmp/old_config', ignore_errors=True)
        os.makedirs('/tmp/old_config')

        with open('/tmp/old_config/config.json', 'w') as old_config_file:
            json.dump({'version': [0, -1, 0], 'separator': '-*-::-*-'}, old_config_file)

        self.assertRaises(ConfigError, FriendlyDB, data_directory='/tmp/old_config')
        shutil.rmtree('/tmp/old_config')

    def test_get_user(self):
        fdb = FriendlyDB(data_directory=self.data_dir)
        daniel = fdb['daniel']
        self.assertTrue(isinstance(daniel, FriendlyUser))
        self.assertEqual(daniel.username, 'daniel')

    def test_clear(self):
        fdb = FriendlyDB(data_directory=self.data_dir)
        daniel = fdb['daniel']

        self.assertFalse(os.path.exists(daniel.full_path))
        daniel.setup()
        self.assertTrue(os.path.exists(daniel.full_path))

        self.assertTrue(fdb.clear())
        self.assertFalse(os.path.exists(daniel.full_path))
