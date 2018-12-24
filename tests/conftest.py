# -*- coding: utf-8 -*-
import pytest
import asyncio

from sanic import Sanic
from wtforms.validators import ValidationError


SLEEP_DURATION = 0.01

@pytest.fixture(scope='function')
def app():
    test_app = Sanic('test_app')
    session = {}

    @test_app.middleware('request')
    async def add_session(request):
        name = request.app.config.get('WTF_CSRF_CONTEXT_NAME', 'session')
        request[name] = session

    return test_app

@pytest.fixture(scope='function')
def async_validator_conditionally_fail():
    async def async_validator(form, field):
        await asyncio.sleep(SLEEP_DURATION)
        if form.msg.data == 'fail':
            raise ValidationError('Invalid')
        else:
            pass

    return async_validator

@pytest.fixture(scope='function')
def async_validator_always_pass():
    async def async_validator(form, field):
        await asyncio.sleep(SLEEP_DURATION)
    return async_validator