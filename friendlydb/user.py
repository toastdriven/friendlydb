# Let's try to get away without file-locking for now.
# import fcntl
import hashlib
import os
import time
from friendlydb import HASH_WIDTH, SEPARATOR, ADDED, DELETED
from friendlydb.exceptions import ConfigError


class FriendlyUser(object):
    def __init__(self, username, data_directory, hash_width=None, separator=None):
        self.username = username
        self.data_directory = data_directory
        self.hash_width = hash_width
        self.separator = separator

        if self.hash_width is None:
            self.hash_width = HASH_WIDTH

        if self.separator is None:
            self.separator = SEPARATOR

        self.added = ADDED
        self.deleted = DELETED
        self.user_hash = self.hash_username()
        self.full_path = os.path.join(self.data_directory, self.user_hash)
        self.is_setup = False
        self._following = None
        self._followers = None

        if self.hash_width <= 0:
            raise ConfigError("'filename_width' must be greater than 0. Got: %s" % self.hash_width)

        if self.hash_width > 32:
            raise ConfigError("'filename_width' must be less than or equal to 32. Got: %s" % self.hash_width)

        if not isinstance(self.separator, basestring) or self.separator == '':
            raise ConfigError("'separator' must be a string of at least 1 characters or more. Got: %s" % self.separator)

    def setup(self):
        if not os.path.exists(self.full_path):
            os.makedirs(self.full_path)

        # Append nothing, but enough to make sure the files are there.
        self._touch(self.following_path())
        self._touch(self.followers_path())

        self.is_setup = True

    def __repr__(self):
        username = self.username

        if isinstance(self.username, unicode):
            username = username.encode('utf-8')

        return "<%s %s>" % (self.__class__.__name__, username)

    # Plumbing.

    def hash_username(self):
        return hashlib.md5(self.username).hexdigest()[:self.hash_width]

    def following_path(self):
        return os.path.join(self.full_path, 'following')

    def followers_path(self):
        return os.path.join(self.full_path, 'followers')

    def _read(self, filename):
        if not self.is_setup:
            self.setup()

        with open(filename, 'r') as read_file:
            return read_file.readlines()

    def _touch(self, filename):
        with open(filename, 'a') as touch_file:
            touch_file.write('')

    def _make_record(self, action, username, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        return self.separator.join([action, username, str(float(timestamp))])

    def _parse_record(self, record):
        record = record.strip()
        bits = record.split(self.separator)

        if bits[0] == self.added:
            bits[0] = 'Added'
        elif bits[0] == self.deleted:
            bits[0] = 'Deleted'
        else:
            bits[0] = 'Unknown'

        bits[2] = float(bits[2])
        return bits

    def _write(self, filename, action, username, timestamp=None):
        if not self.is_setup:
            self.setup()

        record = self._make_record(action, username, timestamp)

        with open(filename, 'a') as add_file:
            add_file.write(record + '\n')

    def _add_to_following(self, following_username):
        following_path = self.following_path()
        self._write(following_path, self.added, following_username)

    def _add_to_followers(self, follower_username):
        followers_path = self.followers_path()
        self._write(followers_path, self.added, follower_username)

    def _remove_from_following(self, ex_following_username):
        following_path = self.following_path()
        self._write(following_path, self.deleted, ex_following_username)

    def _remove_from_followers(self, ex_follower_username):
        followers_path = self.followers_path()
        self._write(followers_path, self.deleted, ex_follower_username)

    def _unify_people(self, history):
        people_set = set([])

        for bits in history:
            if bits[0] == 'Added':
                people_set.add(bits[1])
            else:
                try:
                    people_set.remove(bits[1])
                except KeyError:
                    pass

        # If we didn't care about ordering, we could've just returned the
        # set. Unfortunately, in proper date order gives a better user
        # experience.
        people = []

        for bits in history:
            if bits[1] in people_set:
                people.append(bits[1])
                # Remove the name from the set so we don't dupe it.
                people_set.remove(bits[1])

        return people

    # End-user methods!

    def following_history(self):
        history = []
        following_path = self.following_path()

        for line in self._read(following_path):
            history.append(self._parse_record(line))

        return history

    def following(self, cached=False):
        if cached and self._following is not None:
            return self._following

        history = self.following_history()
        self._following = self._unify_people(history)
        return self._following

    def followers_history(self):
        history = []
        followers_path = self.followers_path()

        for line in self._read(followers_path):
            history.append(self._parse_record(line))

        return history

    def followers(self, cached=False):
        if cached and self._followers is not None:
            return self._followers

        history = self.followers_history()
        self._followers = self._unify_people(history)
        return self._followers

    def follow(self, username):
        if self.username == username:
            return False

        # Add to our following.
        self._add_to_following(username)

        # Make sure the change is reflected in their followers.
        other = self.__class__(username, self.data_directory, hash_width=self.hash_width, separator=self.separator)
        other._add_to_followers(self.username)
        return True

    def unfollow(self, username):
        if self.username == username:
            return False

        # Remove from our following.
        self._remove_from_following(username)

        # Make sure the change is reflected in their followers.
        other = self.__class__(username, self.data_directory, hash_width=self.hash_width, separator=self.separator)
        other._remove_from_followers(self.username)
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
            other = self.__class__(follower, self.data_directory, hash_width=self.hash_width, separator=self.separator)
            other.unfollow(self.username)

        return True
