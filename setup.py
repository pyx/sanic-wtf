# -*- coding: utf-8 -*-
import re
from os import path
from setuptools import find_packages, setup

ROOT_DIR = path.abspath(path.dirname(__file__))

DESCRIPTION = 'Sanic-WTF - Sanic meets WTForms'
LONG_DESCRIPTION = open(path.join(ROOT_DIR, 'README.rst')).read()
VERSION = re.search(
    "__version__ = '([^']+)'",
    open(path.join(ROOT_DIR, 'sanic_wtf', '__init__.py')).read()
).group(1)


setup(
    name='Sanic-WTF',
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    url='https://github.com/pyx/sanic-wtf/',
    author='Philip Xu and contributors',
    author_email='pyx@xrefactor.com',
    license='BSD-New',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    install_requires=[
        'sanic',
        # this lib monkey patches wtforms to add async capabilities.
        # We're hard coding the version here
        # in order to avoid any unexpected changes
        # that might break this lib
        'wtforms==2.2.1',
        'aio-recaptcha>=0.0.8',
        'markupsafe'
    ],
    extras_require={
        'dev': [
            'aiohttp',
            'flake8',
            'pytest',
            'pytest-cov',
            'pytest-asyncio',
            'Sphinx',
            'tox',
            'twine',
        ],
    },
    zip_safe=False,
    platforms='any',
)
