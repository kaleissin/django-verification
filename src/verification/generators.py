# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import hashlib
import random
import re
import string

# Some chars are hard to tell apart in some phone-fonts:
# 1 vs. l vs. I
SAFE_ALPHABET = 'abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ0123456789+-'
SHORT_LENGTH = 8

__all__ = ['Registry', 'GeneratorError']

class GeneratorError(Exception):
    pass

class AbstractKeyGenerator(object):
    """Do not use directly."""
    length = 0
    name = 'abstract'

    def __init__(self, length=0, seed=None, randomizer=None, name='', **kwargs):
        self.random = randomizer if randomizer else random
        self.length = length if length else self.length
        self.name = name if name else self.name
        self.seed = seed
        if self.seed:
            self.random.seed(self.seed)

    def generate_one_key(self, *args):
        raise NotImplemented

    def valid_key(self, key):
        raise NotImplemented

    def sms_safe(self):
        return True if self.length <= 10 else False

    def tweet_safe(self):
        return True if self.length <= 40 else False

    def register(self):
        registry = Registry()
        registry.register(self.name, self)

    def unregister(self):
        registry = Registry()
        registry.unregister(self.name)

class AbstractAlphabetKeyGenerator(AbstractKeyGenerator):
    """Can be used directly, behaves like SMSKeyGenerator"""
    alphabet = SAFE_ALPHABET
    length = SHORT_LENGTH

    def __init__(self, alphabet='', **kwargs):
        super(AbstractAlphabetKeyGenerator, self).__init__(**kwargs)
        self.alphabet = alphabet if alphabet else self.alphabet
        self.base = len(self.alphabet)
        self.valid_re = re.compile('^[%s]{%i}$' % (self.alphabet, self.length))

    def generate_one_key(self, *args):
        """Alphabet generators do not use salts or extra in-data"""
        key = []
        for i in range(self.length):
            key.append(self.alphabet[self.random.randint(0, self.base-1)])
        return ''.join(key)

    def valid_key(self, key):
        return self.valid_re.search(key)

class SMSKeyGenerator(AbstractAlphabetKeyGenerator):
    name = 'sms'
    alphabet = SAFE_ALPHABET
    length = SHORT_LENGTH

class PINCodeGenerator(AbstractAlphabetKeyGenerator):
    name = 'pin'
    alphabet = '0123456789'
    length = 4

class UsernameKeyGenerator(AbstractKeyGenerator):
    name = 'username'
    alphabet = string.ascii_letters + string.digits

class LowercaseKeyGenerator(AbstractAlphabetKeyGenerator):
    name = 'lowercase'
    alphabet = string.ascii_lowercase

class HashedHexKeyGenerator(AbstractAlphabetKeyGenerator):
    """The generated keys are typically so long that they are not suitable for
    typing, but ought to be made clickable"""
    hex_alphabet = 'abcdef0123456789'
    alphabet = hex_alphabet[:]
    hasher = hashlib.sha1
    name = '-hex'

    def __init__(self, hasher=None, **kwargs):
        """Takes one extra keyword argument, the hasher to use.
        
        This s a function or method which:
            - takes one input-argument when called
            - the result of the call has a callable, hexdigest()
        
        All the hashers in hashlib fulfills this.
        
        The fallback hasher is hashlib.sha1()"""

        super(HashedHexKeyGenerator, self).__init__(**kwargs)
        self.base = 16
        self.hasher = hasher if hasher else self.hasher
        self.length = len(self.hasher().hexdigest())
        if self.alphabet != self.hex_alphabet:
            self.alphabet = self.alphabet[:16]

    def generate_one_key(self, *args):
        super(HashedHexKeyGenerator, self).generate_one_key(*args)
        if not args:
            args = [self.random.random()]
        args = [str(arg) for arg in args]
        salt = self.hasher(str(self.random.random())).hexdigest()[:5]
        return self.hasher(salt+''.join(args)).hexdigest()

class MD5HexKeyGenerator(HashedHexKeyGenerator):
    name = 'md5-hex'
    hasher = hashlib.md5

class SHA1HexKeyGenerator(HashedHexKeyGenerator):
    name = 'sha1-hex'
    hasher = hashlib.sha1

class SHA224HexKeyGenerator(HashedHexKeyGenerator):
    name = 'sha224-hex'
    hasher = hashlib.sha224

class SHA256HexKeyGenerator(HashedHexKeyGenerator):
    name = 'sha256-hex'
    hasher = hashlib.sha256

class SHA384HexKeyGenerator(HashedHexKeyGenerator):
    name = 'sha384-hex'
    hasher = hashlib.sha384

class SHA512HexKeyGenerator(HashedHexKeyGenerator):
    name = 'sha512-hex'
    hasher = hashlib.sha512

class Registry(object):
    _generators = {}

    def register(self, name, generator):
        self._generators[name] = generator

    def unregister(self, name):
        if name in self.available():
            del self._generators[name]

    def available(self):
        return self._generators.keys()

    def get(self, generator, fallback=None):
        generator = self._generators.get(generator, fallback)
        if generator == fallback and fallback is None:
            raise GeneratorError('Invalid generator')
        return generator

    def reset(self):
        reset()

registry = Registry()

DEFAULT_GENERATORS = (
    SMSKeyGenerator,
    PINCodeGenerator,
    UsernameKeyGenerator,
    LowercaseKeyGenerator,
    MD5HexKeyGenerator,
    SHA1HexKeyGenerator,
    SHA224HexKeyGenerator,
    SHA256HexKeyGenerator,
    SHA384HexKeyGenerator,
    SHA512HexKeyGenerator,
)

DEFAULT_GENERATOR_NAMES = []

def reset():
    global DEFAULT_GENERATOR_NAMES
    DEFAULT_GENERATOR_NAMES = []
    for generator in DEFAULT_GENERATORS:
        name = generator.name
        registry.register(name, generator)
        DEFAULT_GENERATOR_NAMES.append(name)
    for generator in registry.available():
        if not generator in DEFAULT_GENERATOR_NAMES:
            registry.unregister(generator)

reset()
