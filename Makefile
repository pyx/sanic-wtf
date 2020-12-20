NAME = $(shell python setup.py --name)
FULLNAME = $(shell python setup.py --fullname)
DESCRIPTION = $(shell python setup.py --description)
VERSION = $(shell python setup.py --version)
URL = $(shell python setup.py --url)

DOCS_DIR = docs

help:
	@echo '$(NAME) - $(DESCRIPTION)'
	@echo 'Version: $(VERSION)'
	@echo 'URL: $(URL)'
	@echo
	@echo 'Targets:'
	@echo '  help         : display this help text.'
	@echo '  install      : install package $(NAME).'
	@echo '  test         : run all tests.'
	@echo '  coverage     : analyze test coverage.'
	@echo '  tox          : run all tests with tox.'
	@echo '  docs         : generate documentation files.'
	@echo '  quality      : code quality check.'
	@echo '  clean        : remove files created by other targets.'

.PHONY: install
install:
	pip install --upgrade .

.PHONY: dev-install
dev-install:
	pip install --upgrade -e .[dev]

.PHONY: docs
docs: doc-html doc-pdf

.PHONY: doc-html
doc-html: test
	cd $(DOCS_DIR); $(MAKE) html

.PHONY: doc-pdf
doc-pdf: test
	cd $(DOCS_DIR); $(MAKE) latexpdf

.PHONY: release
release: clean quality tox
	@echo 'Checking release version, abort if attempt to release a dev version.'
	echo '$(VERSION)' | grep -qv dev
	@echo 'Bumping version number to $(VERSION), abort if no pending changes.'
	hg commit -m 'Bumped version number to $(VERSION)'
	@echo "Tagging release version $(VERSION), abort if already exists."
	hg tag $(VERSION)
	@echo "Generating package."
	python setup.py sdist bdist_wheel
	@echo "Uploading to PyPI."
	twine upload --sign dist/*
	@echo "Done."

.PHONY: test
test:
	py.test

.PHONY: coverage
coverage:
	py.test --cov sanic_wtf --cov-report=html

.PHONY: tox
tox:
	tox

.PHONY: quality
quality:
	flake8 sanic_wtf tests

.PHONY: clean
clean:
	cd $(DOCS_DIR) && $(MAKE) clean
	rm -rf build/ dist/ htmlcov/ *.egg-info MANIFEST $(DOCS_DIR)/conf.pyc *~
	rm -rf sanic_wtf/__pycache__/ tests/__pycache__/ examples/__pycache__/
	rm -rf .tox/ .pytest_cache/
