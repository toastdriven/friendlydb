# Green the world, baby.
from gevent import monkey
monkey.patch_all()

from gevent import pywsgi
import re
from friendlydb import get_version
from friendlydb.db import FriendlyDB
try:
    import simplejson as json
except ImportError:
    import json


fdb = None


class NotAllowed(Exception):
    pass


def setup(options):
    # Feel gross about this but just sucking it up for now.
    global fdb

    if not options.data_directory:
        print("The -d flag is required!")
        sys.exit()

    fdb = FriendlyDB(options.data_directory, options.hash_width)


# The HTTPs.
def _make_response(env, start_response, status, body=None):
    start_response(status, [('Content-Type', 'text/plain')])
    if body is None:
        body = {'message': 'ok'}
    return [json.dumps(body)]

def not_found(env, start_response):
    return _make_response(env, start_response, '404 NOT FOUND', {'error': 'Not found.'})

def not_allowed(env, start_response):
    return _make_response(env, start_response, '405 METHOD NOT ALLOWED', {'error': 'That HTTP method is not allowed at this endpoint.'})

def ok(env, start_response, body=None):
    return _make_response(env, start_response, '200 OK', body)

def created(env, start_response, body=None):
    return _make_response(env, start_response, '201 CREATED', body)

def accepted(env, start_response, body=None):
    return _make_response(env, start_response, '202 ACCEPTED', body)

def _check_method(method, request_method):
    if method.upper() != request_method:
        raise NotAllowed()


# The application itself.
def index(request_method):
    _check_method('GET', request_method)
    return ok, {'version': get_version()}

def user_detail(request_method, username):
    _check_method('GET', request_method)
    user = fdb[username]
    return ok, {
        'username': username,
        'following': user.following(),
        'followers': user.followers(),
    }

def user_following(request_method, username):
    _check_method('GET', request_method)
    user = fdb[username]
    return ok, {
        'username': username,
        'following': user.following(),
    }

def user_followers(request_method, username):
    _check_method('GET', request_method)
    user = fdb[username]
    return ok, {
        'username': username,
        'followers': user.followers(),
    }

def user_friends(request_method, username):
    _check_method('GET', request_method)
    user = fdb[username]
    return ok, {
        'username': username,
        'friends': list(user.friends()),
    }

def follow(request_method, username, other_username):
    _check_method('POST', request_method)
    user = fdb[username]
    return created, {
        'username': username,
        'other_username': other_username,
        'followed': user.follow(other_username),
    }

def unfollow(request_method, username, other_username):
    _check_method('POST', request_method)
    user = fdb[username]
    return created, {
        'username': username,
        'other_username': other_username,
        'unfollowed': user.unfollow(other_username),
    }

def is_following(request_method, username, other_username):
    _check_method('GET', request_method)
    user = fdb[username]
    return created, {
        'username': username,
        'other_username': other_username,
        'is_following': user.is_following(other_username),
    }

def is_followed_by(request_method, username, other_username):
    _check_method('GET', request_method)
    user = fdb[username]
    return created, {
        'username': username,
        'other_username': other_username,
        'is_followed_by': user.is_followed_by(other_username),
    }


def application(env, start_response):
    paths = (
        ('^/$', index),
        ('^/(?P<username>[\w\d._-]+)/?$', user_detail),
        ('^/(?P<username>[\w\d._-]+)/following/?$', user_following),
        ('^/(?P<username>[\w\d._-]+)/followers/?$', user_followers),
        ('^/(?P<username>[\w\d._-]+)/friends/?$', user_friends),
        ('^/(?P<username>[\w\d._-]+)/follow/(?P<other_username>[\w\d._-]+)/?$', follow),
        ('^/(?P<username>[\w\d._-]+)/unfollow/(?P<other_username>[\w\d._-]+)/?$', unfollow),
        ('^/(?P<username>[\w\d._-]+)/is_following/(?P<other_username>[\w\d._-]+)/?$', is_following),
        ('^/(?P<username>[\w\d._-]+)/is_followed_by/(?P<other_username>[\w\d._-]+)/?$', is_followed_by),
    )

    request_path = env.get('PATH_INFO', '/')
    request_method = env.get('REQUEST_METHOD', 'GET').upper()

    for path_re, handler in paths:
        if re.match(path_re, request_path):
            url_match = re.search(path_re, request_path)
            url_params = {}

            if hasattr(url_match, 'groupdict'):
                url_params = url_match.groupdict()

            try:
                resp_func, body = handler(request_method, **url_params)
            except NotAllowed:
                return not_allowed(env, start_response)
            except TypeError:
                return not_found(env, start_response)

            return resp_func(env, start_response, body)

    # Nothing matched. 404'd!
    return not_found(env, start_response)


if __name__ == '__main__':
    from optparse import OptionParser
    import sys

    parser = OptionParser()
    parser.add_option("-d", "--data", dest="data_directory", help="The directory to store the data in.")
    parser.add_option("-w", "--width", dest="hash_width", type="int", default=None, help="Defines the width of the hashes.")
    parser.add_option("-H", "--host", dest="host", default='127.0.0.1', help="Choose the host IP/domain name to run the service on. Default: '127.0.0.1'")
    parser.add_option("-p", "--port", dest="port", type="int", default=8008, help="Choose the port to run the service on. Default: 8008")
    (options, args) = parser.parse_args()

    # Set up the DB.
    setup(options)

    # Start handling requests.
    print "Welcome to FriendlyDB (v%s)!" % get_version()
    print "Serving on http://%s:%s..." % (options.host, options.port)
    server = pywsgi.WSGIServer((options.host, options.port), application)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print "Shutting down. Have a nice day!"
