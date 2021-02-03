"""
:Created: 31 October 2014
:Author: Lucas Connors

"""

import abc
import inspect
import logging
import random

from .exceptions import InvalidConditionError, UndefinedConditionError

__all__ = ["Condition", "CompareCondition"]


logger = logging.getLogger("condition")


class Condition:
    """
    A condition which evaluates either to True or False
    """

    __metaclass__ = abc.ABCMeta
    keys_allowed = []  # By default, allow any key
    key_examples = []
    operand_examples = []

    def __repr__(self):
        return "{not_}{condstr}{key}{operator}".format(
            not_="NOT " if self.include_not else "",
            condstr=self.condstr,
            key=f" {self.key}" if self.key else "",
            operator=" {operator} {operand}".format(
                operator=self.operatorname, operand=self.operand
            )
            if self.operatorname
            else "",
        )

    encode = __repr__

    @classmethod
    def decode(cls, value, definitions=None):
        all_conditions = definitions or {}
        condition_definitions = {}
        for condition_group in all_conditions.values():
            condition_definitions.update(condition_group)
        include_not = False
        operator = operand = key = None
        condtuple = value.split(" ")

        # CONDSTR
        condstr = condtuple.pop(0)

        # NOT
        if condstr == "NOT":
            include_not = True
            condstr = condtuple.pop(0)

        # Evaluate CONDSTR
        try:
            condition = condition_definitions[condstr]
        except KeyError:
            raise UndefinedConditionError(f"The condition {condstr} is not defined.")

        # KEY
        if len(condtuple) > 0:
            key = condtuple.pop(0)
            if issubclass(condition, CompareCondition) and key in condition.operators():
                operator = key
                key = None
                if condition.key_required():
                    raise InvalidConditionError("A key is required in this condition.")
            elif (
                condition.key_required()
                and condition.keys_allowed
                and key not in condition.keys_allowed
            ):
                raise InvalidConditionError(
                    "The key in this condition must be one of: {keys}; found {key}".format(
                        keys=", ".join(condition.keys_allowed), key=key
                    )
                )

        # OPERATOR
        if not operator and len(condtuple) > 0:
            operator = condtuple.pop(0)

        # OPERAND
        if operator:
            operand = condtuple.pop(0)

        # Return initialized condition
        return condition(
            operator=operator, operand=operand, key=key, include_not=include_not
        )

    @classmethod
    def key_required(cls):
        try:
            eval_func = cls.eval_operand
        except AttributeError:
            eval_func = cls.eval_bool

        try:
            func_code = eval_func.__code__
        except AttributeError:  # Python 2
            func_code = eval_func.im_func.func_code

        return "key" in func_code.co_names

    @classmethod
    def key_example(cls):
        if cls.key_required():
            key = " "
            if cls.keys_allowed:
                key += random.choice(cls.keys_allowed)
            elif cls.key_examples:
                key += random.choice(cls.key_examples)
            else:
                key += "SOME_KEY_HERE"
        else:
            key = ""
        return key

    @classmethod
    def module_name(cls):
        module = inspect.getmodule(cls)
        try:
            return module.NAME
        except AttributeError:
            return module.__name__.split(".")[-1]

    @classmethod
    def help_text(cls):
        """
        Randomly generate a possible example for this condition
        """
        return "Ex. {not_}{condstr}{key}".format(
            not_=random.choice(["NOT ", ""]), condstr=cls.condstr, key=cls.key_example()
        )

    @classmethod
    def full_description(cls):
        """
        Return full description of condition (from docstring), if available
        (otherwise return help_text)
        """
        docstring = inspect.getdoc(cls)
        if docstring:
            return docstring.replace("\r", "").replace("\n", " ")
        else:
            return cls.help_text()

    def __init__(
        self, operator=None, operand=None, key=None, include_not=False, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.operatorname = operator
        self.key = key
        self.include_not = include_not

    def eval(self, user, **kwargs):
        try:
            evaluation = self.eval_bool(user, **kwargs)
        except Exception as e:
            logger.warning(
                "An exception occurred while processing a condition: {exception}".format(
                    exception=str(e)
                ),
                exc_info=True,
            )
            return False

        if self.include_not:
            return not evaluation
        else:
            return evaluation

    @abc.abstractmethod
    def eval_bool(self, user, **kwargs):
        pass


class CompareCondition(Condition):
    """
    A condition which evaluates based on a comparison
    (ie. <, ==, >=, !=, etc.)
    """

    cast_operand = float

    @classmethod
    def operators(cls):
        """
        Produce the dict of operators for this condition
        """
        if cls.cast_operand in [float, int]:
            return {
                "<": lambda x, y: x < y,
                "<=": lambda x, y: x <= y,
                "==": lambda x, y: x == y,
                "!=": lambda x, y: x != y,
                ">=": lambda x, y: x >= y,
                ">": lambda x, y: x > y,
            }
        else:
            return {}

    @classmethod
    def operand_example(cls):
        if cls.cast_operand in [float, int]:
            if cls.cast_operand == float:
                operand = round(random.uniform(0, 100), 2)
            elif cls.cast_operand == int:
                operand = random.randint(0, 100)
        elif cls.operand_examples:
            operand = random.choice(cls.operand_examples)
        else:
            operand = "SOME_OPERAND_HERE"
        return operand

    @classmethod
    def help_text(cls):
        """
        Randomly generate a possible example for this condition
        """
        normal_condition_help_text = super().help_text()

        help_text = "{normal} {operator} {operand}".format(
            normal=normal_condition_help_text,
            operator=random.choice(list(cls.operators().keys())),
            operand=cls.operand_example(),
        )
        return help_text

    def __init__(self, operator, operand, key=None, include_not=False, *args, **kwargs):
        try:
            self.operator = self.operators()[operator]
        except KeyError:
            raise InvalidConditionError(
                "The given function is not a comparison function or is unsupported."
            )
        self.operand = self.cast_operand(operand)

        super().__init__(operator, operand, key, include_not, *args, **kwargs)

    def eval_bool(self, user, **kwargs):
        return self.operator(
            self.cast_operand(self.eval_operand(user, **kwargs)), self.operand
        )

    @abc.abstractmethod
    def eval_operand(self, user, **kwargs):
        pass
