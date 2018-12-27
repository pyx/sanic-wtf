# -*- coding: utf-8 -*-
from collections import ChainMap
from datetime import timedelta
from itertools import chain

from wtforms import Form
from wtforms.csrf.session import SessionCSRF
from wtforms.meta import DefaultMeta
from wtforms.validators import DataRequired, StopValidation
from wtforms.fields.core import Field

from ._patch import patch
from .recaptcha import RecaptchaField

__version__ = '0.7.0.dev0'

__all__ = [
    'SanicForm',
    'FileAllowed', 'file_allowed', 'FileRequired', 'file_required', 'RecaptchaField'
]


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


SUBMIT_VERBS = frozenset({'DELETE', 'PATCH', 'POST', 'PUT'})


sentinel = object()


class FileRequired(DataRequired):
    """Validate that the data is a non-empty `sanic.request.File` object"""
    def __call__(self, form, field):
        # type sanic.request.File as of v 0.5.4 is:
        # File = namedtuple('File', ['type', 'body', 'name'])
        # here, we check whether the name contains anything
        if not getattr(field.data, 'name', ''):
            msg = self.message or field.gettext('This field is required.')
            raise StopValidation(msg)


file_required = FileRequired


class FileAllowed:
    """Validate that the file (by extention) is one of the listed types"""
    def __init__(self, extensions, message=None):
        extensions = (ext.lower() for ext in extensions)
        extensions = (
            ext if ext.startswith('.') else '.' + ext for ext in extensions)
        self.extensions = frozenset(extensions)
        self.message = message

    def __call__(self, form, field):
        filename = getattr(field.data, 'name', '')
        if not filename:
            return

        filename = filename.lower()
        # testing with .endswith instead of the fastest `in` test, because
        # there may be extensions with more than one dot (.), e.g. ".tar.gz"
        if any(filename.endswith(ext) for ext in self.extensions):
            return

        raise StopValidation(self.message or field.gettext(
            'File type does not allowed.'))


file_allowed = FileAllowed


class ChainRequestParameters(ChainMap):
    """ChainMap with sanic.RequestParameters style API"""
    def get(self, name, default=None):
        """Return the first element with key `name`"""
        return super().get(name, [default])[0]

    def getlist(self, name, default=None):
        """Return all elements with key `name`

        Only elementes of the first chained map with such key are return.
        """
        return super().get(name, default)

class SanicForm(Form):
    """Form with session-based CSRF Protection.

    Upon initialization, the form instance will setup CSRF protection with
    settings fetched from provided Sanic style request object.  With no
    request object provided, CSRF protection will be disabled.
    """
    class Meta(DefaultMeta):
        csrf = True
        csrf_class = SessionCSRF

    def __init__(self, request=None, *args, meta=None, **kwargs):
        # Patching status
        self.patched = False

        # Meta
        form_meta = meta_for_request(request)
        form_meta.update(meta or {})
        kwargs['meta'] = form_meta

        # Formdata
        self.request = request
        if request is not None:
            formdata = kwargs.pop('formdata', sentinel)
            if formdata is sentinel:
                if request.files:
                    formdata = ChainRequestParameters(
                        request.form, request.files)
                else:
                    formdata = request.form
            # signature of wtforms.Form (formdata, obj, prefix, ...)
            args = chain([formdata], args)

        super().__init__(*args, **kwargs)

        # Pass app to fields that need it 
        if self.request is not None:
            for name, field in self._fields.items():
                if hasattr(field, '_get_app'):
                    field._get_app(self.request.app)

    # @unpatch ??
    def validate_on_submit(self):
        ''' For async validators: use self.validate_on_submit_async.
            This method is only still here for backward compatibility
        '''
        if self.patched is not False:
            raise RuntimeError('Once you go async, you can never go back. :)\
                                Continue using validate_on_submit_async \
                                 instead of validate_on submit')
        """Return `True` if this form is submited and all fields verified"""
        return self.request and (self.request.method in SUBMIT_VERBS) and \
               self.validate()

    @patch
    async def validate_on_submit_async(self):
        ''' supports async validators and Sanic-WTF Recaptcha 
        
        .. note::
        
            As a side effect of patching wtforms to support async, 
            there's a restriction you must be aware of: 
            Don't use SanifForm.validate_on_submit() after running this method.
            Doing so will most likely cause an error.

        '''
        return self.request and (self.request.method in SUBMIT_VERBS) and \
               await self.validate()
