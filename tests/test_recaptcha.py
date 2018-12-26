import asyncio

import pytest
from wtforms import ValidationError
import multidict

from sanic_wtf import SanicForm, RecaptchaField


def get_req_with_config(config):
    class Request:
        def __init__(self, app):
            self.app = app
            self.files = None
            self.form = multidict.CIMultiDict()
            self.json = multidict.CIMultiDict()
            self.method = 'POST' 
    
    class App:
        def __init__(self, config):
            self.config = config


    _base_config = {'WTF_CSRF_ENABLED': False}
    test_app = App({**_base_config, **config})
    return Request(test_app)

def test_recaptcha_validator_is_coro():

    class TestForm(SanicForm):
        recapfield = RecaptchaField('recapt')

    test_req = get_req_with_config(
        {'RECAPTCHA_PUBLIC_KEY': 'pubkey', 'RECAPTCHA_PRIVATE_KEY': 'privkey'}
    )
    testf = TestForm(test_req)

    assert asyncio.iscoroutinefunction(
        testf._fields['recapfield'].validators[0]
    )

def test_widget_renders():

    class TestForm(SanicForm):
        recapfield = RecaptchaField('recapt')

    test_req = get_req_with_config(
        {'RECAPTCHA_PUBLIC_KEY': 'pubkey', 'RECAPTCHA_PRIVATE_KEY': 'privkey'}
    )
    testf = TestForm(test_req)

    assert 'pubkey' in testf.recapfield()
    assert '<div' in testf.recapfield()
    assert '<script' in testf.recapfield()
    assert isinstance(testf.recapfield(), str)

@pytest.mark.asyncio
async def test_validator_awaitable():
    class TestForm(SanicForm):
        recapfield = RecaptchaField('recapt')

    test_req = get_req_with_config(
        {'RECAPTCHA_PUBLIC_KEY': 'pubkey', 'RECAPTCHA_PRIVATE_KEY': 'privkey'}
    )
    testf = TestForm(test_req)

    assert await testf.validate_on_submit_async() is False
    assert 'The response parameter is missing.' in str(testf.errors)

@pytest.mark.asyncio
async def test_validator_skips_when_tesing():
    class TestForm(SanicForm):
        recapfield = RecaptchaField('recapt')

    test_req = get_req_with_config(
        {'RECAPTCHA_PUBLIC_KEY': 'pubkey', 'RECAPTCHA_PRIVATE_KEY': 'privkey', 'TESTING': True}
    )
    testf = TestForm(test_req)

    assert await testf.validate_on_submit_async() is True
    assert not testf.errors


@pytest.mark.asyncio
async def test_validator_is_called():
    class TestForm(SanicForm):
        recapfield = RecaptchaField('recapt')

    test_req = get_req_with_config(
        {'RECAPTCHA_PUBLIC_KEY': 'pubkey', 'RECAPTCHA_PRIVATE_KEY': 'privkey', 'TESTING': True}
    )
    testf = TestForm(test_req)

    passed = False

    async def fake_val(form, field, **kwargs):
        nonlocal passed
        await asyncio.sleep(0.01)
        passed = True


    testf._fields.get('recapfield').validators[0] = fake_val
    testf.request.form['g-recaptcha-response'] = 'must exist'

    res = await testf.validate_on_submit_async()
    assert passed is True
    assert res is True
