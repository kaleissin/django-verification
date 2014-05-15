from __future__ import unicode_literals

import random
import hashlib
import datetime
import unittest

from django.core.urlresolvers import resolve, reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django import test
from django.http import HttpRequest

from verification.models import *
from verification.views import *
from verification.generators import (
    Registry,
    GeneratorError,
    SMSKeyGenerator,
    AbstractKeyGenerator,
    AbstractAlphabetKeyGenerator,
    HashedHexKeyGenerator,
    DEFAULT_GENERATOR_NAMES,
    SAFE_ALPHABET,
    SHORT_LENGTH,
)

class RegistryTest(unittest.TestCase):

    def setUp(self):
        registry = Registry()
        registry.reset()

    def tearDown(self):
        registry = Registry()
        registry.unregister('abstract')

    def test_available(self):
        registry = Registry()
        available = registry.available()
        expected = DEFAULT_GENERATOR_NAMES
        self.assertEqual(set(available), set(expected))

    def test_get(self):
        registry = Registry()
        sms = registry.get('sms')
        self.assertEqual(sms, SMSKeyGenerator)

    def test_register(self):
        registry = Registry()
        registry.register('abstract', AbstractKeyGenerator)
        self.assertEqual(registry.get('abstract'), AbstractKeyGenerator)

    def test_unregister(self):
        registry = Registry()
        registry.register('abstract', AbstractKeyGenerator)
        registry.unregister('abstract')
        self.assertRaises(GeneratorError, registry.get, 'abstract')
        self.assertFalse(registry.get('abstract', False))

    def test_reset(self):
        registry = Registry()
        expected = DEFAULT_GENERATOR_NAMES
        registry.register('abstract', AbstractKeyGenerator)
        now_expected = DEFAULT_GENERATOR_NAMES + ['abstract']
        self.assertEqual(set(registry.available()), set(now_expected))
        registry.reset()
        self.assertEqual(set(registry.available()), set(expected))

class AbstractKeyGeneratorTest(unittest.TestCase):

    def tearDown(self):
        registry = Registry()
        registry.unregister('abstract')

    def test_init(self):
        gen = AbstractKeyGenerator()
        self.assertEqual(gen.length, 0)
        #self.assertEqual(gen.name, '')
        self.assertEqual(gen.seed, None)

    def test_sms_safe(self):
        gen = AbstractKeyGenerator()
        self.assertEqual(gen.sms_safe(), True)
        gen = AbstractKeyGenerator(length=10)
        self.assertEqual(gen.sms_safe(), True)
        gen = AbstractKeyGenerator(length=11)
        self.assertEqual(gen.sms_safe(), False)

    def test_tweet_safe(self):
        gen = AbstractKeyGenerator()
        self.assertEqual(gen.tweet_safe(), True)
        gen = AbstractKeyGenerator(length=40)
        self.assertEqual(gen.tweet_safe(), True)
        gen = AbstractKeyGenerator(length=41)
        self.assertEqual(gen.tweet_safe(), False)

    def test_register(self):
        gen = AbstractKeyGenerator()
        gen.register()
        registry = Registry()
        self.assertEqual(registry.get('abstract'), gen)

    def test_unregister(self):
        gen = AbstractKeyGenerator()
        gen.register()
        registry = Registry()
        self.assertEqual(registry.get('abstract'), gen)
        gen.unregister()
        self.assertRaises(GeneratorError, registry.get, 'abstract')

class AbstractAlphabetKeyGeneratorTest(unittest.TestCase):

    def test_init(self):
        gen = AbstractAlphabetKeyGenerator()
        self.assertEqual(gen.alphabet, SAFE_ALPHABET)
        self.assertEqual(gen.length, SHORT_LENGTH)
        self.assertTrue(hasattr(gen, 'base'))
        self.assertTrue(hasattr(gen, 'valid_re'))

    def test_valid_key(self):
        gen = AbstractAlphabetKeyGenerator()
        goodkey = 'abc123+-'
        self.assertTrue(gen.valid_key(goodkey))
        badkey = 'abc"123'
        self.assertFalse(gen.valid_key(badkey))

    def test_generate_one_key(self):
        seed = 12345
        expected_key = 'Aa1txnLk'
        gen = AbstractAlphabetKeyGenerator(seed=seed)
        key = gen.generate_one_key()
        self.assertEqual(expected_key, key)

class HashedHexKeyGeneratorTest(unittest.TestCase):

    def test_init(self):
        gen = HashedHexKeyGenerator()
        self.assertEqual(gen.hasher, hashlib.sha1)
        gen = HashedHexKeyGenerator(alphabet=SAFE_ALPHABET)
        self.assertEqual(gen.base, 16)
        self.assertEqual(gen.alphabet, SAFE_ALPHABET[:16])

    def test_generate_one_key(self):
        seed = 12345
        expected_key = '2b5389d4a96d6f5c03cbbf9b46d56cf0297d9ffd'
        gen = HashedHexKeyGenerator(seed=seed)
        key = gen.generate_one_key()
        self.assertEqual(expected_key, key)
        key = gen.generate_one_key('fii')
        expected_key = '98397f5b411802bac598c3f0a19cd7c3063461ca'
        self.assertEqual(expected_key, key)

class KeyGroupTest(test.TestCase):

    def setUp(self):
        self.kg_sms = KeyGroup.objects.create(name='test1', generator='sms')
        self.kg_pin = KeyGroup.objects.create(name='test2', generator='pin')

    def test_str(self):
        kg = KeyGroup.objects.create(name='test')
        self.assertEqual(str(kg), 'test')

    def test_get_generator(self):
        self.assertEqual(self.kg_sms.get_generator(), SMSKeyGenerator)
        kg = KeyGroup.objects.create(name='test3', generator='doesnotexist')
        self.assertIsNone(kg.get_generator())

    def test_purge_keys(self):
        model = self.kg_sms.key_set.model
        for i in range(5):
            model.generate(self.kg_sms)
        for i in range(5):
            model.generate(self.kg_pin)
        self.assertEqual(model.objects.count(), 10)
        self.kg_sms.purge_keys()
        self.assertEqual(set(model.objects.all()),
                         set(model.objects.filter(group=self.kg_pin)))
        self.assertEqual(model.objects.count(), 5)

    def test_generate_one_key(self):
        k = self.kg_sms.generate_one_key(Key, seed=12345)
        self.assertEqual(k.key, 'Aa1txnLk')

    def test_generate_one_key_with_fact(self):
        fact = 'this is a test'
        k = self.kg_sms.generate_one_key(Key, seed=12345, fact=fact)
        self.assertEqual(k.key, 'Aa1txnLk')
        self.assertEqual(k.fact, fact)

class KeyTest(test.TestCase):

    def setUp(self):
        self.kg_sms = KeyGroup.objects.create(name='sms', generator='sms')
        self.kg_fact = KeyGroup.objects.create(name='fact', has_fact=True, generator='pin')
        self.kg_ttl = KeyGroup.objects.create(name='ttl', ttl=5, generator='pin')

    def test_expired(self):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=5)
        k = Key.objects.create(group=self.kg_sms, expires=earlier)
        expired_keys = Key.objects.expired()
        self.assertEqual(k, expired_keys[0])

    def test_delete_expired(self):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=5)
        k = Key.objects.create(group=self.kg_sms, expires=earlier)
        Key.objects.delete_expired()
        expired_keys = Key.objects.expired()
        self.assertFalse(expired_keys)

    def test_claimed(self):
        now = datetime.datetime.now()
        k = Key.objects.create(group=self.kg_sms, claimed=now)
        claimed_keys = Key.objects.claimed()
        self.assertEqual(k, claimed_keys[0])

    def test_available(self):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=5+random.randint(0, 200))
        later = now + datetime.timedelta(minutes=5+random.randint(0, 200))
        k1 = Key.objects.create(key='1', group=self.kg_sms, claimed=now)
        k2 = Key.objects.create(key='2', group=self.kg_sms, claimed=now, expires=earlier)
        k3 = Key.objects.create(key='3', group=self.kg_sms, claimed=now, expires=later)
        k4 = Key.objects.create(key='4', group=self.kg_sms)
        k5 = Key.objects.create(key='5', group=self.kg_sms, expires=earlier)
        k6 = Key.objects.create(key='6', group=self.kg_sms, expires=later)
        claimed_keys = Key.objects.claimed()
        self.assertEqual(set(Key.objects.available()), set((k4, k6)))

    def test_pprint(self):
        now = datetime.datetime.now()
        k = Key.objects.create(key='PPRint', group=self.kg_sms, pub_date=now)
        pub_date = k.pub_date
        simple = k.pprint()
        self.assertEqual(simple, 'PPRint (sms) %s (<= None)' % pub_date)
        k.expires = now
        k.save()
        simple = k.pprint()
        self.assertEqual(simple, 'PPRint (sms) %s (<= %s)' % (pub_date, now))

    def test_clean(self):
        k1 = Key.objects.create(key='1', group=self.kg_sms)
        self.assertEqual(k1.clean(), None)
        k2 = Key.objects.create(key='2', group=self.kg_sms, fact='boo')
        self.assertEqual(k2.clean(), None)
        k3 = Key.objects.create(key='3', group=self.kg_fact)
        self.assertRaises(ValidationError, k3.clean)
        k4 = Key.objects.create(key='4', group=self.kg_fact, fact='boo')
        self.assertEqual(k4.clean(), None)

    def test_save(self):
        k1 = Key(key='1', group=self.kg_sms)
        k1.save()
        self.assertIsNone(k1.expires)
        k2 = Key(key='2', group=self.kg_ttl)
        k2.save()
        self.assertEqual(k2.expires, k2.pub_date + datetime.timedelta(minutes=5))

    def test_send_key(self):
        def dummy_send(*args):
            return args
        k1 = Key.objects.create(key='1', group=self.kg_sms)
        self.assertRaises(TypeError, k1.send_key)
        k2 = Key.objects.create(key='2', group=self.kg_sms)
        k2.send_func = dummy_send
        self.assertEqual(('mjam',), k2.send_key('mjam'))

    def test_str(self):
        k1 = Key.objects.create(key='1', group=self.kg_sms)
        self.assertEqual(str(k1), '1')

    def test_claim(self):
        k1 = Key.objects.create(key='1', group=self.kg_sms)
        User = get_user_model()
        u = User.objects.create(username='testuser')
        k_claimed = k1.claim(u)
        self.assertEqual(k_claimed.claimed_by, u)
        self.assertTrue(k_claimed.claimed)

    def test_claim_manager(self):
        k1 = Key.objects.create(key='1', group=self.kg_sms)
        User = get_user_model()
        u = User.objects.create(username='testuser')
        k_claimed = Key.objects.claim('1', u)
        self.assertEqual(k_claimed.claimed_by, u)
        self.assertTrue(k_claimed.claimed)

    def test_generate(self):
        k = Key.generate(group=self.kg_sms, seed=12345)
        self.assertEqual(k.key, 'Aa1txnLk')
        self.assertEqual(k.group, self.kg_sms)

    def test_generate_with_fact(self):
        fact = 'this is a test'
        k = Key.generate(group=self.kg_sms, seed=12345, fact=fact)
        self.assertEqual(k.key, 'Aa1txnLk')
        self.assertEqual(k.group, self.kg_sms)
        self.assertEqual(k.fact, fact)

class ClaimTest(test.TestCase):

    def setUp(self):
        self.kg = KeyGroup.objects.create(name='sms')
        User = get_user_model()
        self.user = User.objects.create(username='testuser')

    def test_claim_key_exists(self):
        k1 = Key.objects.create(key='1', group=self.kg)
        k_claimed = claim('1', self.user)
        self.assertEqual(self.user, k_claimed.claimed_by)
        self.assertTrue(k_claimed.claimed)

    def test_claim_key_doesnotexist(self):
        self.assertRaises(VerificationError, claim, '1', self.user)

    def test_claim_already_claimed(self):
        k1 = Key.objects.create(key='1', group=self.kg)
        k_claimed = claim('1', self.user)
        self.assertRaises(VerificationError, claim, '1', self.user)

    def test_claim_expired(self):
        now = datetime.datetime.now()
        earlier = now - datetime.timedelta(minutes=5+random.randint(0, 200))
        k1 = Key.objects.create(key='1', group=self.kg, expires=earlier)
        self.assertRaises(VerificationError, claim, '1', self.user)

class AdminTest(unittest.TestCase):

    def test_all_defined(self):
        try:
            import verification.admin
        except (NameError, AssertionError) as e:
            self.fail(e)

class ClaimSuccessViewTest(test.TestCase):

    def setUp(self):
        self.kg = KeyGroup.objects.create(name='sms')
        self.k = Key.objects.create(key='blabla', group=self.kg)
        self.factory = test.RequestFactory()

    def test_find_view(self):
        kwargs = {
            'key': self.k.key,
            'group': self.kg.name
        }
        found = resolve(reverse('verification-success', kwargs=kwargs))
        self.assertEqual(found.func, claim_success)

    def test_not500(self):
        kwargs = {
            'key': self.k.key,
            'group': self.kg.name
        }
        request = self.factory.get(reverse('verification-success', kwargs=kwargs))
        response = claim_success(request, **kwargs)
        self.assertNotEqual(response.status_code, 500)
