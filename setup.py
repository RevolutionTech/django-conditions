#!/usr/bin/env python
import os
from setuptools import setup, find_packages, Command


with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import django
        from django.conf import settings
        from django.core.management import call_command

        settings.configure(
            DATABASES={
                'default': {
                    'NAME': ':memory:',
                    'ENGINE': 'django.db.backends.sqlite3',
                }
            },
            INSTALLED_APPS=(
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'conditions',
            ),
            MIDDLEWARE_CLASSES=()
        )
        django.setup()
        call_command('test')


requirements = [
    'Django >= 1.8, < 1.10a0',
    'django-jsonfield >= 1.0.1, < 2.0.0a0',
]


setup(
    name='django-conditions',
    version='0.9.10',
    packages=find_packages(),
    include_package_data=True,
    license='ISC License',
    description='A Django app that allows creation of conditional logic in admin.',
    long_description=README,
    url='https://github.com/RevolutionTech/django-conditions/',
    author='Lucas Connors',
    author_email='lucas@revolutiontech.ca',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    package_data={
        'conditions': [
            'static/conditions/js/conditions_widget.js',
            'static/conditions/img/icon-information.png',
            'static/conditions/img/icon-information.png',
            'static/conditions/img/icon-information.png',
            'templates/conditions/conditions_widget.html',
        ],
    },
    install_requires=requirements,
    tests_require=requirements,
    cmdclass={'test': TestCommand},
)
