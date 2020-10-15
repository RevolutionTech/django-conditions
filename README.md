# django-conditions

[![Build Status](https://travis-ci.org/RevolutionTech/django-conditions.svg?branch=master)](https://travis-ci.org/RevolutionTech/django-conditions)
[![codecov](https://codecov.io/gh/RevolutionTech/django-conditions/branch/master/graph/badge.svg)](https://codecov.io/gh/RevolutionTech/django-conditions)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/8fccc57f17e44c5496a912adc691fc39)](https://www.codacy.com/app/RevolutionTech/django-conditions)
[![Dependency Status](https://www.versioneye.com/user/projects/56de7e4cdf573d0048dafc52/badge.svg?style=flat)](https://www.versioneye.com/user/projects/56de7e4cdf573d0048dafc52)
[![Documentation Status](https://readthedocs.org/projects/django-conditions/badge/?version=latest)](http://django-conditions.readthedocs.org/en/latest/)

Move conditional logic that changes often from code into models so that the logic can be easily modified in admin. Some possible use cases:
- Segment your user base into cohorts with targeted messaging
- Provide different rewards to users depending on their expected value
- In a game, define the winning objectives of a mission/quest
- and many more...

## Installation

First install the `django-conditions` package:

    pip install django-conditions

Then add `conditions` to your `INSTALLED_APPS` setting:

```python
## settings.py
INSTALLED_APPS = [
    ...
    'conditions',
]
```

## Basic Usage

Start by defining a condition in code:

```python
## condition_types.py
from conditions import Condition

class FullName(Condition):
    # The name that appears in the db and represents your condition
    condstr = 'FULL_NAME'

    # Normal conditions define eval_bool, which takes in a user
    # and returns a boolean
    def eval_bool(self, user, **kwargs):
        return bool(user.first_name and user.last_name)
```

Then add a ConditionsField to your model:

```python
## models.py
from django.db import models
from conditions import ConditionsField, conditions_from_module
import condition_types

class Campaign(models.Model):
    text = models.TextField()

    # The ConditionsField requires the definitions of all possible conditions
    # conditions_from_module can take an imported module and sort this out for you
    target = ConditionsField(definitions=conditions_from_module(condition_types))
```

In the model's change form on admin, you can enter JSON to represent when you want your condition to be satisfied.

```javascript
{
    "all": ["FULL_NAME"]
}
```

Now you can use the logic you created in admin to determine the outcome of an event:

```python
## views.py
from django.http import HttpResponse
from conditions import eval_conditions
from models import Campaign

def profile(request):
    for campaign in Campaign.objects.all():
        if eval_conditions(campaign, 'target', request.user):
            return HttpReponse(campaign.text)

    return HttpResponse("Nothing new to see.")
```

Use django-conditions in your Django projects to change simple logic without having to re-deploy, and pass on the power to product managers and other non-engineers.

## More Information

Full documentation is available [on Read The Docs](http://django-conditions.readthedocs.org/).
