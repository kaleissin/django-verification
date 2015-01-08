#!/usr/bin/env python

from __future__ import unicode_literals

import os
import sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'verification.tests.settings'
sys.path.append('./src')

from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    try: # Django 1.7+
        from django import setup
        setup()
    except ImportError:
        pass
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["verification"])
    sys.exit(bool(failures))
