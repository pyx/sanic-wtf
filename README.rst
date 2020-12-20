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

  pip install --upgrade Sanic-WTF


How to use it
-------------


Intialization (of Sanic)
^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

  from sanic import Sanic

  app = Sanic(__name__)

  # either WTF_CSRF_SECRET_KEY or SECRET_KEY should be set
  app.config['WTF_CSRF_SECRET_KEY'] = 'top secret!'

  @app.middleware('request')
  async def add_session_to_request(request):
      # setup session


Defining Forms
^^^^^^^^^^^^^^

.. code-block:: python

  from sanic_wtf import SanicForm
  from wtforms import PasswordField, StringField, SubmitField
  from wtforms.validators import DataRequired

  class LoginForm(SanicForm):
      name = StringField('Name', validators=[DataRequired()])
      password = PasswordField('Password', validators=[DataRequired()])
      submit = SubmitField('Sign In')

That's it, just subclass `SanicForm` and later on passing in the current
`request` object when you instantiate the form class.  Sanic-WTF will do the
trick.


Form Validation
^^^^^^^^^^^^^^^

.. code-block:: python

  from sanic import response

  @app.route('/', methods=['GET', 'POST'])
  async def index(request):
      form = LoginForm(request)
      if request.method == 'POST' and form.validate():
          name = form.name.data
          password = form.password.data
          # check user password, log in user, etc.
          return response.redirect('/profile')
      # here, render_template is a function that render template with context
      return response.html(await render_template('index.html', form=form))


.. note::
  For WTForms users: please note that `SanicForm` requires the whole `request`
  object instead of some sort of `MultiDict`.


For more details, please see documentation.


License
=======

BSD New, see LICENSE for details.


Links
=====

- `Documentation <http://sanic-wtf.readthedocs.org/>`_

- `Issue Tracker <https://github.com/pyx/sanic-wtf/issues/>`_

- `Source Package @ PyPI <https://pypi.python.org/pypi/sanic-wtf/>`_

- `Git Repository @ Github
  <https://github.com/pyx/sanic-wtf/>`_

- `Git Repository @ Gitlab
  <https://gitlab.com/pyx/sanic-wtf/>`_

- `Development Version
  <http://github.com/pyx/sanic-wtf/zipball/master#egg=sanic-wtf-dev>`_
