import re
import asyncio

from sanic import response
from wtforms.validators import DataRequired, Length, ValidationError
from wtforms import FileField, StringField, SubmitField

from sanic_wtf import SanicForm, to_bytes
from .helpers import render_form, csrf_token_pattern


def test_async_validators_with_csrf(
    app,
    async_validator_conditionally_fail
):
    app.config['WTF_CSRF_SECRET_KEY'] = 'top secret !!!'

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[
            DataRequired(),
            Length(max=10),
            async_validator_conditionally_fail
        ])
        submit = SubmitField('Submit')

    @app.route('/', methods=['POST'])
    async def index(request):
        form = TestForm(request)
        if not await form.validate_on_submit_async():
            return response.text(
                str(form.errors)
            )
        else:
            return response.text('valid')

    @app.route('/', methods=['GET'])
    async def index_(request):
        form = TestForm(request)
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
    assert 'valid' in resp.text

def test_two_async_validators(
    app,
    async_validator_conditionally_fail,
    async_validator_always_pass
):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[
            DataRequired(),
            Length(max=10),
            async_validator_conditionally_fail,
            async_validator_always_pass
        ])
        submit = SubmitField('Submit')

    @app.route('/', methods=['POST'])
    async def index(request):
        form = TestForm(request)
        if not await form.validate_on_submit_async():
            return response.text('invalid')
        else:
            return response.text('valid')

    @app.route('/', methods=['GET'])
    async def index_(request):
        form = TestForm(request)
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200

    payload = {'msg': 'fail'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'invalid' in resp.text

    payload = {'msg': 'pass'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'valid' in resp.text

def test_async_with_sync_validators_fail(
    app,
    async_validator_conditionally_fail,
    async_validator_always_pass,
    sync_validator_always_fail
):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[
            DataRequired(),
            Length(max=10),
            async_validator_conditionally_fail,
            async_validator_always_pass,
            sync_validator_always_fail
        ])
        submit = SubmitField('Submit')

    @app.route('/', methods=['POST'])
    async def index(request):
        form = TestForm(request)
        if not await form.validate_on_submit_async():
            return response.text('invalid')
        else:
            return response.text('valid')

    @app.route('/', methods=['GET'])
    async def index_(request):
        form = TestForm(request)
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200

    payload = {'msg': 'fail'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'invalid' in resp.text

    payload = {'msg': 'pass'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'invalid' in resp.text

def test_async_with_sync_validators_conditionally_fail(
    app,
    async_validator_conditionally_fail,
    async_validator_always_pass,
    sync_validator_conditionally_fail
):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[
            DataRequired(),
            Length(max=10),
            async_validator_conditionally_fail,
            async_validator_always_pass,
            sync_validator_conditionally_fail
        ])
        submit = SubmitField('Submit')

    @app.route('/', methods=['POST'])
    async def index(request):
        form = TestForm(request)
        if not await form.validate_on_submit_async():
            return response.text('invalid')
        else:
            return response.text('valid')

    @app.route('/', methods=['GET'])
    async def index_(request):
        form = TestForm(request)
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200

    payload = {'msg': 'fail'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'invalid' in resp.text

    payload = {'msg': 'pass'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'valid' in resp.text

def test_async_and_sync_stock_validator(
    app,
    async_validator_conditionally_fail,
    async_validator_always_pass
):
    app.config['WTF_CSRF_ENABLED'] = False

    class TestForm(SanicForm):
        msg = StringField('Note', validators=[
            DataRequired(),
            Length(max=2),   # <--
            async_validator_conditionally_fail,
            async_validator_always_pass
        ])
        submit = SubmitField('Submit')

    @app.route('/', methods=['POST'])
    async def index(request):
        form = TestForm(request)
        if not await form.validate_on_submit_async():
            return response.text('invalid')
        else:
            return response.text('valid')

    @app.route('/', methods=['GET'])
    async def index_(request):
        form = TestForm(request)
        content = render_form(form)
        return response.html(content)

    req, resp = app.test_client.get('/')
    assert resp.status == 200

    payload = {'msg': 'fail'}
    req, resp = app.test_client.post('/', data=payload)
    assert resp.status == 200
    assert 'invalid' in resp.text
