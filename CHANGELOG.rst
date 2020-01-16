Changelog
=========

Release 1.1.0
-------------

Adds support for Django 2.2.

Release 1.0.0
-------------

Drops support for Python 2 and Django < 1.11.

Adds support for Django 2.0 and 2.1.

Shims have not been removed, but if this works on Python 2.7 or
Django < 1.11 it is considered a bug, not a feature.

Release 0.5.2
-------------

Final release with support for Python 2 and Django < 1.11.

Release 0.5.1
-------------

Adaptations to new pypi and newer setuptools and packaging regime.

The demo should also run on newer Djangos and Py3K now.

Release 0.5
-----------

Drops support for Django 1.7.

Needs Django 1.8 or newer, up to Django 1.11. Works on both Python
2.7, 3.5 and 3.6.

Release 0.4
-----------

Works with, and needs, Django 1.7+.

Changes:

- KeyManager is generated from the queryset as per Django 1.7 now. This
  also shuts up the warning "RemovedInDjango18Warning:
  `KeyManager.get_query_set` method should be renamed `get_queryset`."
- Migrations are supported.
- Supports the new application-definition of Django 1.7, meaning
  multiple copies and renames of an app is possible.

Renames/moves:

- KeyGroup.key_set -> KeyGroup.keys

Bugfix 0.3.1
------------

UsernameKeyGenerator now actually works.

Release 0.3
-----------

Even bigger class hierarchy. ClaimContextMixin inherits from the new mixin,
ArgLookupMixin, so nothing should break.

Renames/moves:

- ClaimContextMixin.get_key_arg() -> ArgLookupMixin.get_key_arg()
- ClaimContextMixin.get_group_arg() -> ArgLookupMixin.get_group_arg()

Release 0.2
-----------

New feature that ought to have been included from the start: Activating a Key
through inputting the key into a form, with no magic in the link structure.
This necessitated a refactoring of the included views.

Breaking changes
~~~~~~~~~~~~~~~~

If you use ClaimMixin or ClaimContextMixin dirctly, be advised that these have
been extensively refactored. Both now inherit from KeyLookupMixin.

The existing claiming views that were direct children of ClaimContextMixin now
inherit from UrlClaimMixin, which combines ClaimMixin and ClaimContextMixin.

Renames/moves:

- \*.key -> KeyLookupMixin.key
- ClaimContextMixin.default_group -> KeyLookupMixin.keygroup
- ClaimContextMixin.get_key() -> KeyLookupMixin.get_key_from_string()
- ClaimContextMixin.get_group() -> KeyLookupMixin.get_group_from_string()
- ClaimMixin._claim() -> UrlClaimMixin._claim()

Gone:

- ClaimContextMixin.foo(). Yay!

Other
~~~~~

- Tweaks to the demo templates to make the demo less bug ugly
- Tweaks to the demo views to improve DRY
- A new view, AbstractClaimView, which shows a form that asks for a key and
  then claims that key. This closes issue #1. Thanks, @senbon

