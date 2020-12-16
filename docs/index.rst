.. include:: ../README.rst


Prerequisites
=============

To enable CSRF protection, a session is required, Sanic-WTF expects
:code:`request.ctx.session` is available in this case.  For a simple client side
only, cookie-based session, similar to Flask's built-in session, you might want
to try `Sanic-CookieSession`_.

.. _Sanic-CookieSession: https://github.com/pyx/sanic-cookiesession


Configuration
=============

CSRF Configs
---------------

================================ =============================================
Option                           Description
================================ =============================================
:code:`WTF_CSRF_ENABLED`         If :code:`True`, CSRF protection is enabled.
                                 Default is :code:`True`
:code:`WTF_CSRF_FIELD_NAME`      The field name used in the form and session
                                 to store the CSRF token. Default is
                                 `csrf_token`
:code:`WTF_CSRF_SECRET_KEY`      :code:`bytes` used for CSRF token generation.
                                 If it is unset, :code:`SECRET_KEY` will be
                                 used instead.  Either one of these have to be
                                 set to enable CSRF protection.
:code:`WTF_CSRF_TIME_LIMIT`      How long CSRF tokens are valid for, in seconds.
                                 Default is `1800`. (Half an hour)
================================ =============================================

Recaptcha Configs
------------------

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

  * Default: 'normal'

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


API
===

.. note::
  For users of versions prior to 0.3.0, there is backward incompatible changes
  in API.  The module-level helper object is not longer required, the new form
  :class:`SanicForm` is smart enough to figure out how to get user defined
  settings.


.. automodule:: sanic_wtf
  :members:


Full Example
============


Guest Book
----------

.. literalinclude:: ../examples/guestbook.py


File Upload
-----------

.. literalinclude:: ../examples/upload.py


Changelog
=========

- 0.5.0

  Added file upload support and filefield validators :class:`FileAllowed` and
  :class:`FileRequired`.

- 0.4.0

  **backward incompatible upgrade**

  Removed property hidden_tag

- 0.3.0

  **backward incompatible upgrade**

  Re-designed the API to fixed #6 - possible race condition. The new API is
  much simplified, easier to use, while still getting things done, and more.

  Added new setting: WTF_CSRF_TIME_LIMIT
  Added new method :meth:`validate_on_submit` in the style of Flask-WTF.

- 0.2.0

  Made :attr:`SanicWTF.Form` always available so that one can create the form
  classes before calling :meth:`SanicWTF.init_app`

- 0.1.0

  First public release.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
