#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Sanic-WTF documentation build configuration file
import os
import sys

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.insert(0, PROJECT_DIR)
import sanic_wtf  # noqa

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
]

source_suffix = '.rst'

master_doc = 'index'

project = u'Sanic-WTF'
copyright = u'2017, Philip Xu'
author = u'Philip Xu and contributors'

release = sanic_wtf.__version__
version = release.rsplit('.', 1)[0]

language = None

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

pygments_style = 'sphinx'

todo_include_todos = False

html_theme = 'alabaster'

html_theme_options = {
    'github_banner': True,
    'github_repo': 'sanic-wtf',
    'github_user': 'pyx',
}

htmlhelp_basename = 'Sanic-WTFdoc'

latex_documents = [
    (master_doc, 'Sanic-WTF.tex', u'Sanic-WTF Documentation',
     u'Philip Xu and contributors', 'manual'),
]

man_pages = [
    (master_doc, 'sanic-wtf', u'Sanic-WTF Documentation',
     [author], 1)
]

texinfo_documents = [
    (master_doc, 'Sanic-WTF', u'Sanic-WTF Documentation',
     author, 'Sanic-WTF', 'One line description of project.',
     'Miscellaneous'),
]
