"""Core abstractions for the BitML abstract syntax tree."""

from collections.abc import Sequence

from bitml2mcmas.bitml.ast import (
    BitMLExpression,
    BitMLParticipant,
    BitMLPreconditionExpression,
)
from bitml2mcmas.bitml.validation import BitMLContractValidator, _BitMLFundsCheck


class BitMLContract:
    def __init__(
        self,
        participants: Sequence[BitMLParticipant],
        preconditions: Sequence[BitMLPreconditionExpression],
        contract: BitMLExpression,
    ) -> None:
        self.__participants = participants
        self.__preconditions = preconditions
        self.__contract_root = contract

        self._check_validity()

    @property
    def participants(self) -> Sequence[BitMLParticipant]:
        return self.__participants

    @property
    def preconditions(self) -> Sequence[BitMLPreconditionExpression]:
        return self.__preconditions

    @property
    def contract_root(self) -> BitMLExpression:
        return self.__contract_root

    def _check_validity(self) -> None:
        _check_bitml_validity(self)

    def __repr__(self) -> str:
        return (
            f"BitMLContract("
            f"participants={self.participants!r}, "
            f"preconditions={self.preconditions!r}, "
            f"contract={self.contract_root!r})"
        )


def _check_bitml_validity(contract: BitMLContract) -> None:
    validator = BitMLContractValidator()
    for participant in contract.participants:
        validator.add_participant(participant)

    for precondition in contract.preconditions:
        validator.add_precondition(precondition)

    validator.check_bitml_contract_validity(contract.contract_root)
    _BitMLFundsCheck(contract).check()
