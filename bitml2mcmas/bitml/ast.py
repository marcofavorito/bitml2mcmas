"""Core abstractions for the BitML abstract syntax tree."""

import dataclasses
from collections.abc import Sequence
from typing import Annotated, Union, cast

from bitml2mcmas.bitml.custom_types import HexString, Name, TermString
from bitml2mcmas.helpers.validation import (
    InstanceOf,
    NonNegativeDecimal,
    NonNegativeInt,
    SequenceConstraint,
    TypeIs,
    _BaseDataClass,
)


@dataclasses.dataclass(frozen=True)
class BitMLParticipant(_BaseDataClass):
    """A BitML participant."""

    identifier: Name
    pubkey: HexString


@dataclasses.dataclass(frozen=True)
class BitMLTransactionOutput(_BaseDataClass):
    """A BitML transaction."""

    tx_identifier: Name
    tx_output_index: NonNegativeInt


BitMLDefinition = Union[BitMLParticipant]


@dataclasses.dataclass(frozen=True)
class BitMLDepositPrecondition(_BaseDataClass):
    participant_id: Name
    amount: NonNegativeDecimal
    tx: Annotated[BitMLTransactionOutput, TypeIs(BitMLTransactionOutput)]


@dataclasses.dataclass(frozen=True)
class BitMLVolatileDepositPrecondition(_BaseDataClass):
    participant_id: Name
    deposit_id: TermString
    amount: NonNegativeDecimal
    tx: Annotated[BitMLTransactionOutput, TypeIs(BitMLTransactionOutput)]


@dataclasses.dataclass(frozen=True)
class BitMLFeePrecondition(_BaseDataClass):
    participant_id: Name
    fee_amount: NonNegativeDecimal
    tx: Annotated[BitMLTransactionOutput, TypeIs(BitMLTransactionOutput)]


BitMLDeposit = Union[
    BitMLDepositPrecondition, BitMLVolatileDepositPrecondition, BitMLFeePrecondition
]


@dataclasses.dataclass(frozen=True)
class BitMLSecretPrecondition(_BaseDataClass):
    participant_id: Name
    secret_id: TermString
    secret_hash: HexString


BitMLPreconditionExpression = Union[
    BitMLDeposit,
    BitMLSecretPrecondition,
]


class _BaseExpression(_BaseDataClass):
    def __add__(self, other: "BitMLAtom") -> "Plus":
        return Plus(cast(BitMLAtom, self), other)  # type: ignore[call-arg]

    def __sub__(self, other: "BitMLAtom") -> "Minus":
        return Minus(cast(BitMLAtom, self), other)  # type: ignore[call-arg]


@dataclasses.dataclass(frozen=True)
class BitMLExpressionInt(_BaseExpression):
    value: int


@dataclasses.dataclass(frozen=True)
class BitMLExpressionSecret(_BaseExpression):
    secret_id: TermString


BitMLAtom = Union[BitMLExpressionInt, BitMLExpressionSecret]


class _BasePredicate(_BaseDataClass):
    def __and__(self, other: "BitMLPredicate") -> "BitMLPredicate":
        return And(cast(BitMLPredicate, self), other)  # type: ignore[call-arg]

    def __or__(self, other: "BitMLPredicate") -> "BitMLPredicate":
        return Or(cast(BitMLPredicate, self), other)  # type: ignore[call-arg]

    def __invert__(self) -> "BitMLPredicate":
        return Not(cast(BitMLPredicate, self))  # type: ignore[call-arg]


@dataclasses.dataclass(frozen=True)
class _BinaryExpression(_BaseExpression):
    left: Annotated["Expression", InstanceOf(_BaseExpression)]
    right: Annotated["Expression", InstanceOf(_BaseExpression)]


@dataclasses.dataclass(frozen=True)
class Plus(_BinaryExpression):
    pass


@dataclasses.dataclass(frozen=True)
class Minus(_BinaryExpression):
    pass


Expression = Union[Plus, Minus, BitMLAtom]


@dataclasses.dataclass(frozen=True)
class _BinaryPredicate(_BasePredicate):
    left: Annotated[Expression, TypeIs(Expression)]
    right: Annotated[Expression, TypeIs(Expression)]


@dataclasses.dataclass(frozen=True)
class EqualTo(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class NotEqualTo(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class LessThan(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class LessThanOrEqual(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class GreaterThan(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class GreaterThanOrEqual(_BinaryPredicate):
    pass


@dataclasses.dataclass(frozen=True)
class Between(_BasePredicate):
    arg: Annotated[BitMLAtom, TypeIs(BitMLAtom)]
    left: Annotated[Expression, TypeIs(Expression)]
    right: Annotated[Expression, TypeIs(Expression)]


@dataclasses.dataclass(frozen=True)
class Not(_BasePredicate):
    arg: Annotated["BitMLPredicate", InstanceOf(_BasePredicate)]


@dataclasses.dataclass(frozen=True)
class _BooleanConnectivePredicate(_BasePredicate):
    left: Annotated["BitMLPredicate", InstanceOf(_BasePredicate)]
    right: Annotated["BitMLPredicate", InstanceOf(_BasePredicate)]


@dataclasses.dataclass(frozen=True)
class And(_BooleanConnectivePredicate):
    pass


@dataclasses.dataclass(frozen=True)
class Or(_BooleanConnectivePredicate):
    pass


BitMLPredicate = Union[
    Expression,
    EqualTo,
    NotEqualTo,
    LessThan,
    LessThanOrEqual,
    GreaterThan,
    GreaterThanOrEqual,
    Between,
    Not,
    And,
    Or,
]


class _BaseBitMLExpression(_BaseDataClass):
    pass


@dataclasses.dataclass(frozen=True)
class BitMLWithdrawExpression(_BaseBitMLExpression):
    participant_id: Name


@dataclasses.dataclass(frozen=True)
class BitMLAfterExpression(_BaseBitMLExpression):
    timeout: NonNegativeInt
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLChoiceExpression(_BaseBitMLExpression):
    choices: Annotated[
        Sequence["BitMLExpression"],
        SequenceConstraint(min_items=2, item_type=_BaseBitMLExpression),
    ]


@dataclasses.dataclass(frozen=True)
class BitMLAuthorizationExpression(_BaseBitMLExpression):
    participant_id: Name
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLSplitBranch(_BaseDataClass):
    amount: NonNegativeDecimal
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLSplitExpression(_BaseBitMLExpression):
    branches: Annotated[
        Sequence[BitMLSplitBranch],
        SequenceConstraint(min_items=2, item_type=BitMLSplitBranch),
    ]


@dataclasses.dataclass(frozen=True)
class BitMLPutExpression(_BaseBitMLExpression):
    deposit_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(unique_items=True, item_type=TermString),
    ]
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLPutRevealExpression(_BaseBitMLExpression):
    deposit_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(unique_items=True, item_type=TermString),
    ]
    secret_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(min_items=1, unique_items=True, item_type=TermString),
    ]
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLPutRevealIfExpression(_BaseBitMLExpression):
    deposit_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(unique_items=True, item_type=TermString),
    ]
    secret_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(min_items=1, unique_items=True, item_type=TermString),
    ]
    predicate: BitMLPredicate
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLRevealIfExpression(_BaseBitMLExpression):
    secret_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(min_items=1, unique_items=True, item_type=TermString),
    ]
    predicate: BitMLPredicate
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


@dataclasses.dataclass(frozen=True)
class BitMLRevealExpression(_BaseBitMLExpression):
    secret_ids: Annotated[
        Sequence[TermString],
        SequenceConstraint(min_items=1, unique_items=True, item_type=TermString),
    ]
    branch: Annotated["BitMLExpression", InstanceOf(_BaseBitMLExpression)]


BitMLExpression = Union[
    BitMLWithdrawExpression,
    BitMLAfterExpression,
    BitMLChoiceExpression,
    BitMLAuthorizationExpression,
    BitMLSplitExpression,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLPutRevealIfExpression,
    BitMLRevealIfExpression,
    BitMLRevealExpression,
]


class BitMLException(Exception):
    pass
