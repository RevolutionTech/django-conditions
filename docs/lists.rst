Condition Lists
^^^^^^^^^^^^^^^

Once you've created a few Conditions, you can combine them in many different ways.

To require multiple conditions to be satisfied at the same time, use an "all" list:

.. code-block:: javascript

    {
        "all": ["FULL_NAME", "ACTIVE", "SUPERUSER"]
    }

To allow just one of a set of conditions, use an "any" list:

.. code-block:: javascript

    {
        "any": ["FULL_NAME", "FB_CONNECTED", "EMAIL_VERIFIED"]
    }

Of course the lists may be nested:

.. code-block:: javascript

    {
        "all": [
            "ACTIVE",
            "SUPERUSER",
            {
                "any": [
                    "FULL_NAME",
                    "FB_CONNECTED",
                    "EMAIL_VERIFIED"
                ]
            }
        ]
    }

You may also add :code:`NOT` to the beginning of any condition to evaluate its negation:

.. code-block:: javascript

    {
        "all": ["FULL_NAME", "ACTIVE", "NOT SUPERUSER", "NOT STAFF"]
    }
