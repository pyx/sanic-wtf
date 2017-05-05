# -*- coding: utf-8 -*-
from datetime import timedelta
from itertools import chain

from wtforms import Form
from wtforms.csrf.session import SessionCSRF
from wtforms.meta import DefaultMeta

__version__ = '0.4.0'

__all__ = ['SanicForm']


def to_bytes(text, encoding='utf8'):
    if isinstance(text, str):
        return text.encode(encoding)
    return bytes(text)


def meta_for_request(request):
    """Create a meta dict object with settings from request.app"""
    meta = {'csrf': False}
    if not request:
        return meta
    config = request.app.config

    csrf = meta['csrf'] = config.get('WTF_CSRF_ENABLED', True)
    if not csrf:
        return meta

    meta['csrf_field_name'] = config.get('WTF_CSRF_FIELD_NAME', 'csrf_token')
    secret = config.get('WTF_CSRF_SECRET_KEY')
    if secret is None:
        secret = config.get('SECRET_KEY')
    if not secret:
        raise ValueError(
            'CSRF protection needs either WTF_CSRF_SECRET_KEY or SECRET_KEY')
    meta['csrf_secret'] = to_bytes(secret)

    seconds = config.get('WTF_CSRF_TIME_LIMIT', 1800)
    meta['csrf_time_limit'] = timedelta(seconds=seconds)

    name = config.get('WTF_CSRF_CONTEXT_NAME', 'session')
    meta['csrf_context'] = request[name]
    return meta


SUBMIT_WORDS = frozenset({'DELETE', 'PATCH', 'POST', 'PUT'})


class SanicForm(Form):
    """Form with session-based CSRF Protection.

    Upon initialization, the form instance will setup CSRF protection with
    settings fetched from provided Sanic style request objerct.  With no
    request object provided, CSRF protection will be disabled.
    """
    class Meta(DefaultMeta):
        csrf = True
        csrf_class = SessionCSRF

    def __init__(self, request=None, *args, meta=None, **kwargs):
        """"""
        form_meta = meta_for_request(request)
        form_meta.update(meta or {})
        kwargs['meta'] = form_meta

        self.request = request
        if request is None:
            super().__init__(*args, **kwargs)
            return

        formdata = kwargs.pop('formdata', getattr(request, 'form', None))
        # signature of wtforms.Form (formdata, obj, prefix, ...)
        super().__init__(*chain([formdata], args), **kwargs)

    def validate_on_submit(self):
        """Return `True` if this form is submited and all fields verified"""
        request = self.request
        return request and request.method in SUBMIT_WORDS and self.validate()
