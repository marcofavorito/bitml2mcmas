"""Builder pattern for BitML contracts."""

import dataclasses
from collections import ChainMap, OrderedDict
from collections.abc import Mapping, Sequence
from decimal import Decimal
from functools import singledispatchmethod
from typing import AbstractSet, cast

from bitml2mcmas.bitml.ast import (
    Between,
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLDeposit,
    BitMLDepositPrecondition,
    BitMLExpression,
    BitMLExpressionInt,
    BitMLExpressionSecret,
    BitMLFeePrecondition,
    BitMLParticipant,
    BitMLPreconditionExpression,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLPutRevealIfExpression,
    BitMLRevealExpression,
    BitMLRevealIfExpression,
    BitMLSecretPrecondition,
    BitMLSplitExpression,
    BitMLTransactionOutput,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
    Not,
    _BaseExpression,
    _BinaryExpression,
    _BinaryPredicate,
    _BooleanConnectivePredicate,
)
from bitml2mcmas.bitml.custom_types import HexString, Name, TermString
from bitml2mcmas.bitml.exceptions import (
    BitMLDispatchError,
    BitMLParticipantAlreadyDefinedError,
    BitMLParticipantNotDefinedError,
    BitMLSecretHashAlreadyCommitted,
    BitMLSecretIdAlreadyDefinedError,
    BitMLSecretIdNotDefinedError,
    BitMLSplitExpressionInputOutpuInconsistencyError,
    BitMLTxAlreadyLockedError,
    BitMLVolatileDepositAlreadyDefined,
    BitMLVolatileDepositIdNotDefinedError,
    BitMLVolatileDepositsAlreadySpentError,
)
from bitml2mcmas.helpers.misc import assert_


class _ParticipantsIndex:
    def __init__(self) -> None:
        self.__participants_by_id = OrderedDict[Name, BitMLParticipant]()

    @property
    def participants(self) -> Sequence[BitMLParticipant]:
        participants = cast(
            Sequence[BitMLParticipant], tuple(self.__participants_by_id.values())
        )
        return participants

    def reset(self) -> None:
        self.__participants_by_id.clear()

    def add_participant(self, participant: BitMLParticipant) -> None:
        participant_id = participant.identifier
        assert_(participant_id not in self.__participants_by_id)
        self.__participants_by_id[participant_id] = participant

    def check_participant_id_not_defined(self, participant_id: Name) -> None:
        if participant_id not in self.__participants_by_id:
            raise BitMLParticipantNotDefinedError(participant_id)

    def check_id_not_already_defined(self, participant: BitMLParticipant) -> None:
        if participant.identifier in self.__participants_by_id:
            raise BitMLParticipantAlreadyDefinedError(participant.identifier)


class _TxsIndex:
    def __init__(self) -> None:
        self.__tx_to_persistent_deposit = OrderedDict[
            BitMLTransactionOutput, BitMLDepositPrecondition
        ]()
        self.__tx_to_volatile_deposit = OrderedDict[
            BitMLTransactionOutput, BitMLVolatileDepositPrecondition
        ]()
        self.__volatile_deposits_by_deposit_id = OrderedDict[
            TermString, BitMLTransactionOutput
        ]()
        self.__tx_to_fee_deposit = OrderedDict[
            BitMLTransactionOutput, BitMLFeePrecondition
        ]()
        self.__tx_to_deposit = cast(
            ChainMap[BitMLTransactionOutput, BitMLDeposit],
            ChainMap(
                self.__tx_to_persistent_deposit,
                self.__tx_to_volatile_deposit,
                self.__tx_to_fee_deposit,
            ),
        )

    def reset(self) -> None:
        self.__tx_to_persistent_deposit.clear()
        self.__tx_to_volatile_deposit.clear()
        self.__tx_to_fee_deposit.clear()

    @property
    def txs(self) -> AbstractSet[BitMLTransactionOutput]:
        return self.__tx_to_deposit.keys()

    @property
    def persistent_deposits(self) -> Sequence[BitMLDepositPrecondition]:
        return cast(
            Sequence[BitMLDepositPrecondition],
            tuple(self.__tx_to_persistent_deposit.values()),
        )

    @property
    def volatile_deposits(self) -> Sequence[BitMLVolatileDepositPrecondition]:
        return cast(
            Sequence[BitMLVolatileDepositPrecondition],
            tuple(self.__tx_to_volatile_deposit.values()),
        )

    @property
    def fees(self) -> Sequence[BitMLFeePrecondition]:
        return cast(
            Sequence[BitMLFeePrecondition], tuple(self.__tx_to_fee_deposit.values())
        )

    def add_persistent_deposit(
        self, persistent_deposit: BitMLDepositPrecondition
    ) -> None:
        assert_(persistent_deposit.tx not in self.__tx_to_deposit)
        self.__tx_to_persistent_deposit[persistent_deposit.tx] = persistent_deposit

    def add_volatile_deposit(
        self, volatile_deposit: BitMLVolatileDepositPrecondition
    ) -> None:
        assert_(volatile_deposit.tx not in self.__tx_to_deposit)
        assert_(
            volatile_deposit.deposit_id not in self.__volatile_deposits_by_deposit_id
        )
        self.__tx_to_volatile_deposit[volatile_deposit.tx] = volatile_deposit
        self.__volatile_deposits_by_deposit_id[volatile_deposit.deposit_id] = (
            volatile_deposit.tx
        )

    def add_fee_deposit(self, fee_deposit: BitMLFeePrecondition) -> None:
        assert_(fee_deposit.tx not in self.__tx_to_deposit)
        self.__tx_to_fee_deposit[fee_deposit.tx] = fee_deposit

    def check_tx_not_already_locked(self, tx: BitMLTransactionOutput) -> None:
        other_deposit_precondition = self.__tx_to_deposit.get(tx, None)
        if other_deposit_precondition is not None:
            raise BitMLTxAlreadyLockedError(tx, other_deposit_precondition)

    def check_volatile_deposit_id_defined(
        self, volatile_deposit_id: TermString
    ) -> None:
        if volatile_deposit_id not in self.__volatile_deposits_by_deposit_id:
            raise BitMLVolatileDepositIdNotDefinedError(volatile_deposit_id)

    def check_volatile_deposit_id_not_already_defined(
        self, volatile_deposit_id: TermString
    ) -> None:
        if volatile_deposit_id in self.__volatile_deposits_by_deposit_id:
            raise BitMLVolatileDepositAlreadyDefined(volatile_deposit_id)


class _SecretsIndex:
    def __init__(self) -> None:
        self.__secret_id_to_secret_precondition = OrderedDict[
            TermString, BitMLSecretPrecondition
        ]()
        self.__secret_hash_to_secret_id = OrderedDict[HexString, TermString]()

    def reset(self) -> None:
        self.__secret_id_to_secret_precondition.clear()
        self.__secret_hash_to_secret_id.clear()

    @property
    def secrets(self) -> Sequence[BitMLSecretPrecondition]:
        return cast(
            Sequence[BitMLSecretPrecondition],
            tuple(self.__secret_id_to_secret_precondition.values()),
        )

    def add_secret(self, secret_precondition: BitMLSecretPrecondition) -> None:
        secret_id = secret_precondition.secret_id
        secret_hash = secret_precondition.secret_hash
        assert_(secret_id not in self.__secret_id_to_secret_precondition)
        assert_(secret_hash not in self.__secret_hash_to_secret_id)
        self.__secret_id_to_secret_precondition[secret_id] = secret_precondition
        self.__secret_hash_to_secret_id[secret_hash] = secret_id

    def check_secret_id_not_already_defined(self, secret_id: TermString) -> None:
        other_secret_precondition = self.__secret_id_to_secret_precondition.get(
            secret_id, None
        )
        if other_secret_precondition is not None:
            raise BitMLSecretIdAlreadyDefinedError(secret_id, other_secret_precondition)

    def check_secret_hash_not_already_committed(self, secret_hash: HexString) -> None:
        other_secret_id = self.__secret_hash_to_secret_id.get(secret_hash, None)
        if other_secret_id is not None:
            raise BitMLSecretHashAlreadyCommitted(secret_hash, other_secret_id)

    def check_secret_id_defined(self, secret_id: TermString) -> None:
        if secret_id not in self.__secret_id_to_secret_precondition:
            raise BitMLSecretIdNotDefinedError(secret_id)


class BitMLContractValidator:
    def __init__(self) -> None:
        self.__participants_index = _ParticipantsIndex()
        self.__txs_index = _TxsIndex()
        self.__secrets_index = _SecretsIndex()

        self.reset()

    def reset(self) -> None:
        self.__participants_index.reset()
        self.__txs_index.reset()
        self.__secrets_index.reset()

    @property
    def participants(self) -> Sequence[BitMLParticipant]:
        return self.__participants_index.participants

    def add_participant(self, participant: BitMLParticipant) -> None:
        """Add a participant to the builder."""
        self.__participants_index.check_id_not_already_defined(participant)

        self.__participants_index.add_participant(participant)

    @property
    def preconditions(self) -> tuple[BitMLPreconditionExpression, ...]:
        return tuple(
            [
                *self.__txs_index.persistent_deposits,
                *self.__txs_index.volatile_deposits,
                *self.__txs_index.fees,
                *self.__secrets_index.secrets,
            ]
        )

    @singledispatchmethod
    def add_precondition(self, precondition: object) -> None:
        raise BitMLDispatchError(precondition, "BitMLPreconditionExpression")

    @add_precondition.register
    def add_deposit_precondition(
        self, deposit_precondition: BitMLDepositPrecondition
    ) -> None:
        participant_id = deposit_precondition.participant_id
        self.__participants_index.check_participant_id_not_defined(participant_id)
        self.__txs_index.check_tx_not_already_locked(deposit_precondition.tx)

        self.__txs_index.add_persistent_deposit(deposit_precondition)

    @add_precondition.register
    def add_volatile_deposit_precondition(
        self, volatile_deposit_precondition: BitMLVolatileDepositPrecondition
    ) -> None:
        participant_id = volatile_deposit_precondition.participant_id
        self.__participants_index.check_participant_id_not_defined(participant_id)
        self.__txs_index.check_tx_not_already_locked(volatile_deposit_precondition.tx)
        self.__txs_index.check_volatile_deposit_id_not_already_defined(
            volatile_deposit_precondition.deposit_id
        )

        self.__txs_index.add_volatile_deposit(volatile_deposit_precondition)

    @add_precondition.register
    def add_fee_deposit_precondition(
        self, fee_precondition: BitMLFeePrecondition
    ) -> None:
        participant_id = fee_precondition.participant_id
        self.__participants_index.check_participant_id_not_defined(participant_id)
        self.__txs_index.check_tx_not_already_locked(fee_precondition.tx)

        self.__txs_index.add_fee_deposit(fee_precondition)

    @add_precondition.register
    def add_secret_precondition(
        self, secret_precondition: BitMLSecretPrecondition
    ) -> None:
        participant_id = secret_precondition.participant_id
        secret_id = secret_precondition.secret_id
        secret_hash = secret_precondition.secret_hash
        self.__participants_index.check_participant_id_not_defined(participant_id)
        self.__secrets_index.check_secret_id_not_already_defined(secret_id)
        self.__secrets_index.check_secret_hash_not_already_committed(secret_hash)

        self.__secrets_index.add_secret(secret_precondition)

    @singledispatchmethod
    def check_bitml_contract_validity(
        self, obj: object, recursive: bool = True
    ) -> None:
        raise BitMLDispatchError(obj, "BitMLExpression")

    @check_bitml_contract_validity.register
    def check_withdraw_expression_validity(
        self, expr: BitMLWithdrawExpression, recursive: bool = True
    ) -> None:
        participant_id = expr.participant_id
        self.__participants_index.check_participant_id_not_defined(participant_id)

    @check_bitml_contract_validity.register
    def check_after_expr_validity(
        self, expr: BitMLAfterExpression, recursive: bool = True
    ) -> None:
        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_choice_expr_validity(
        self, expr: BitMLChoiceExpression, recursive: bool = True
    ) -> None:
        if recursive:
            for choice in expr.choices:
                self.check_bitml_contract_validity(choice, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_authorization_expr_validity(
        self, expr: BitMLAuthorizationExpression, recursive: bool = True
    ) -> None:
        participant_id = expr.participant_id
        self.__participants_index.check_participant_id_not_defined(participant_id)
        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_split_expr_validity(
        self, expr: BitMLSplitExpression, recursive: bool = True
    ) -> None:
        if recursive:
            for split_branch in expr.branches:
                self.check_bitml_contract_validity(
                    split_branch.branch, recursive=recursive
                )

    @check_bitml_contract_validity.register
    def check_put_expr_validity(
        self, expr: BitMLPutExpression, recursive: bool = True
    ) -> None:
        for deposit_id in expr.deposit_ids:
            self.__txs_index.check_volatile_deposit_id_defined(deposit_id)

        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_put_reveal_expr_validity(
        self, expr: BitMLPutRevealExpression, recursive: bool = True
    ) -> None:
        for deposit_id in expr.deposit_ids:
            self.__txs_index.check_volatile_deposit_id_defined(deposit_id)

        for secret_id in expr.secret_ids:
            self.__secrets_index.check_secret_id_defined(secret_id)

        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_put_reveal_if_expr_validity(
        self, expr: BitMLPutRevealIfExpression, recursive: bool = True
    ) -> None:
        for deposit_id in expr.deposit_ids:
            self.__txs_index.check_volatile_deposit_id_defined(deposit_id)

        for secret_id in expr.secret_ids:
            self.__secrets_index.check_secret_id_defined(secret_id)

        self.check_predicate(expr.predicate)

        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_reveal_if_expr_validity(
        self, expr: BitMLRevealIfExpression, recursive: bool = True
    ) -> None:
        for secret_id in expr.secret_ids:
            self.__secrets_index.check_secret_id_defined(secret_id)

        self.check_predicate(expr.predicate)

        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @check_bitml_contract_validity.register
    def check_reveal_expr_validity(
        self, expr: BitMLRevealExpression, recursive: bool = True
    ) -> None:
        for secret_id in expr.secret_ids:
            self.__secrets_index.check_secret_id_defined(secret_id)

        if recursive:
            self.check_bitml_contract_validity(expr.branch, recursive=recursive)

    @singledispatchmethod
    def check_atom(self, obj: object) -> None:
        raise BitMLDispatchError(obj, "BitMLAtom")

    @check_atom.register
    def check_atom_int_expression(self, atom_int: BitMLExpressionInt) -> None:
        pass

    @check_atom.register
    def check_atom_secret(self, atom_secret: BitMLExpressionSecret) -> None:
        self.__secrets_index.check_secret_id_defined(atom_secret.secret_id)

    @singledispatchmethod
    def check_expression(self, obj: object) -> None:
        raise ValueError(
            f"cannot handle object {obj} of type {type(obj)} as a BitML expression"
        )

    @check_expression.register
    def check_atomic_expression(self, atom: _BaseExpression) -> None:
        self.check_atom(atom)

    @check_expression.register
    def check_binary_expressions(self, expr: _BinaryExpression) -> None:
        self.check_expression(expr.left)
        self.check_expression(expr.right)

    @singledispatchmethod
    def check_predicate(self, obj: object) -> None:
        raise BitMLDispatchError(obj, "BitMLPredicate")

    @check_predicate.register
    def check_predicate_atom(self, atom: _BaseExpression) -> None:
        self.check_atom(atom)

    @check_predicate.register
    def check_predicate_binary_expression(self, pred: _BinaryExpression) -> None:
        self.check_expression(pred)

    @check_predicate.register
    def check_binary_predicate(self, pred: _BinaryPredicate) -> None:
        self.check_predicate(pred.left)
        self.check_predicate(pred.right)

    @check_predicate.register
    def check_between_predicate(self, pred: Between) -> None:
        self.check_predicate(pred.arg)
        self.check_predicate(pred.left)
        self.check_predicate(pred.right)

    @check_predicate.register
    def check_not_predicate(self, pred: Not) -> None:
        self.check_predicate(pred.arg)

    @check_predicate.register
    def check_boolean_connective_predicate(
        self, pred: _BooleanConnectivePredicate
    ) -> None:
        self.check_predicate(pred.left)
        self.check_predicate(pred.right)


class _BitMLFundsCheck:
    @dataclasses.dataclass(frozen=True)
    class _State:
        current_contract_funds: Decimal
        available_volatile_deposits: Mapping[str, Decimal]

        def set_funds(self, amount: Decimal) -> "_BitMLFundsCheck._State":
            return _BitMLFundsCheck._State(amount, self.available_volatile_deposits)

        def spend_volatile_deposit(self, deposit_id: str) -> "_BitMLFundsCheck._State":
            assert_(deposit_id in self.available_volatile_deposits)
            new_deposits = dict(self.available_volatile_deposits)
            deposit_funds = new_deposits.pop(deposit_id)
            return _BitMLFundsCheck._State(
                self.current_contract_funds + deposit_funds, new_deposits
            )

    def __init__(self, contract: "BitMLContract") -> None:  # type: ignore[name-defined]
        total_persistent_deposits, total_volatile_deposits = self._get_total_deposits(
            contract.preconditions
        )

        self._contract = contract
        self._initial_contract_funds = total_persistent_deposits
        self._initial_available_volatile_deposits = total_volatile_deposits

    @classmethod
    def _get_total_deposits(
        cls, preconditions: Sequence[BitMLPreconditionExpression]
    ) -> tuple[Decimal, Mapping[str, Decimal]]:
        total_persistent_deposits = Decimal("0")
        available_volatile_deposits = {}
        for precondition in preconditions:
            if isinstance(precondition, BitMLDepositPrecondition):
                total_persistent_deposits += precondition.amount
            elif isinstance(precondition, BitMLVolatileDepositPrecondition):
                available_volatile_deposits[precondition.deposit_id] = (
                    precondition.amount
                )
        return total_persistent_deposits, available_volatile_deposits

    def check(self) -> None:
        initial_state = _BitMLFundsCheck._State(
            self._initial_contract_funds, self._initial_available_volatile_deposits
        )
        self.check_funds(self._contract.contract_root, initial_state)

    @singledispatchmethod
    def check_funds(self, obj: object, state: _State) -> None:
        raise BitMLDispatchError(obj, "BitMLContract")

    @check_funds.register
    def check_funds_in_withdraw_expr(
        self, expr: BitMLWithdrawExpression, state: _State
    ) -> None:
        return

    @check_funds.register
    def check_funds_in_after_expr(
        self, expr: BitMLAfterExpression, state: _State
    ) -> None:
        self.check_funds(expr.branch, state)

    @check_funds.register
    def check_funds_in_choice(self, expr: BitMLChoiceExpression, state: _State) -> None:
        for choice in expr.choices:
            self.check_funds(choice, state)

    @check_funds.register
    def check_funds_in_authorization(
        self, expr: BitMLAuthorizationExpression, state: _State
    ) -> None:
        self.check_funds(expr.branch, state)

    @check_funds.register
    def check_funds_in_split(self, expr: BitMLSplitExpression, state: _State) -> None:
        amount_branch_pairs = [
            (split_branch.amount, split_branch.branch) for split_branch in expr.branches
        ]
        amounts, branches = zip(*amount_branch_pairs, strict=False)
        total_output_amounts = sum(amounts)

        if total_output_amounts != state.current_contract_funds:
            raise BitMLSplitExpressionInputOutpuInconsistencyError(
                total_output_amounts, state.current_contract_funds
            )

        for split_branch in expr.branches:
            new_state = state.set_funds(split_branch.amount)
            self.check_funds(split_branch.branch, new_state)

    @check_funds.register
    def check_funds_in_puts(self, expr: BitMLPutExpression, state: _State) -> None:
        self._check_put_expressions(expr.deposit_ids, expr.branch, state)

    @check_funds.register
    def check_funds_in_put_reveal(
        self, expr: BitMLPutRevealExpression, state: _State
    ) -> None:
        self._check_put_expressions(expr.deposit_ids, expr.branch, state)

    @check_funds.register
    def check_funds_in_put_reveal_if(
        self, expr: BitMLPutRevealIfExpression, state: _State
    ) -> None:
        self._check_put_expressions(expr.deposit_ids, expr.branch, state)

    def _check_put_expressions(
        self, deposit_ids: Sequence[TermString], branch: BitMLExpression, state: _State
    ) -> None:
        already_spent_deposits = set(deposit_ids) - set(
            state.available_volatile_deposits.keys()
        )

        if len(already_spent_deposits) != 0:
            raise BitMLVolatileDepositsAlreadySpentError(already_spent_deposits)

        new_state = state
        for deposit_id in deposit_ids:
            new_state = new_state.spend_volatile_deposit(deposit_id)

        self.check_funds(branch, new_state)

    @check_funds.register
    def check_funds_in_reveal_if(
        self, expr: BitMLRevealIfExpression, state: _State
    ) -> None:
        self.check_funds(expr.branch, state)

    @check_funds.register
    def check_funds_in_reveal(self, expr: BitMLRevealExpression, state: _State) -> None:
        self.check_funds(expr.branch, state)
