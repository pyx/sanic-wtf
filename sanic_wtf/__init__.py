# -*- coding: utf-8 -*-
from operator import itemgetter
from wtforms import Form
from wtforms.csrf.session import SessionCSRF
from wtforms.meta import DefaultMeta

__version__ = '0.2.0'


def to_bytes(text, encoding='utf8'):
    if isinstance(text, str):
        return text.encode(encoding)
    return bytes(text)


# NOTE
# This is dark magic, the Meta class is constantly changing...
# You've been warned.

class SanicWTF:
    """The WTForms helper"""
    bound = False
    #: Function that returns a dict-like session object when given the current
    #: request.  Override this to customize how the session is accessed.
    get_csrf_context = itemgetter('session')

    #: Form class derived from :code:`wtforms.form.Form`.
    Form = Form

    def __init__(self, app=None):
        self.app = app
        self.bound = False

        # NOTE:
        # have to create new class each time, we don't want to share states
        # between instances of SanicWTF.
        class SanicForm(Form):
            """Form with session-based CSRF Protection"""
            class Meta(DefaultMeta):
                csrf_class = SessionCSRF
                csrf_field_name = 'csrf_token'

                @property
                def csrf(self):
                    raise NotImplementedError(
                        'used form outside of running app')

            @property
            def hidden_tag(self):
                return getattr(self, self.Meta.csrf_field_name)

        self.Form = SanicForm

        if app:
            self.init_app(app)

    def init_app(self, app):
        """Setup the form class using settings from :code:`app.config`

        This method should be called only once, either explicitly or
        implicitly by passing in the :code:`app` object when creating
        :class:`SanicWTF` instance.
        """
        if self.bound:
            raise RuntimeError(
                'SanicWTF instance can only be initialized with an app once')
        self.bound = True

        @app.listener('after_server_start')
        async def setup_csrf(app, loop):
            """Get settings from app and setup the Form class accordingly"""
            conf = app.config
            Meta = self.Form.Meta
            Meta.csrf = conf.get('WTF_CSRF_ENABLED', True)
            if not Meta.csrf:
                return

            secret = conf.get('WTF_CSRF_SECRET_KEY', conf.get('SECRET_KEY'))
            if not secret:
                raise ValueError(
                    'please set either WTF_CSRF_SECRET_KEY or SECRET_KEY')
            Meta.csrf_secret = to_bytes(secret)

            field_name = conf.get('WTF_CSRF_FIELD_NAME', Meta.csrf_field_name)
            Meta.csrf_field_name = field_name

        @app.middleware('request')
        async def setup_csrf_context(request):
            """Setup the csrf_context to be used for CSRF Protection"""
            Meta = self.Form.Meta
            if not Meta.csrf:
                return
            Meta.csrf_context = self.get_csrf_context(request)
