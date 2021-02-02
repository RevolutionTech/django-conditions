"""
:Created: 6 December 2014
:Author: Lucas Connors

"""

import abc

from .conditions import Condition
from .exceptions import InvalidConditionError

__all__ = ["CondList", "CondAllList", "CondAnyList", "eval_conditions"]


class CondList(list):
    """
    A list of conditions;
    Subclassed to decide how the conditions are evaluated
    """

    __metaclass__ = abc.ABCMeta

    @classmethod
    def decode_item(cls, value, definitions=None):
        if isinstance(value, dict):
            return cls.decode(value, definitions=definitions)
        else:
            return Condition.decode(value, definitions=definitions)

    @classmethod
    def decode_list(cls, value, definitions=None):
        # Validate condlist
        if not isinstance(value, list):
            raise InvalidConditionError("Condition list is invalid.")

        return [cls.decode_item(item, definitions=definitions) for item in value]

    @classmethod
    def decode(cls, value, definitions=None):
        # Validate conddict
        if value is not None and (
            not isinstance(value, dict) or "all" in value == "any" in value
        ):
            raise InvalidConditionError(
                "Conditions dict is invalid. Exactly one of 'all' or 'any' must be used."
            )

        if "all" in value:
            return CondAllList(cls.decode_list(value["all"], definitions=definitions))
        elif "any" in value:
            return CondAnyList(cls.decode_list(value["any"], definitions=definitions))

    @abc.abstractmethod
    def encode(self):
        pass

    @abc.abstractmethod
    def eval(self, user, **kwargs):
        pass


class CondAllList(CondList):
    """
    All conditions must evaluate to True
    """

    def __repr__(self):
        return f"<All: {super().__repr__()}>"

    def encode(self):
        return {
            "all": map(lambda x: x.encode(), self),
        }

    def eval(self, user, **kwargs):
        for condition in self:
            if not condition.eval(user, **kwargs):
                return False
        return True


class CondAnyList(CondList):
    """
    Any conditions may evaluate to True
    """

    def __repr__(self):
        return f"<Any: {super().__repr__()}>"

    def encode(self):
        return {
            "any": map(lambda x: x.encode(), self),
        }

    def eval(self, user, **kwargs):
        for condition in self:
            if condition.eval(user, **kwargs):
                return True
        return False


def eval_conditions(model, field_name, user, **kwargs):
    conditions = getattr(model, field_name)

    if conditions is None:
        return False

    if isinstance(conditions, dict):
        condition_definitions = model._meta.get_field(field_name).condition_definitions
        conditions = CondList.decode(conditions, definitions=condition_definitions)

    return conditions.eval(user, **kwargs)
