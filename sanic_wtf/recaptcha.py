from wtforms.fields import Field
from wtforms import ValidationError
import aiorecaptcha
from markupsafe import Markup
from sanic.exceptions import InvalidUsage


__all__ = ['RecaptchaField']

async def recaptcha_validator(form, field):
    # Skip if testing
    if hasattr(form, 'request'):
        if 'TESTING' in form.request.app.config:
            if form.request.app.config['TESTING'] is True:
                return

    # Get captcha response from request
    try:
        response = form.request.form.get('g-recaptcha-response')
    except InvalidUsage:
        response = None
    if not response:
        try:
            response = form.request.json.get('g-recaptcha-response')
        except InvalidUsage:
            pass

    if response is None:
        raise ValidationError('The response parameter is missing.')
    ip = getattr(form.request, 'ip', None)

    # Verify
    try:
        await aiorecaptcha.verify(
            secret=form.request.app.config[field._config_prefix + '_PRIVATE_KEY'],
            response=response,
            remoteip=ip
        )
    except aiorecaptcha.RecaptchaError as e:
        raise ValidationError(e.msg)

def recaptcha_widget(self, field, error=None, **kwargs):
    js = aiorecaptcha.js(
        onload=field._config.get(self._config_prefix + '_ONLOAD'),
        render=field._config.get(self._config_prefix + '_RENDER'),
        language=field._config.get(self._config_prefix + '_LANGUAGE'),
        async_=field._config.get(self._config_prefix + '_ASYNC'),
        defer=field._config.get(self._config_prefix + '_DEFER'),
    )
    if field._config.get(self._config_prefix + '_JS_ONLY') is True:
        return Markup(js)
    html = aiorecaptcha.html(
        site_key=field._config.get(self._config_prefix + '_PUBLIC_KEY'),
        theme=field._config.get(self._config_prefix + '_THEME'),
        badge=field._config.get(self._config_prefix + '_BADGE'),
        size=field._config.get(self._config_prefix + '_SIZE'),
        type_=field._config.get(self._config_prefix + '_TYPE'),
        tabindex=field._config.get(self._config_prefix + '_TABINDEX'),
        callback=field._config.get(self._config_prefix + '_CALLBACK'),
        expired_callback=field._config.get(self._config_prefix + '_EXPIRED_CALLBACK'),
        error_callback=field._config.get(self._config_prefix + '_ERROR_CALLBACK')
    )
    return Markup(js) + Markup(html)

class RecaptchaField(Field):
    '''

    Async Recaptcha Field
    
    Arguments:

        label (int): Field's label

        validators (list, tuple): Leave it as None. Overriding this will replace the stock validator

        config_prefix (str): 
        
            * Default: 'RECAPTCHA'. 
        
            * Change this if you want to use many types of Recaptchas in your app e.g. RECAPTCHA_V2 and RECAPTCHA_V3

    .. note::

        Don't pass this field your configs. Instead set it to your app's configs.

        Then when instantiating your sanic form for rendering, pass it your request object

    Configs to set:

        Request with an App that has the following configs:

            RECAPTCHA_PUBLIC_KEY:

                * Required

                * Your Sitekey

            RECAPTCHA_PRIVATE_KEY:

                * Required

            RECAPTCHA_ONLOAD (str):

                * Optional
            
                * The name of your callback function to be executed once all the dependencies have loaded.

            RECAPTCHA_RENDER (str):

                * Optional
                
                * Whether to render the widget explicitly. 
                
                * Defaults to onload, which will render the widget in the first g-recaptcha tag it finds.

                * Either: ``"onload"`` or explicitly specify a widget value

            RECAPTCHA_LANGUAGE (str):

                * Optional

                * hl language code

                * Reference: https://developers.google.com/recaptcha/docs/language

            RECAPTCHA_ASYNC (bool):

                * Optional

                * add async tag to JS script

                * Default True

            RECAPTCHA_DEFER (bool):

                * Optional

                * Add def tag to JS Script

                * Default True

            RECAPTCHA_THEME:

                * The color theme of the widget.

                * Optional

                * One of: (dark, light)

                * Default: light

            RECAPTCHA_BADGE:

                * Reposition the reCAPTCHA badge. 'inline' lets you position it with CSS.

                * Optional

                * One of: ('bottomright', 'bottomleft', 'inline')

                * Default: None

            RECAPTCHA_SIZE:

                * Optional

                * The size of the widget

                * One of: ("compact", "normal", "invisible")

                * Default: normal

            RECAPTCHA_TYPE:

                * Optional

                * One of: ('image', 'audio')

                * Default: 'image'

            RECAPTCHA_TABINDEX (int):

                * Optional

                * The tabindex of the widget and challenge. 
                
                * If other elements in your page use tabindex, it should be set to make user navigation easier.

                * Default: 0

            RECAPTCHA_CALLBACK (str):

                * Optional

                * The name of your callback function, executed when the user submits a successful response.

                * The **g-recaptcha-response** token is passed to your callback.

            RECAPTCHA_EXPIRED_CALLBACK (str):

                * Opional

                * The name of your callback function, executed when the reCAPTCHA response expires and the user needs to re-verify.

            RECAPTCHA_ERROR_CALLBACK (str):

                * Optional

                * The name of your callback function, executed when reCAPTCHA encounters an error 
                (usually network connectivity) and cannot continue until connectivity is restored.

                * If you specify a function here, you are responsible for informing the user that they should retry.

            RECAPTCHA_JS_ONLY (bool):

                * Default False

                * You might need this if you only want to use Recaptcha's JS script (Recaptcha V3)
    '''

    widget = recaptcha_widget
            
    def __init__(self, label='Recaptcha', extra_validators: list=None, **kwargs):
        validators = set([recaptcha_validator])
        if isinstance(extra_validators, (list, set, tuple)):
            validators.update(extra_validators)
        self._config_prefix = kwargs.pop('config_prefix', None) or 'RECAPTCHA'
        super(RecaptchaField, self).__init__(label, list(validators), **kwargs)

    def _get_app(self, app):
        self._config = app.config
