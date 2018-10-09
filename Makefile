SHELL := /bin/sh

# SET THIS! Directory containing wsgi.py
PROJECT := demo

LOCALPATH := $(CURDIR)/src
PYTHONPATH := $(LOCALPATH)
SETTINGS := production
DJANGO_SETTINGS_MODULE = $(PROJECT).settings.$(SETTINGS)
DJANGO_POSTFIX := --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=.$(PYTHONPATH)
LOCAL_SETTINGS := development
DJANGO_LOCAL_SETTINGS_MODULE = $(PROJECT).settings.$(LOCAL_SETTINGS)
DJANGO_LOCAL_POSTFIX := --settings=$(DJANGO_LOCAL_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
TEST_SETTINGS := test
DJANGO_TEST_SETTINGS_MODULE = $(PROJECT).settings.$(TEST_SETTINGS)
DJANGO_POSTFIX := --settings=$(DJANGO_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
DJANGO_TEST_POSTFIX := --settings=$(DJANGO_TEST_SETTINGS_MODULE) --pythonpath=$(PYTHONPATH)
PYTHON_BIN := $(VIRTUAL_ENV)/bin

.PHONY: all bootstrap clean collectstatic compare coverage demo load_demo_fixtures pip predeploy refresh rsync runserver_unsafe sdist showenv showenv.all showenv.site showenv.virtualenv test upload virtualenv virtual_env_set

.DEFAULT: virtual_env_set
	$(PYTHON_BIN)/django-admin.py $@ $(FLAGS) $(DJANGO_POSTFIX)

showenv:
	@echo 'Environment:'
	@echo '-----------------------'
	@$(PYTHON_BIN)/python -c "import sys; print 'sys.path:', sys.path"
	@echo 'PYTHONPATH:' $(PYTHONPATH)
	@echo 'PROJECT:' $(PROJECT)
	@echo 'DJANGO_SETTINGS_MODULE:' $(DJANGO_SETTINGS_MODULE)
	@echo 'DJANGO_LOCAL_SETTINGS_MODULE:' $(DJANGO_LOCAL_SETTINGS_MODULE)
	@echo 'DJANGO_TEST_SETTINGS_MODULE:' $(DJANGO_TEST_SETTINGS_MODULE)

showenv.all: showenv showenv.virtualenv showenv.site

showenv.virtualenv: virtual_env_set
	PATH := $(VIRTUAL_ENV)/bin:$(PATH)
	export $(PATH)
	@echo 'VIRTUAL_ENV:' $(VIRTUAL_ENV)
	@echo 'PATH:' $(PATH)

showenv.site: site_set
	@echo 'SITE:' $(SITE)

collectstatic: virtual_env_set
	-mkdir -p .$(LOCALPATH)/static
	$(PYTHON_BIN)/django-admin.py collectstatic -c --noinput $(DJANGO_POSTFIX)

refresh:
	touch $(PYTHONPATH)/$(PROJECT)/wsgi.py

rsync:
	rsync -avz --checksum --exclude-from .gitignore --exclude-from .rsyncignore . $(REMOTE_URI)

compare:
	rsync -avz --checksum --dry-run --exclude-from .gitignore --exclude-from .rsyncignore . $(REMOTE_URI)

clean:
	find . -name "*.pyc" -print0 | xargs -0 rm -rf
	find . -name "*.egg-info" -print0 | xargs -0 rm -rf
	-rm -rf demo.sqlite
	-rm -rf htmlcov
	-rm -rf .coverage
	-rm -rf build
	-rm -rf dist
	-rm -rf docs/_build

test: clean
	django-admin.py test $(APP) $(DJANGO_TEST_POSTFIX)

coverage: virtual_env_set
	$(PYTHON_BIN)/coverage run --source="$(PYTHONPATH)/" $(PYTHON_BIN)/django-admin.py test $(APP) $(DJANGO_TEST_POSTFIX)
	$(PYTHON_BIN)/coverage html --include="$(LOCALPATH)/*" --omit="*/admin.py,*/test*"

predeploy: test

sdist: virtual_env_set
	python setup.py sdist

upload: virtual_env_set
	python setup.py sdist upload
	make clean

bootstrap: virtualenv pip virtual_env_set

pip: requirements/$(SETTINGS).txt virtual_env_set
	pip install -r requirements/$(SETTINGS).txt

virtualenv:
	virtualenv --no-site-packages $(VIRTUAL_ENV)
	echo $(VIRTUAL_ENV)

load_demo_fixtures:
	$(PYTHON_BIN)/django-admin.py loaddata $(PYTHONPATH)/$(PROJECT)/fixtures/example.json $(DJANGO_POSTFIX)

demodatabase: clean virtual_env_set
	$(PYTHON_BIN)/django-admin.py migrate $(DJANGO_POSTFIX)

resetdemodatabase: demodatabase load_demo_fixtures

demo: virtual_env_set pip resetdemodatabase runserver_unsafe

runserver_unsafe:
	$(PYTHON_BIN)/django-admin.py runserver --insecure $(DJANGO_LOCAL_POSTFIX)

all: collectstatic refresh

