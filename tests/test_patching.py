import asyncio

import pytest
from wtforms import Form, Field, FieldList, StringField
from wtforms import validators
from multidict import CIMultiDict

from sanic_wtf import SanicForm
from sanic_wtf._patch import _patch

''' 
Tests:
    Patch fields to make them support async validators
    Patches:

    1. wtforms.Form.validate() --> _wtforms_form_validate
    2. wtforms.BaseForm.validate() --> _wtforms_base_form_validate
    3. fields and field lists
    3.1 wtforms.fields.core.Field
    3.1.1. wtforms.fields.core.Field.validate() --> _field_validate
    3.1.2. wtforms.fields.core.Field._run_validation_chain() --> _run_validation_chain_async 
    TODO: 3.2 wtforms.fields.core.FieldList
'''

# Form validate is async
def test_Form_validate_is_patched():
    class _Form(SanicForm):
        string = StringField('asdsad', [validators.input_required()])

        def __init__(self, *args, **kwargs):
            self.patched = False
            super().__init__(*args, **kwargs)

    form = _Form()
    _patch(form)
    assert asyncio.iscoroutinefunction(form.validate)

# BaseForm validate is async
def test_BaseForm_validate_is_patched():
    class _Form(SanicForm):
        
        string = StringField('asdasd',[validators.input_required()])

        def __init__(self, *args, **kwargs):
            self.patched = False
            super().__init__(*args, **kwargs)

    form = _Form()
    assert hasattr(form, 'validate_base') is False
    _patch(form)
    assert asyncio.iscoroutinefunction(form.validate_base)

# test validate methods
def test_all_fields_have_async_validate_method():

    async def async_val(form, field):
        pass

    class _Form(SanicForm):
        sync_field = StringField('sync_field', [validators.input_required()])
        async_field = StringField('async_field', [async_val])
        mix_field = StringField('mix_field', [async_val, validators.input_required()])

        def __init__(self, *args, **kwargs):
            self.patched = False
            super().__init__(*args, **kwargs)

    form = _Form()
    for _, field in form._fields.items():
        if hasattr(field, 'validate'):
            assert asyncio.iscoroutinefunction(
                field.validate
            ) is False
    _patch(form)
    for _, field in form._fields.items():
        if hasattr(field, 'validate'):
            assert asyncio.iscoroutinefunction(
                field.validate
            ) is True

# Pre/Post Validators

class AsyncValidatorFound(Exception):
    pass

@pytest.fixture
def req():
    class App:
        pass
    class Request:
        def __init__(self):
            self.app = App()
            self.app.config = {'WTF_CSRF_ENABLED': False}
            self.files = None
    req_ = Request()
    req_.method = 'POST'
    return req_


@pytest.mark.asyncio
async def test_post_validator_field_patch(req):
    POST_VAL_ERR_MSG = 'post_patched_and_called'
    class AsyncPostValidatorField(StringField):
        async def post_validate(self, form, stop_validation):
            raise AsyncValidatorFound(POST_VAL_ERR_MSG)

    class _Form(SanicForm):
        string = AsyncPostValidatorField('asdasd', [validators.input_required()])

    req.form = CIMultiDict(dict(string='asdasdsda'))
    form = _Form(
        req
    )
    with pytest.raises(AsyncValidatorFound) as e:
        await form.validate_on_submit_async()
        assert POST_VAL_ERR_MSG in str(e)
    
@pytest.mark.asyncio
async def test_post_validator_field_sync(req):
    POST_VAL_ERR_MSG = 'post_patched_and_called'
    class AsyncPostValidatorField(StringField):
        def post_validate(self, form, stop_validation):
            raise AsyncValidatorFound(POST_VAL_ERR_MSG)

    class _Form(SanicForm):
        string = AsyncPostValidatorField('asdasd', [validators.input_required()])

    req.form = CIMultiDict(dict(string='asdasdsda'))
    form = _Form(
        req
    )
    with pytest.raises(AsyncValidatorFound) as e:
        await form.validate_on_submit_async()
        assert POST_VAL_ERR_MSG in str(e)

@pytest.mark.asyncio
async def test_post_validator_field_async_passes(req):
    class AsyncPostValidatorField(StringField):
        async def post_validate(self, form, stop_validation):
            pass

    class _Form(SanicForm):
        string = AsyncPostValidatorField('asdasd', [validators.input_required()])

    req.form = CIMultiDict(dict(string='asdasdsda'))
    form = _Form(
        req
    )
    assert await form.validate_on_submit_async()

@pytest.mark.asyncio
async def test_post_validator_field_async_fails(req):
    class AsyncPostValidatorField(StringField):
        async def post_validate(self, form, stop_validation):
            pass

    async def fail(*args):
        raise ValueError('I failed')

    class _Form(SanicForm):
        string = AsyncPostValidatorField('asdasd', [validators.input_required(), fail])

    req.form = CIMultiDict(dict(string='asdasdsda'))
    form = _Form(
        req
    )

    assert await form.validate_on_submit_async() is False
    assert 'I failed' in str(form.errors)

@pytest.mark.asyncio
async def test_post_validator_field_async_fails_with_post_validator(req):
    class AsyncPostValidatorField(StringField):
        async def post_validate(self, form, stop_validation):
            raise ValueError('I failed again')

    async def fail(*args):
        raise ValueError('I failed')

    class _Form(SanicForm):
        string = AsyncPostValidatorField('asdasd', [validators.input_required(), fail])

    req.form = CIMultiDict(dict(string='asdasdsda'))
    form = _Form(
        req
    )

    assert await form.validate_on_submit_async() is False
    assert 'I failed' in str(form.errors)
    assert 'I failed again' in str(form.errors)
  