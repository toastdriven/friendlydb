__author__ = 'Daniel Lindsley'
__version__ = (0, 4, 0)
__license__ = 'BSD'


def get_version():
    return '-'.join(['.'.join([str(num) for num in __version__[:3]])] + list(__version__[3:]))


# Constants
HASH_WIDTH = 6
ADDED = 'A'
DELETED = 'D'
SEPARATOR = '::'

# TODO:
# * LRU cache
# * Maybe add ``flock`` & exponential back-off in.
# * Docs
