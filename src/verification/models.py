from __future__ import unicode_literals

from datetime import timedelta

from django.db import models
from django.utils.timezone import now as tznow
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet

from verification.signals import key_claimed
from verification.generators import registry as generators

__all__ = [
    'VerificationError', 
    'KeyQuerySet',
    'KeyGroup',
    'AbstractKey',
    'claim',
]

Q = models.Q

class VerificationError(Exception):
    pass

def claim(keystring, claimant):
    """Claims a specific key for claimant, returns True if successful,
    raises an exception otherwise"""
    now = tznow()
    try:
        key = Key.objects.get(key=keystring)
    except Key.DoesNotExist:
        raise VerificationError('Key %s does not exist, typo?' % keystring)
    if key.expires and key.expires <= now:
        raise VerificationError('Key expired on %s' % key.expires)
    if key.claimed:
        raise VerificationError('Key has already been claimed')
    key.claimed_by = claimant
    key.claimed = now
    key.save()
    key_claimed.send_robust(sender=key, claimant=claimant, group=key.group)
    return key

class KeyQuerySet(QuerySet):

    def expired(self):
        "Get keys that have expired"
        now = tznow()
        return self.exclude(expires=None).filter(expires__lte=now)

    def available(self):
        "Get still available keys"
        now = tznow()
        return self.filter(Q(expires__gt=now)|Q(expires=None)).filter(claimed=None)

    def claimed(self):
        "Get claimed keys"
        return self.exclude(claimed=None)

    def delete_expired(self):
        """Removes expired keys"""
        now = tznow()
        self.filter(expires__lte=now).delete()

    def claim(self, *args):
        return claim(*args)


class KeyGroup(models.Model):
    """
    name      - The purpose of the group: password reset, verify email address etc.
    ttl       - Time to live. A generated key will have "expires" set to
                "pub_date" + "ttl", or will not expire of ttl is None
    generator - The name of a key generator
    has_fact  - Whether Key.fact must be set
    """
    name = models.SlugField(max_length=32, primary_key=True)
    ttl = models.IntegerField('Time to live, in minutes', blank=True, null=True)
    generator = models.CharField(max_length=64)
    has_fact = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_generator(self):
        if self.generator in generators.available():
            return generators.get(self.generator)

    def purge_keys(self):
        "Delete all keys belonging to this group"
        model = self.keys.model
        model.objects.filter(group=self).delete()

    def generate_one_key(self, keycls, seed=None, fact=None, *args):
        "Generate and return a new key of class <keycls>"
        Generator = self.get_generator()
        generator = Generator(seed=seed)
        keystring = generator.generate_one_key(*args)
        key = keycls(group=self, key=keystring)
        if fact:
            key.fact = fact
        key.save()
        return key


class AbstractKey(models.Model):
    """
    key         - Generated by the group.
    group       - Groups the keys into the same type, provides a generator
    fact        - Some fact that is claimed/verified by the claimant. Can be empty.
    pub_date    - When the key was generated
    expires     - Datetime for when the key expires, or None for doesn't expire
    claimed     - When the key was claimed

    Subclass this if keys are to be claimed by another model than AUTH_USER_MODEL.

    Something like this:

        class YourSpecialKey(AbstractKey):
            claimed_by = models.ForeignKey(
                'yourapp.yourmodel',
                on_delete=models.CASCADE,
                blank=True,
                null=True
            )

            objects = KeyQuerySet.as_manager()

    If you need to do more than just setting claimed_by to the correct
    yourapp.yourmodel-instance when claiming:

    1. Write your own claim()-function (it can call the existing claim()-function)
    2. Subclass the KeyQuerySet to call your claim-function::

        class YourSpecialKeyQuerySet(KeyQuerySet):

            def claim(self, *args):
                return yourclaim(*args)

    3. Replace the claim-method on the YourSpecialKey-class and add in your own manager::

        class YourSpecialKey(AbstractKey):
            claimed_by = models.ForeignKey(
                'yourapp.yourmodel',
                on_delete=models.CASCADE,
                blank=True,
                null=True
            )

            objects = YourSpecialKeyQuerySet.as_manager()

            def claim(self, your_args):
                return claim(self.key, yourargs)
    """
    send_func = None

    key = models.CharField(unique=True, max_length=255)
    group = models.ForeignKey(KeyGroup, on_delete=models.CASCADE, related_name='keys')
    fact = models.TextField(blank=True, null=True)
    pub_date = models.DateTimeField(default=tznow, editable=False, blank=True)
    expires = models.DateTimeField(blank=True, null=True)
    claimed = models.DateTimeField(blank=True, null=True)

    objects = KeyQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ('-pub_date',)
        get_latest_by = 'pub_date'

    def __str__(self):
        return self.key

    def pprint(self):
        "Show info about a key"
        return  '%s (%s) %s (<= %s)' % (self.key, self.group, self.pub_date, self.expires)

    def save(self, *args, **kwargs):
        "Save key and set ttl if the group has it"
        now = tznow()
        if not self.pk:
            self.pub_date = now
            if self.group.ttl:
                add_minutes = timedelta(minutes=self.group.ttl)
                self.expires = self.pub_date + add_minutes
        super(AbstractKey, self).save(*args, **kwargs)

    def clean(self):
        """Verify that facts is filled if the group demands it"""
        if self.group.has_fact == True and not self.fact:
            raise ValidationError('This key must have a fact but none is provided')

    @classmethod
    def generate(cls, group, seed=None, fact=None, *args):
        "Generate and return a new key"
        key = group.generate_one_key(cls, seed, fact, *args)
        return key

    def claim(self, user):
        "Claim this key for user"
        self = claim(self.key, user)
        return self

    def send_key(self, *args, **kwargs):
        "Send this key with <send_func>"
        if callable(self.send_func):
            return self.send_func(*args, **kwargs)
        raise TypeError('Key.send_func is not a callable')

class Key(AbstractKey):
    """Standard key, claimable by AUTH_USER_MODEL"""
    claimed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name='verification_keys')

    objects = KeyQuerySet.as_manager()
