import hashlib
from typing import Any

import six
from urllib.parse import unquote

import sqlalchemy as sa

from ckan.common import CKANConfig
from ckan.types import CKANApp

class TrackingMiddleware(object):

    def __init__(self, app: CKANApp, config: CKANConfig):
        self.app = app
        self.engine = sa.create_engine(config.get_value('sqlalchemy.url'))

    def __call__(self, environ: Any, start_response: Any) -> Any:
        path = environ['PATH_INFO']
        method = environ.get('REQUEST_METHOD')
        if path == '/_tracking' and method == 'POST':
            # do the tracking
            # get the post data
            payload = six.ensure_str(environ['wsgi.input'].read())
            parts = payload.split('&')
            data = {}
            for part in parts:
                k, v = part.split('=')
                data[k] = unquote(v)
            start_response('200 OK', [('Content-Type', 'text/html')])
            # we want a unique anonomized key for each user so that we do
            # not count multiple clicks from the same user.
            key = ''.join([
                environ['HTTP_USER_AGENT'],
                environ['REMOTE_ADDR'],
                environ.get('HTTP_ACCEPT_LANGUAGE', ''),
                environ.get('HTTP_ACCEPT_ENCODING', ''),
            ])
            key = hashlib.md5(six.ensure_binary(key)).hexdigest()
            # store key/data here
            sql = '''INSERT INTO tracking_raw
                     (user_key, url, tracking_type)
                     VALUES (%s, %s, %s)'''
            self.engine.execute(sql, key, data.get('url'), data.get('type'))
            return []
        return self.app(environ, start_response)
