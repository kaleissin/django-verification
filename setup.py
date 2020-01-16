#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

README_FILE = open('README.rst')
try:
    long_description = README_FILE.read()
finally:
    README_FILE.close()

setup(name='django-verification',
        version='1.1.0',
        packages=['verification'],
        package_dir = {'': 'src',},
        include_package_data=True,
        zip_safe=False,
        platforms=['any'],
        description='Generalized app for two-step verification',
        author_email='kaleissin@gmail.com',
        author='kaleissin',
        url='https://github.com/kaleissin/django-verification',
        long_description=long_description,
        install_requires=['Django>=1.11,<3.0'],
        classifiers=[
                'Development Status :: 4 - Beta',
                'Environment :: Web Environment',
                'Framework :: Django',
                'Intended Audience :: Developers',
                'License :: OSI Approved :: MIT License',
                'Operating System :: OS Independent',
                'Programming Language :: Python',
                'Topic :: Software Development :: Libraries :: Application Frameworks',
                'Topic :: Software Development :: Libraries :: Python Modules',
                'Framework :: Django :: 1.11',
                'Framework :: Django :: 2.2',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.5',
                'Programming Language :: Python :: 3.6',
                'Programming Language :: Python :: 3.7',
        ]
)
