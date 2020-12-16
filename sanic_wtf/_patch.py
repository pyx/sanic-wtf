import types
import inspect
import itertools
import functools
import asyncio
import warnings
from wtforms import Form
from wtforms.validators import StopValidation
from wtforms.fields.core import Field, FieldList


async def _wtforms_form_validate(self):
    """
    Validates the form by calling `validate` on each field, passing any
    extra `Form.validate_<fieldname>` validators to the field validator.
    """
    extra = {}
    for name in self._fields:
        inline = getattr(self.__class__, "validate_%s" % name, None)
        if inline is not None:
            extra[name] = [inline]

    # Added an await here
    return await self.validate_base(extra)

async def _wtforms_base_form_validate(self, extra_validators=None):
    """
    Validates the form by calling `validate` on each field.

    :param extra_validators:
        If provided, is a dict mapping field names to a sequence of
        callables which will be passed as extra validators to the field's
        `validate` method.

    Returns `True` if no errors occur.
    """
    self._errors = None
    success = True
    for name, field in self._fields.items():
        if extra_validators is not None and name in extra_validators:
            extra = extra_validators[name]
        else:
            extra = tuple()
        # Added an await here
        if not await field.validate(self, extra):
            success = False
    return success


async def _field_validate(self, form, extra_validators=()):
    """
    Validates the field and returns True or False. `self.errors` will
    contain any errors raised during validation. This is usually only
    called by `Form.validate`.

    Subfields shouldn't override this, but rather override either
    `pre_validate`, `post_validate` or both, depending on needs.

    :param form: The form the field belongs to.
    :param extra_validators: A sequence of extra validators to run.
    """
    self.errors = list(self.process_errors)
    stop_validation = False


    # Call pre_validate
    try:
        # Await if a coroutine
        res = self.pre_validate(form)
        if inspect.isawaitable(res):
            res = await(res)
    except StopValidation as e:
        if e.args and e.args[0]:
            self.errors.append(e.args[0])
        stop_validation = True
    except ValueError as e:
        self.errors.append(e.args[0])

    # Run validators
    if not stop_validation:
        chain = itertools.chain(self.validators, extra_validators)
        stop_validation = await self._run_validation_chain(form, chain)

    # Call post_validate
    try:
        # Await if a coroutine
        res = self.post_validate(form, stop_validation)
        if inspect.isawaitable(res):
            await res
    except ValueError as e:
        self.errors.append(e.args[0])

    return len(self.errors) == 0

async def _run_validation_chain_async(self, form, validators):
    """
    Run a validation chain, stopping if any validator raises StopValidation.

    :param form: The Form instance this field belongs to.
    :param validators: a sequence or iterable of validator callables.
    :return: True if validation was stopped, False otherwise.
    """

    for validator in validators:
        # If async 
        try:
            res = validator(form, self)
            if inspect.isawaitable(res):
                await res
        except StopValidation as e:
            if e.args and e.args[0]:
                self.errors.append(e.args[0])
            return True
        except ValueError as e:  # Catches validation errors
            self.errors.append(e.args[0])
    return False    

def _patch(self):
    if not self.patched:
        # 1. Patch Form.validate
        setattr(
            self,
            'validate',
            types.MethodType(_wtforms_form_validate, self)
        )
        # 2. Patch BaseForm.validate
        # NOTE: Form.validate will now call validate_base() instead of calling super().validate()
        setattr(
            self,
            'validate_base',
            types.MethodType(_wtforms_base_form_validate, self)
        )
        # 3. Patch each field in a form
        for field_name, field in self._fields.items():
            # 3.1 Patch field type
            if not isinstance(field, FieldList) and isinstance(field, Field):
                # 3.1.1 Patch field.validate
                if hasattr(field, 'validate'):
                    setattr(
                        self._fields[field_name],
                        'validate',
                        types.MethodType(
                            # Else, Attach this method
                            _field_validate,
                            self._fields[field_name]
                        )
                    )
                # 3.1.2 Patch field._run_validation_chain
                if hasattr(field, '_run_validation_chain'):
                    setattr(
                        self._fields[field_name],
                        '_run_validation_chain',
                        types.MethodType(_run_validation_chain_async, self._fields[field_name])
                    )
            # # 3.2 Patch fieldlist type
            # # Won't work asynchronously until "entries" (subfields) are dealt with
        self.patched = True

def patch(f):
    ''' Patch wtforms to make it support async validators
    Patches:

    1. wtforms.Form.validate() --> _wtforms_form_validate
    2. wtforms.BaseForm.validate() --> _wtforms_base_form_validate
    3.1 wtforms.fields.core.Field
    3.1.1. wtforms.fields.core.Field.validate() --> _field_validate
    3.1.2. wtforms.fields.core.Field._run_validation_chain() --> _run_validation_chain_async
    TODO: 3.2 wtforms.fields.core.FieldList
    TODO: Look into wtforms.fields.process
    '''
    @functools.wraps(f)
    async def wrapper(self, *args, **kwargs):
        _patch(self)
        return await f(self, *args, **kwargs)
    return wrapper
