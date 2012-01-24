import os
import shutil
import time
from friendlydb import __version__, HASH_WIDTH, SEPARATOR
from friendlydb.exceptions import StorageError, ConfigError
from friendlydb.user import FriendlyUser
try:
    # For performance!
    import simplejson as json
except ImportError:
    import json


class FriendlyDB(object):
    """
    The database of following/followers
    """
    def __init__(self, data_directory=None, hash_width=None, separator=None, user_klass=FriendlyUser):
        if data_directory is None:
            data_directory = os.path.join(os.path.dirname(__file__), 'data')

        self.data_directory = data_directory
        self.hash_width = hash_width or HASH_WIDTH
        self.user_klass = user_klass
        self.separator = separator or SEPARATOR
        self.is_setup = False

        self.setup()

    # Setup methods, to make sure the kit is sane.

    def setup(self):
        if not os.path.exists(self.data_directory):
            os.makedirs(self.data_directory)

        if not os.path.isdir(self.data_directory):
            raise StorageError("The path '%s' is not a directory & hence can't be written to." % self.data_directory)

        config = self._read_config()

        if config.get('separator', self.separator) != self.separator:
            raise ConfigError("The pre-existing separator '%s' doesn't match the current separator '%s'. Data files will be unusable & require migration." % (config.get('separator', self.separator), self.separator))

        # TODO: If there are ever changes that require data migration, we'll
        #       need to check them here.

        # Make sure it's up to date.
        self._write_config()
        self.is_setup = True

    def config_path(self):
        return os.path.join(self.data_directory, 'config.json')

    def _read_config(self):
        config_path = self.config_path()

        if not os.path.exists(config_path):
            self._write_config()

        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        return config

    def _write_config(self):
        config_path = self.config_path()
        config = {
            'version': __version__,
            'separator': self.separator,
            'last_opened': time.time(),
        }

        with open(config_path, 'w') as config_file:
            json.dump(config, config_file)

        return config

    # End-user methods!

    def clear(self):
        shutil.rmtree(self.data_directory)
        self.setup()
        return True

    def __getitem__(self, username):
        kwargs = {}

        if self.hash_width:
            kwargs['hash_width'] = int(self.hash_width)

        if self.separator:
            kwargs['separator'] = self.separator

        return self.user_klass(username, self.data_directory, **kwargs)

    def delete_user(self, username):
        user = self[username]
        return user.delete()
