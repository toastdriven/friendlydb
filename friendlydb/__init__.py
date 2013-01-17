__author__ = 'Daniel Lindsley'
__version__ = (2, 0, 0)
__license__ = 'BSD'


def get_version():
    return '-'.join(['.'.join([str(num) for num in __version__[:3]])] + list(__version__[3:]))


# Constants
SEPARATOR = '::'
