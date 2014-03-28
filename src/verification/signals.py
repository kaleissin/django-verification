from __future__ import unicode_literals

import django.dispatch

__all__ = ['key_claimed']

key_claimed = django.dispatch.Signal(providing_args=["claimant", "group"])
