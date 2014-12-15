Using Keys
^^^^^^^^^^

Sometimes you want to generalize a Condition so that the user entering the Conditions JSON can provide an arbitrary string that changes how the Condition gets evaluated slightly. In these cases, you can use a key:

.. code-block:: python

    class EmailDomain(Condition):
        condstr = 'EMAIL_DOMAIN'

        def eval_bool(self, user, **kwargs):
            domain = user.email.split('@')[1]
            return domain == self.key

.. code-block:: javascript

    {
        "any": ["EMAIL_DOMAIN gmail.com", "EMAIL_DOMAIN yahoo.com"]
    }

When the Conditions :code:`"EMAIL_DOMAIN gmail.com"` and :code:`"EMAIL_DOMAIN yahoo.com"` get evaluated, :code:`self.key` will contain the strings "gmail.com" and "yahoo.com" respectively.

Of course, the admin interface once again does not know what keys are appropriate so by default, the random example will simply say :code:`SOME_KEY_HERE`. You can define :code:`key_examples` as a list similar to :code:`operand_examples`, or if the set of all possible keys is finite, you may define :code:`keys_allowed` to actually restrict the user entering the Conditions JSON to one of the options from a list:

.. code-block:: python

    class EmailDomain(Condition):
        condstr = 'EMAIL_DOMAIN'
        key_examples = ['gmail.com', 'yahoo.com', 'hotmail.com']

        ...
