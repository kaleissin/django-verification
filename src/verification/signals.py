from __future__ import unicode_literals

import django.dispatch

__all__ = ['key_claimed']

# provides args "claimant", "group"
key_claimed = django.dispatch.Signal()
