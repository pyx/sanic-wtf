# -*- coding: utf-8 -*-
from collections import namedtuple
from wtforms import FileField
from sanic_wtf import FileAllowed, FileRequired, SanicForm


class FileUploadForm(SanicForm):
    required = FileField('Required File', validators=[FileRequired()])


class ImageUploadForm(SanicForm):
    image = FileField(
        'Image', validators=[FileAllowed('png JpG .jpeg'.split())])


# compatible Sanic File object as of v 0.5.4
File = namedtuple('File', 'type body name')


def test_file_required():
    data = {'required': File(type='', body=b'', name='')}
    form = FileUploadForm(data=data)
    assert not form.validate()

    data = {'required': File(type='', body=b'', name='fake-file.lol')}
    form = FileUploadForm(data=data)
    assert form.validate()


def test_file_allowed():
    data = {'image': File(type='', body=b'', name='')}
    form = ImageUploadForm(data=data)
    # okay, because FileAllowed is fine with empty field
    assert form.validate()

    data = {'image': File(type='', body=b'import this', name='left-pad.js')}
    form = ImageUploadForm(data=data)
    assert not form.validate()

    data = {'image': File(type='', body=b'=^o^=', name='sanic.jpg')}
    form = ImageUploadForm(data=data)
    assert form.validate()

    data = {'image': File(type='', body=b'=^o^=', name='sanic.JPEG')}
    form = ImageUploadForm(data=data)
    assert form.validate()

    data = {'image': File(type='', body=b'=^o^=', name='sanic.exe.png')}
    form = ImageUploadForm(data=data)
    assert form.validate()

    data = {'image': File(type='', body=b'=^o^=', name='sanic.png.exe')}
    form = ImageUploadForm(data=data)
    assert not form.validate()

    # just for the record... not that this is a good idea
    data = {'image': File(type='', body=b'=^o^=', name='.png')}
    form = ImageUploadForm(data=data)
    assert form.validate()


def test_empty_file():
    form = ImageUploadForm(data={})
    assert form.validate()

    # NOTE: this is a reminder, being validated dose not mean file exists
    assert not form.image.data
