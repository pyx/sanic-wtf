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

- 0.6.0

  **backward incompatible upgrade**

  Supporting python 3.6, 2.7, 3.8, 3.9, and Sanic 20.3.0

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
