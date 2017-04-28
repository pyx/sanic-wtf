.. include:: ../README.rst


Prerequisites
=============

To enable CSRF protection, a session is required, Sanic-WTF expects
:code:`request['session']` is available in this case.  For a simple client side
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
================================ =============================================


API
===

.. automodule:: sanic_wtf
  :members:


Full Example
============

.. literalinclude:: ../examples/guestbook.py


Changelog
=========

- 0.1.0

  Made :attr:`SanicWTF.Form` always available so that one can create the form
  classes before calling :meth:`SanicWTF.init_app`

- 0.1.0

  First public release.


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
