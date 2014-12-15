Providing Additional Context
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Sometimes you want to evaluate a condition on more information than just a user object. For these cases, you can provide any arbitrary keyword arguments to :code:`eval_conditions`:

.. code-block:: python

    ## views.py
    from django.http import HttpResponse
    from conditions import eval_conditions
    from models import Campaign

    def room(request, room_num):
        for campaign in Campaign.objects.all():
            if eval_conditions(campaign, 'target', request.user, room=room_num):
                return HttpReponse(campaign.text)

        return HttpResponse("Nothing in this room.")

Any keyword arguments are then passed through to every condition that needs to be evaluated:

.. code-block:: python

    class InRoom(Condition):
        condstr = 'IN_ROOM'

        def eval_bool(self, user, **kwargs):
            room_num = kwargs['room']
            return room_num == int(self.key)
