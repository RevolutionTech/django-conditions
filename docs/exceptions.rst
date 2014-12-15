Handling Exceptions
^^^^^^^^^^^^^^^^^^^

When an exception is raised in the evaluation of a Condition, it fails silently by returning False.

.. code-block:: python

    # An example where the condition will raise a ValueError

    class Broken(Condition):
        condstr = 'BROKEN'

        def eval_bool(self, user, **kwargs):
            raise ValueError("This condition is broken.")

Failing silently often avoids major problems, but generally, you still want to know when these issues are popping up. django-conditions provides a simple way using `Python's built-in logging framework <https://docs.python.org/3/library/logging.html>`_.

To record these exceptions, add a logger for :code:`condition` in the :code:`LOGGING` configuration dictionary, and handle it however you like. Here is an example, modified from `Django's logging page <https://docs.djangoproject.com/en/dev/topics/logging/#examples>`_:

.. code-block:: python

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': 'DEBUG',
                'class': 'logging.FileHandler',
                'filename': '/path/to/django/debug.log',
            },
        },
        'loggers': {
            'django.request': {
                'handlers': ['file'],
                'level': 'DEBUG',
                'propagate': True,
            },
            'condition': {
                'handlers': ['file'],
                'level': 'DEBUG',
            }
        },
    }
