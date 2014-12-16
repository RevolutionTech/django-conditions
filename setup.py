import os
from setuptools import setup, Command


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
        if django.VERSION[:2] >= (1, 7):
            django.setup()
        call_command('test', 'conditions')


setup(
    name='django-conditions',
    version='0.9.0',
    packages=['conditions'],
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
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['Django>=1.4.3', 'django-jsonfield>=0.9.13'],
    tests_require=['Django>=1.4.3', 'django-jsonfield>=0.9.13'],
    cmdclass={'test': TestCommand},
)
