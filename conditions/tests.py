from django.contrib.auth.models import User
from django.db import models
from django.test import TestCase

from .conditions import Condition, CompareCondition
from .fields import ConditionsField
from .lists import eval_conditions


class FullName(Condition):

    condstr = 'FULL_NAME'

    def eval_bool(self, user, **kwargs):
        return bool(user.first_name and user.last_name)


class Level(CompareCondition):

    condstr = 'LEVEL'

    def eval_operand(self, user, **kwargs):
        return user.userprofile.level


conditions_definitions = {
    'User': {
        'FULL_NAME': FullName,
        'LEVEL': Level,
    },
}


class UserProfile(models.Model):

    user = models.OneToOneField(User)
    level = models.IntegerField(default=1)


class Campaign(models.Model):

    text = models.TextField()
    conditions = ConditionsField(definitions=conditions_definitions)


class CampaignTest(TestCase):

    def setUp(self):
        self.mrx = User.objects.create_user(
            username='mr.x',
            email='x@gmail.com',
            password='top_secret'
        )
        self.mrsy = User.objects.create_user(
            username='mrs.y',
            email='y@gmail.com',
            password='also_top_secret'
        )
        for user in [self.mrx, self.mrsy]:
            UserProfile.objects.create(user=user)

        self.campaign = Campaign.objects.create(
            text='Thanks for providing your full name.',
            conditions={
                'all': ["FULL_NAME",],
            }
        )
        self.comparecondition_campaign = Campaign.objects.create(
            text='Congratulations on getting to Level 5!',
            conditions={
                'all': ["LEVEL == 5",],
            }
        )

    def tearDown(self):
        UserProfile.objects.all().delete()
        User.objects.all().delete()

    def test_basic_campaign_targetting(self):
        # Neither user should be targetted before having a name
        self.assertFalse(eval_conditions(self.campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.campaign, 'conditions', self.mrsy))

        # Mr. X adds his full name; Mrs. Y only adds her last name
        self.mrx.first_name = 'Mr.'
        self.mrx.last_name = 'X'
        self.mrsy.last_name = 'Y'

        # Now Mr. X is targetted, but Mrs. Y is not
        self.assertTrue(eval_conditions(self.campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.campaign, 'conditions', self.mrsy))

    def test_comparecondition_campaign(self):
        # Neither user should be targetted with level 1
        self.assertFalse(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrsy))

        # Mrs. Y upgrades to level 5
        self.mrsy.userprofile.level += 4

        # Now Mrs. Y is targetted, but Mr. X is not
        self.assertFalse(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrx))
        self.assertTrue(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrsy))

        # Mrs. Y upgrades to level 6
        self.mrsy.userprofile.level += 1

        # Now neither user once again is targetted
        self.assertFalse(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.comparecondition_campaign, 'conditions', self.mrsy))
