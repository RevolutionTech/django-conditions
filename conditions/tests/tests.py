import datetime

from django.contrib.auth.models import User
from django.test import TestCase

from ..lists import eval_conditions
from .models import UserProfile, Campaign


class CampaignTest(TestCase):

    def setUp(self):
        self.mrx = User.objects.create_user(
            username='mr.x',
            email='x@gmail.com',
            password='top_secret'
        )
        self.mrsy = User.objects.create_user(
            username='mrs.y',
            email='y@yahoo.com',
            password='also_top_secret'
        )
        # Create UserProfile objects
        for user in [self.mrx, self.mrsy]:
            UserProfile.objects.create(user=user)

        # Set Mr. X to have been a long-term member
        self.mrx.date_joined = datetime.datetime(day=31, month=12, year=2013)

        self.campaign = Campaign.objects.create(
            text="Thanks for providing your full name.",
            conditions={
                'all': ["FULL_NAME"],
            }
        )
        self.comparecondition_campaign = Campaign.objects.create(
            text="Congratulations on getting to Level 5!",
            conditions={
                'all': ["LEVEL == 5"],
            }
        )
        self.long_term_user_campaign = Campaign.objects.create(
            text="Thanks for being a long-term member.",
            conditions={
                'any': ["DATE_JOINED < 01/01/2014"],
            }
        )
        self.non_gmail_users_campaign = Campaign.objects.create(
            text="Why aren\'t you using Gmail?",
            conditions={
                'all': ["NOT EMAIL_DOMAIN gmail.com"]
            }
        )
        self.long_term_gmail_yahoo_user_campaign = Campaign.objects.create(
            text="You\'ve been using the same email for a long time.",
            conditions={
                'all': [
                    {
                        'any': ["EMAIL_DOMAIN gmail.com", "EMAIL_DOMAIN yahoo.com"],
                    },
                    "DATE_JOINED < 01/01/2014",
                ],
            }
        )

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

    def test_custom_operators(self):
        # Mr. X is a long-term member, but Mrs. Y isn't
        self.assertTrue(eval_conditions(self.long_term_user_campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.long_term_user_campaign, 'conditions', self.mrsy))

    def test_key(self):
        # Mr X. uses Gmail, but Mrs. Y doesn't
        self.assertFalse(eval_conditions(self.non_gmail_users_campaign, 'conditions', self.mrx))
        self.assertTrue(eval_conditions(self.non_gmail_users_campaign, 'conditions', self.mrsy))

    def test_nested_condlists(self):
        # Mr. X is a long-term member, but Mrs. Y isn't
        # Even though they both use either Gmail or Yahoo!, only Mr. X is targeted
        self.assertTrue(eval_conditions(self.long_term_gmail_yahoo_user_campaign, 'conditions', self.mrx))
        self.assertFalse(eval_conditions(self.long_term_gmail_yahoo_user_campaign, 'conditions', self.mrsy))
