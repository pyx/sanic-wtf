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

.. code-block:: python

  from sanic import Sanic
  from sanic_wtf import SanicWTF
  from wtforms import PasswordField, StringField, SubmitField
  from wtforms.validators import DataRequired


  app = Sanic(__name__)
  wtf = SanicWTF(app)


  class LoginForm(wtf.Form):
      name = StringField('Name', validators=[DataRequired()])
      password = PasswordField('Password', validators=[DataRequired()])
      submit = SubmitField('Sign In')


  @app.route('/', methods=['GET', 'POST'])
  def index(request):
      form = LoginForm(request.form):
      if request.method == 'POST' and form.validate():
          name = form.name.data
          password = form.password.data
          # check user password, log in user, etc.
          return response.redirect('/profile')
      return response.html('index.html', form=form)

  if __name__ == '__main__':
      app.run(debug=True)


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
