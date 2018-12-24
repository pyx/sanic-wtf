import types
import itertools
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
        # TODO: Should we await this?
        self.pre_validate(form)
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
        # TODO: Should we await this?
        self.post_validate(form, stop_validation)
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
    async def async_validate(validator):
        try:
            await validator(form, self)
        except StopValidation as e:
            if e.args and e.args[0]:
                self.errors.append(e.args[0])
            raise e
        except ValueError as e:  # Catches validation errors
            self.errors.append(e.args[0])

    # Sort validators
    sync_validators = []
    async_validators = []

    for validator in validators:

        # If wrap in a future to execute concurrently
        if asyncio.iscoroutinefunction(validator):
            async_validators.append(
                asyncio.ensure_future(
                    async_validate(
                        validator
                    )
                )
            )
        # Else add to sync validators
        else:
            sync_validators.append(
                validator
            )

    # Run async validations
    if async_validators:
        try:
            await asyncio.gather(*async_validators)
        except StopValidation:
            return True

    # Run sync validators
    for validator in sync_validators:
        try:
            validator(form, self)
        except StopValidation as e:
            if e.args and e.args[0]:
                self.errors.append(e.args[0])
            return True
        except ValueError as e:  # Catches validation errors
            self.errors.append(e.args[0])

    return False

def _patch(self):
    if not self.patched:
        # 1. 
        setattr(
            self,
            'validate',
            types.MethodType(_wtforms_form_validate, self)
        )
        # 2. 
        setattr(
            self,
            'validate_base',
            types.MethodType(_wtforms_base_form_validate, self)
        )
        # 3. 
        for field_name, field in self._fields.items():
            # TODO: Patch FieldList
            if not isinstance(field, FieldList) and isinstance(field, Field):
                if hasattr(field, 'validate'):
                    setattr(
                        self._fields[field_name],
                        'validate',
                        types.MethodType(_field_validate, self._fields[field_name])
                    )
            # 4.
                if hasattr(field, '_run_validation_chain'):
                    setattr(
                        self._fields[field_name],
                        '_run_validation_chain',
                        types.MethodType(_run_validation_chain_async, self._fields[field_name])
                    )
        self.patched = True

def patch(f):
    ''' Patch fields to make them support async validators
    Patches:

    1. wtform.Form.validate() --> _wtforms_form_validate
    2. wtform.BaseForm.validate() --> _wtforms_base_form_validate
    3. wtform.fields.core.Field.validate() --> _field_validate
    4. wtform.fields.core.Field._run_validation_chain() --> _run_validation_chain_async
    
     '''
    async def a_wrapper(self, *args, **kwargs):
        _patch(self)
        return await f(self, *args, **kwargs)
    return a_wrapper
