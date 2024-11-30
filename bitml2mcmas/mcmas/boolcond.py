"""Classes to represent logic formulae."""

import dataclasses
from abc import ABC
from typing import Annotated, Any, Generic, Literal, TypeVar, Union, cast

from bitml2mcmas.helpers.validation import InstanceOf, TypeIs, _BaseDataClass
from bitml2mcmas.mcmas.custom_types import McmasId
from bitml2mcmas.mcmas.exceptions import McmasException


class _BaseExpression(ABC):
    @classmethod
    def __check_operation_is_valid(
        cls, arg: Any, operation: Literal["+", "-", "*", "/", "&", "|", "^", "~"]
    ) -> None:
        if not isinstance(arg, Expression):  # type: ignore[list-item,misc,arg-type]
            raise McmasException(
                f"operation {operation!r} expected argument of type {Expression!r}, got {arg!r}"
            )

    def __add__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "+")
        self.__check_operation_is_valid(other, "+")
        return AddExpr(cast(Expression, self), other)

    def __sub__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "-")
        self.__check_operation_is_valid(other, "-")
        return SubtractExpr(cast(Expression, self), other)

    def __mul__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "*")
        self.__check_operation_is_valid(other, "*")
        return MultiplyExpr(cast(Expression, self), other)

    def __truediv__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "/")
        self.__check_operation_is_valid(other, "/")
        return DivideExpr(cast(Expression, self), other)

    def __and__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "&")
        self.__check_operation_is_valid(other, "&")
        return BitAnd(cast(Expression, self), other)

    def __or__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "|")
        self.__check_operation_is_valid(other, "|")
        return BitOr(cast(Expression, self), other)

    def __xor__(self, other: "Expression") -> "Expression":
        self.__check_operation_is_valid(self, "^")
        self.__check_operation_is_valid(other, "^")
        return BitXor(cast(Expression, self), other)

    def __invert__(self) -> "Expression":
        self.__check_operation_is_valid(self, "~")
        return BitNot(cast(Expression, self))


@dataclasses.dataclass(frozen=True)
class TrueBoolValue(_BaseExpression, _BaseDataClass):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, TrueBoolValue)

    def __hash__(self) -> int:
        return hash(TrueBoolValue)


@dataclasses.dataclass(frozen=True)
class FalseBoolValue(_BaseExpression, _BaseDataClass):
    def __eq__(self, other: object) -> bool:
        return isinstance(other, FalseBoolValue)

    def __hash__(self) -> int:
        return hash(FalseBoolValue)


@dataclasses.dataclass(frozen=True)
class IntAtom(_BaseExpression):
    value: Annotated[int, TypeIs(int)]


@dataclasses.dataclass(frozen=True)
class IdAtom(_BaseExpression, _BaseDataClass):
    value: McmasId


@dataclasses.dataclass(frozen=True)
class EnvironmentIdAtom(_BaseExpression, _BaseDataClass):
    attribute: McmasId


@dataclasses.dataclass(frozen=True)
class AttributeIdAtom(_BaseExpression, _BaseDataClass):
    mcmas_object: McmasId
    attribute: McmasId


@dataclasses.dataclass(frozen=True)
class _BaseBinaryExpr(_BaseExpression, _BaseDataClass):
    left: Annotated["Expression", InstanceOf(_BaseExpression)]
    right: Annotated["Expression", InstanceOf(_BaseExpression)]


@dataclasses.dataclass(frozen=True)
class SubtractExpr(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class AddExpr(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class MultiplyExpr(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class DivideExpr(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class BitOr(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class BitXor(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class BitAnd(_BaseBinaryExpr, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class BitNot(_BaseExpression, _BaseDataClass):
    arg: Annotated["Expression", TypeIs(_BaseExpression)]


Expression = Union[
    TrueBoolValue,
    FalseBoolValue,
    IntAtom,
    IdAtom,
    EnvironmentIdAtom,
    AttributeIdAtom,
    SubtractExpr,
    AddExpr,
    MultiplyExpr,
    DivideExpr,
    BitOr,
    BitAnd,
    BitXor,
    BitNot,
]


class _BaseBoolCondition(ABC):
    @classmethod
    def __check_operation_is_valid(
        cls, arg: Any, operation: Literal["&", "|", "~"]
    ) -> None:
        if not isinstance(arg, BooleanCondition):  # type: ignore[list-item,misc,arg-type]
            raise McmasException(
                f"operation {operation!r} expected argument of type {BooleanCondition!r}, got {arg!r}"
            )

    def __and__(self, other: "BooleanCondition") -> "BooleanCondition":
        self.__check_operation_is_valid(other, "&")
        return AndBooleanCondition(cast(BooleanCondition, self), other)

    def __or__(self, other: "BooleanCondition") -> "BooleanCondition":
        self.__check_operation_is_valid(other, "&")
        return OrBooleanCondition(cast(BooleanCondition, self), other)

    def __invert__(self) -> "BooleanCondition":
        self.__check_operation_is_valid(self, "~")
        return NotBooleanCondition(cast(BooleanCondition, self))


@dataclasses.dataclass(frozen=True)
class _BinaryBoolCondition(_BaseBoolCondition, _BaseDataClass):
    left: Annotated[Expression, TypeIs(Expression)]
    right: Annotated[Expression, TypeIs(Expression)]


@dataclasses.dataclass(frozen=True)
class EqualTo(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class NotEqualTo(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class LessThan(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class LessThanOrEqual(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class GreaterThan(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class GreaterThanOrEqual(_BinaryBoolCondition, _BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class ActionEqualToConstraint(_BaseBoolCondition, _BaseDataClass):
    action_value: McmasId


@dataclasses.dataclass(frozen=True)
class AgentActionEqualToConstraint(_BaseBoolCondition, _BaseDataClass):
    agent: McmasId
    action_value: McmasId


@dataclasses.dataclass(frozen=True)
class EnvironmentActionEqualToConstraint(_BaseBoolCondition, _BaseDataClass):
    action_value: McmasId


class _BaseConnectiveBooleanCondition(_BaseBoolCondition):
    pass


OperandType = TypeVar("OperandType", bound="BooleanCondition")


@dataclasses.dataclass(frozen=True)
class NotBooleanCondition(
    _BaseConnectiveBooleanCondition, _BaseDataClass, Generic[OperandType]
):
    arg: Annotated[
        OperandType,
        InstanceOf(_BaseBoolCondition),
    ]


@dataclasses.dataclass(frozen=True)
class AndBooleanCondition(
    _BaseConnectiveBooleanCondition, _BaseDataClass, Generic[OperandType]
):
    left: Annotated[
        OperandType,
        InstanceOf(_BaseBoolCondition),
    ]
    right: Annotated[
        OperandType,
        InstanceOf(_BaseBoolCondition),
    ]


@dataclasses.dataclass(frozen=True)
class OrBooleanCondition(
    _BaseConnectiveBooleanCondition, _BaseDataClass, Generic[OperandType]
):
    left: Annotated[
        "BooleanCondition",
        InstanceOf(_BaseBoolCondition),
    ]
    right: Annotated[
        "BooleanCondition",
        InstanceOf(_BaseBoolCondition),
    ]


BooleanCondition = Union[
    EqualTo,
    NotEqualTo,
    LessThan,
    LessThanOrEqual,
    GreaterThan,
    GreaterThanOrEqual,
    ActionEqualToConstraint,
    AgentActionEqualToConstraint,
    EnvironmentActionEqualToConstraint,
    NotBooleanCondition,
    AndBooleanCondition,
    OrBooleanCondition,
]
