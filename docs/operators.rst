Operators and Operands
^^^^^^^^^^^^^^^^^^^^^^

Conditions that subclass CompareCondition are slightly more advanced than regular Conditions. You can use them to make comparisons with numbers (or other operands).

.. code-block:: python

    from conditions import CompareCondition

    class Level(CompareCondition):
        condstr = 'LEVEL'

        # CompareConditions define eval_operand instead of eval_bool
        # which returns an operand instead
        def eval_operand(self, user, **kwargs):
            return user.profile.level

In JSON, numbers can be compared using the normal boolean operators you see in Python (:code:`<`, :code:`<=`, :code:`==`, :code:`!=`, :code:`>`, and :code:`>=`):

.. code-block:: javascript

    {
        "all": ["FULL_NAME", "LEVEL >= 5"]
    }

By default, a CompareCondition expects a float as the operand, but that can be overwritten by defining the cast_operand attribute. You can also define your own operators by writing your own operators function:

.. code-block:: python

    import datetime
    from conditions import CompareCondition

    class DateJoined(CompareCondition):
        condstr = 'DATE_JOINED'
        cast_operand = lambda self, timestamp: datetime.datetime.strptime(timestamp, "%m/%d/%Y")

        @classmethod
        def operators(cls):
            return {
                '<': datetime.datetime.__lt__,
                '<=': datetime.datetime.__le__,
                '==': datetime.datetime.__eq__,
                '!=': datetime.datetime.__ne__,
                '>=': datetime.datetime.__ge__,
                '>': datetime.datetime.__gt__,
            }

        def eval_operand(self, user, **kwargs):
            return user.date_joined.strftime("%m/%d/%Y")

In the admin interface, an appropriate example is randomly generated for each Condition available. When the operand is a number, a number will be generated randomly for the example automatically. However, with other types of operands this isn't possible so the example will simply show :code:`SOME_OPERAND_HERE`. If you like, you can instead show an appropriate example randomly selected from a list you define:

.. code-block:: python

    class DateJoined(CompareCondition):
        condstr = 'DATE_JOINED'
        cast_operand = timestamp2datetime
        operand_examples = ['04/23/1995', '01/01/2015', '08/13/2014',]

        ...
