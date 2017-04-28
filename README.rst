===============================
Sanic-WTF - Sanic meets WTForms
===============================

Sanic-WTF makes using `WTForms` with `Sanic`_ and CSRF (Cross-Site Request
Forgery) protection a little bit easier.


.. _WTForms: https://github.com/wtforms/wtforms
.. _Sanic: https://github.com/channelcat/sanic


Quick Start
===========


Installation
------------

.. code-block:: sh

  pip install Sanic-WTF


How to use it
-------------

Intialization
^^^^^^^^^^^^^

.. code-block:: python

  from sanic import Sanic, response
  from sanic_wtf import SanicWTF
  from wtforms import PasswordField, StringField, SubmitField
  from wtforms.validators import DataRequired
  from some_session_package import session_middleware

  app = Sanic(__name__)

  # either WTF_CSRF_SECRET_KEY or SECRET_KEY should be set
  app.config['WTF_CSRF_SECRET_KEY'] = 'top secret!'

  @app.middleware('request')
  async def add_session_to_request(request):
      ...

  # then register SanicWTF
  wtf = SanicWTF(app)

.. note::

  Since SanicWTF needs 'session' in request, please make sure the 'session'
  exists before SanicWTF's middleware gets run, that usually means register
  whatever session middleware before register SanicWTF's by calling
  :code:`init_app`.


Defining Forms
^^^^^^^^^^^^^^

.. code-block:: python

  class LoginForm(wtf.Form):
      name = StringField('Name', validators=[DataRequired()])
      password = PasswordField('Password', validators=[DataRequired()])
      submit = SubmitField('Sign In')


Form Validation
^^^^^^^^^^^^^^^

.. code-block:: python

  @app.route('/', methods=['GET', 'POST'])
  def index(request):
      form = LoginForm(request.form)
      if request.method == 'POST' and form.validate():
          name = form.name.data
          password = form.password.data
          # check user password, log in user, etc.
          return response.redirect('/profile')
      return response.html('index.html', form=form)


For more details, please see documentation.


License
=======

BSD New, see LICENSE for details.


Links
=====

- `Documentation <http://sanic-wtf.readthedocs.org/>`_

- `Issue Tracker <https://github.com/pyx/sanic-wtf/issues/>`_

- `Source Package @ PyPI <https://pypi.python.org/pypi/sanic-wtf/>`_

- `Mercurial Repository @ bitbucket
  <https://bitbucket.org/pyx/sanic-wtf/>`_

- `Git Repository @ Github
  <https://github.com/pyx/sanic-wtf/>`_

- `Git Repository @ Gitlab
  <https://gitlab.com/pyx/sanic-wtf/>`_

- `Development Version
  <http://github.com/pyx/sanic-wtf/zipball/master#egg=sanic-wtf-dev>`_
