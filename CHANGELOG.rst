Changelog
=========

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

