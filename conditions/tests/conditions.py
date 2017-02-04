import datetime

from ..conditions import Condition, CompareCondition


NAME = 'Examples'


class FullName(Condition):

    condstr = 'FULL_NAME'

    def eval_bool(self, user, **kwargs):
        return bool(user.first_name and user.last_name)


class Level(CompareCondition):

    condstr = 'LEVEL'

    def eval_operand(self, user, **kwargs):
        return user.userprofile.level


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


class EmailDomain(Condition):

    condstr = 'EMAIL_DOMAIN'

    def eval_bool(self, user, **kwargs):
        return user.email.split('@')[1] == self.key
