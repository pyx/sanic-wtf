# -*- coding: utf-8 -*-
from sanic import Sanic

from sanic_wtf import SanicWTF


# NOTE
# put this test in a separate file as the test_client will be stopped
# abnormally by uncaught exception, the port will not be released, other tests
# will fail with:
# OSError: [Errno 98] error while attempting to bind on address ('127.0.0.1',
# 42101): address already in use
def test_secret_key_required():
    app = Sanic('test')
    assert app.config.get('SECRET_KEY') is None
    assert app.config.get('WTF_CSRF_SECRET_KEY') is None

    wtf = SanicWTF(app)

    # setup mock up session for testing
    session = {}
    wtf.get_csrf_context = lambda _: session

    req, resp = app.test_client.get('/')
    # the server was stopped by uncaught exception ValueError: no secret key
    assert resp is None
