===================
django-verification
===================

Generalized app for two-step verification.

Installation
============

1. Install the library, for instance with pip::

    pip install django-verification

2. Add the library to your INSTALLED_APPS of an exiting project::

    INSTALLED_APPS += ['verification']

3. Add the tables to the existing project.

   Prior to django 1.7::

        $ ./manage.py syncdb

Demo
====

Copy the entire django-verification directory somewhere, set up and enter a
virtualenv, then provided you are on some Un*x::

    make demo

This'll automatically make a user "admin" with the password "demo".

The demo should now be running on http://127.0.0.1/

Running `make demo` again will erase the database from the previous run.

Tests
=====

To run the tests, first install the testing-requirements::

    pip install -r requirements/test.txt

then run the tests with::

    make test APP=verification

Usage
=====

Create a KeyGroup. KeyGroups hold the config for your Keys, so you might want
to make fixtures of them.

.. code-block:: python

    from verification.models import KeyGroup

    keygroup = KeyGroup(
        name='activate_account', # Unique
        generator='sha1',        # See verification.generators
    )

Create a Key on some event, for instance when a user clicks a button:

.. code-block:: python

    from verification.models import Key

    Key.generate(group=keygroup)

Set Key.send_func to some callable:

.. code-block:: python

    from django.core.mail import send_mail

    # In this minimal example, the contents of the email is created earlier
    def email_key(recipient, content):
        subject = "Activate account on FooBlog"
        recipient = ''.join(recipient.strip().split())
        # Use any kind of messaging-system here
        send_mail(subject, content, 'noreply@example.com', [recipient])

    key.send_func = email_key

Choose the claim-view, make the content of the email, send it with
key.send_key():

.. code-block:: python

    from django.core.urlresolvers import reverse

    activate_url = reverse('verification-claim-post-url',
            kwargs={'key': key, 'group': key.group})
    content = "Click on %s to activate your account on FooBlog!" % activate_url
    recipient = 'john.oe@example.com'

    key.send_key(recipient, content)

Hook the ``key_claimed``-signal in order to do something after the key is claimed:

.. code-block:: python

    from django.dispatch import receiver

    from verification.signals import key_claimed

    @receiver(key_claimed)
    def user_created_key_claimed(sender, **kwargs):
        claimant = kwargs['claimant']
        claimant.is_active = True
        claimant.save()

:Version: 0.2
