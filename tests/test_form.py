# -*- coding: utf-8 -*-
import re
import os.path

from sanic import response
from wtforms.validators import DataRequired, Length
from wtforms import FileField, StringField, SubmitField

from sanic_wtf import SanicForm, to_bytes


# NOTE
# taking shortcut here, assuming there will be only one "string" (the token)
# ever longer than 40.
csrf_token_pattern = '''value="([0-9a-f#]{40,})"'''


def render_form(form, multipart=False):
    if multipart is True:
        multipart = ' enctype="multipart/form-data"'
    return """
    <form action="" method="POST"{}>
    {}
    </form>""".format(multipart, ''.join(str(field) for field in form))


def test_form_validation(app):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[DataRequired(), Length(max=10)])
        submit = SubmitField('Submit')

    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        form = TestForm(request)
        if request.method == 'POST' and form.validate():
            return response.text('validated')
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200
    # we disabled it
    assert 'csrf_token' not in resp.text

    # this is longer than 10
    payload = {'msg': 'love is beautiful'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'validated' not in resp.text

    payload = {'msg': 'happy'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'validated' in resp.text


def test_form_csrf_validation(app):
    app.config['WTF_CSRF_SECRET_KEY'] = 'top secret !!!'

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[DataRequired(), Length(max=10)])
        submit = SubmitField('Submit')

    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        form = TestForm(request)
        if request.method == 'POST' and form.validate():
            return response.text('validated')
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200
    assert 'csrf_token' in resp.text
    token = re.findall(csrf_token_pattern, resp.text)[0]
    assert token

    payload = {'msg': 'happy', 'csrf_token': token}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'validated' in resp.text

    payload = {'msg': 'happy'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    # should fail, no CSRF token in payload
    assert 'validated' not in resp.text


def test_secret_key_required(app):
    assert app.config.get('SECRET_KEY') is None
    assert app.config.get('WTF_CSRF_SECRET_KEY') is None

    @app.route('/')
    async def index(request):
        form = SanicForm(request)
        return response.text(form)

    req, resp = app.test_client.get('/', debug=True)
    # the server should render ValueError: no secret key message with 500
    assert resp.status == 500
    assert 'ValueError' in resp.text


def test_csrf_token(app):
    app.config['WTF_CSRF_SECRET_KEY'] = 'top secret !!!'
    app.config['WTF_CSRF_FIELD_NAME'] = 'csrf_token'

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[DataRequired(), Length(max=10)])
        submit = SubmitField('Submit')

    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        form = TestForm(request)
        return response.html(form.csrf_token)

    req, resp = app.test_client.get('/')
    assert resp.status == 200
    assert 'csrf_token' in resp.text
    token = re.findall(csrf_token_pattern, resp.text)[0]
    assert token


def test_no_request_disable_csrf(app):
    app.config['WTF_CSRF_ENABLED'] = True
    app.config['WTF_CSRF_SECRET_KEY'] = 'look ma'

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[DataRequired(), Length(max=10)])
        submit = SubmitField('Submit')

    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        form = TestForm(formdata=request.form)
        if request.method == 'POST' and form.validate():
            return response.text('validated')
        content = render_form(form)
        return response.html(content)

    payload = {'msg': 'happy'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    # should be okay, no request means CSRF was disabled
    assert 'validated' in resp.text


def test_validate_on_submit(app):
    app.config['WTF_CSRF_SECRET_KEY'] = 'top secret !!!'

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[DataRequired(), Length(max=10)])
        submit = SubmitField('Submit')

    @app.route('/', methods=['GET', 'POST'])
    async def index(request):
        form = TestForm(request)
        if form.validate_on_submit():
            return response.text('validated')
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200
    assert 'csrf_token' in resp.text
    token = re.findall(csrf_token_pattern, resp.text)[0]
    assert token

    payload = {'msg': 'happy', 'csrf_token': token}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'validated' in resp.text


def test_file_upload(app):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        upload = FileField('upload file')
        submit = SubmitField('Upload')

    @app.route('/upload', methods=['GET', 'POST'])
    async def upload(request):
        form = TestForm(request)
        if form.validate_on_submit():
            return response.text(form.upload.data.name)
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.post(
        '/upload', files={'upload': open(__file__, 'rb')}, data={})
    assert resp.status == 200
    assert resp.text == os.path.basename(__file__)


def test_to_bytes():
    assert isinstance(to_bytes(bytes()), bytes)
    assert isinstance(to_bytes(str()), bytes)
