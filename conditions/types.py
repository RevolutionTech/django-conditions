"""
:Created: 7 December 2014
:Author: Lucas Connors

"""

import inspect

from .conditions import Condition

__all__ = ["conditions_from_module"]


def _iscondition(cond):
    return (
        inspect.isclass(cond)
        and issubclass(cond, Condition)
        and cond.__name__ not in ["Condition", "CompareCondition"]
    )


def conditions_from_module(module):
    all_conditions = {}
    for name, condition in inspect.getmembers(module):
        if _iscondition(condition):
            condition_module = condition.module_name()
            if condition_module not in all_conditions:
                all_conditions[condition_module] = {}
            all_conditions[condition_module][condition.condstr] = condition

    return all_conditions
