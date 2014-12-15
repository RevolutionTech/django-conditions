Basic Usage
^^^^^^^^^^^

Start by defining a condition in code:

.. code-block:: python

    ## condition_types.py
    from conditions import Condition

    class FullName(Condition):
        # The name that appears in the db and represents your condition
        condstr = 'FULL_NAME'

        # Normal conditions define eval_bool, which takes in a user
        # and returns a boolean
        def eval_bool(self, user, **kwargs):
            return bool(user.first_name and user.last_name)

Then add a ConditionsField to your model:

.. code-block:: python

    ## models.py
    from django.db import models
    from conditions import ConditionsField, conditions_from_module
    import condition_types

    class Campaign(models.Model):
        text = models.TextField()

        # The ConditionsField requires the definitions of all possible conditions
        # conditions_from_module can take an imported module and sort this out for you
        target = ConditionsField(definitions=conditions_from_module(condition_types))

In the model's change form on admin, you can enter JSON to represent when you want your condition to be satisfied.

.. code-block:: javascript

    {
        "all": ["FULL_NAME"]
    }

Now you can use the logic you created in admin to determine the outcome of an event:

.. code-block:: python

    ## views.py
    from django.http import HttpResponse
    from conditions import eval_conditions
    from models import Campaign

    def profile(request):
        for campaign in Campaign.objects.all():
            if eval_conditions(campaign, 'target', request.user):
                return HttpReponse(campaign.text)

        return HttpResponse("Nothing new to see.")

Use django-conditions in your Django projects to change simple logic without having to re-deploy, and pass on the power to product managers and other non-engineers.
