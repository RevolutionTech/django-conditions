"""
:Created: 6 December 2014
:Author: Lucas Connors

"""

__all__ = ["UndefinedConditionError", "InvalidConditionError"]


class UndefinedConditionError(NotImplementedError):
    pass


class InvalidConditionError(ValueError):
    pass
