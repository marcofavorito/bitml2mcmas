"""Tests for the bitml.ast module."""

from decimal import Decimal

import pytest

from bitml2mcmas.bitml.ast import (
    And,
    Between,
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLExpressionInt,
    BitMLExpressionSecret,
    BitMLFeePrecondition,
    BitMLParticipant,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLRevealExpression,
    BitMLRevealIfExpression,
    BitMLSecretPrecondition,
    BitMLSplitBranch,
    BitMLSplitExpression,
    BitMLTransactionOutput,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Minus,
    Not,
    NotEqualTo,
    Or,
    Plus,
)
from bitml2mcmas.helpers.validation import DataClassFieldValidationError


class TestBitMLParticipant:
    def test_instantiation(self) -> None:
        participant_id = "participant_id"
        participant_pubkey = "01234567"
        participant = BitMLParticipant(participant_id, participant_pubkey)
        assert participant.identifier == participant_id
        assert participant.pubkey == participant_pubkey

    def test_instantiation_with_invalid_pubkey(self) -> None:
        participant_id = "participant_id"
        invalid_participant_pubkey = "invalid_pubkey"

        with pytest.raises(DataClassFieldValidationError):
            BitMLParticipant(participant_id, invalid_participant_pubkey)

    def test_instantiation_with_invalid_identifier(self) -> None:
        participant_id = "invalid_participant_id!"
        participant_pubkey = "01234567"

        with pytest.raises(DataClassFieldValidationError):
            BitMLParticipant(participant_id, participant_pubkey)


class TestBitMLTransaction:
    def test_instantiation(self) -> None:
        transaction_id = "tx_id"
        tx_output_index = 0
        tx = BitMLTransactionOutput(transaction_id, tx_output_index)
        assert tx.tx_identifier == transaction_id
        assert tx.tx_output_index == tx_output_index

    def test_instantiation_with_invalid_tx_output_index(self) -> None:
        transaction_id = "tx_id"
        invalid_tx_output_index = -1

        with pytest.raises(DataClassFieldValidationError):
            BitMLTransactionOutput(transaction_id, invalid_tx_output_index)


class TestBitMLVolatileDepositPrecondition:
    def test_instantiation(self) -> None:
        volatile_deposit = BitMLVolatileDepositPrecondition(
            participant_id="participant_id",
            deposit_id="volatile_deposit",
            amount=Decimal("100.5"),
            tx=BitMLTransactionOutput("tx_id", 1),
        )
        assert volatile_deposit.participant_id == "participant_id"
        assert volatile_deposit.deposit_id == "volatile_deposit"
        assert volatile_deposit.amount == 100.5
        assert volatile_deposit.tx.tx_identifier == "tx_id"

    def test_instantiation_with_invalid_amount(self) -> None:
        with pytest.raises(DataClassFieldValidationError):
            BitMLVolatileDepositPrecondition(
                participant_id="participant_id",
                deposit_id="volatile_deposit",
                amount=Decimal(-100.5),
                tx=BitMLTransactionOutput("tx_id", 1),
            )


class TestBitMLFeePrecondition:
    def test_instantiation(self) -> None:
        fee_precondition = BitMLFeePrecondition(
            participant_id="participant_id",
            fee_amount=Decimal(5.0),
            tx=BitMLTransactionOutput("tx_id", 1),
        )
        assert fee_precondition.participant_id == "participant_id"
        assert fee_precondition.fee_amount == 5.0
        assert fee_precondition.tx.tx_identifier == "tx_id"

    def test_instantiation_with_invalid_fee(self) -> None:
        with pytest.raises(DataClassFieldValidationError):
            BitMLFeePrecondition(
                participant_id="participant_id",
                fee_amount=Decimal(-5.0),
                tx=BitMLTransactionOutput("tx_id", 1),
            )


class TestBitMLSecretPrecondition:
    def test_instantiation(self) -> None:
        secret_precondition = BitMLSecretPrecondition(
            participant_id="participant_id",
            secret_id="secret_id",
            secret_hash="0123456789abcdef",
        )
        assert secret_precondition.participant_id == "participant_id"
        assert secret_precondition.secret_id == "secret_id"
        assert secret_precondition.secret_hash == "0123456789abcdef"

    def test_instantiation_with_invalid_secret_bytes(self) -> None:
        with pytest.raises(DataClassFieldValidationError):
            BitMLSecretPrecondition(
                participant_id="participant_id",
                secret_id="secret_id",
                secret_hash="invalid_secret",
            )


class TestBitMLWithdrawExpression:
    def test_instantiation(self) -> None:
        identifier = "participant_id"
        withdraw_expr = BitMLWithdrawExpression(identifier)
        assert withdraw_expr.participant_id == "participant_id"


class TestBitMLAfterExpression:
    def test_instantiation(self) -> None:
        timeout = 42
        identifier = "participant_id"
        withdraw_expr = BitMLWithdrawExpression(identifier)
        after_expr = BitMLAfterExpression(timeout, withdraw_expr)

        assert after_expr.timeout == timeout
        assert after_expr.branch == withdraw_expr


class TestBitMLChoiceExpression:
    def test_instantiation(self) -> None:
        participant_1 = "p1"
        participant_2 = "p2"
        withdraw_expr_1 = BitMLWithdrawExpression(participant_1)
        withdraw_expr_2 = BitMLWithdrawExpression(participant_2)
        choice_expr = BitMLChoiceExpression([withdraw_expr_1, withdraw_expr_2])

        assert choice_expr.choices[0] == withdraw_expr_1
        assert choice_expr.choices[1] == withdraw_expr_2


class TestBitMLAuthorizationExpression:
    def test_instantiation(self) -> None:
        identifier = "participant_id"
        withdraw_expr = BitMLWithdrawExpression(identifier)
        authorization_expr = BitMLAuthorizationExpression(
            participant_id=identifier, branch=withdraw_expr
        )
        assert authorization_expr.participant_id == "participant_id"
        assert authorization_expr.branch == withdraw_expr


class TestBitMLSplitExpression:
    def test_instantiation(self) -> None:
        participant_1 = "p1"
        participant_2 = "p2"
        withdraw_expr_1 = BitMLWithdrawExpression(participant_1)
        withdraw_expr_2 = BitMLWithdrawExpression(participant_2)
        split_expr = BitMLSplitExpression(
            [
                BitMLSplitBranch(Decimal("1.0"), withdraw_expr_1),
                BitMLSplitBranch(Decimal("2.0"), withdraw_expr_2),
            ]
        )

        assert split_expr.branches[0] == BitMLSplitBranch(
            Decimal("1.0"), withdraw_expr_1
        )
        assert split_expr.branches[1] == BitMLSplitBranch(
            Decimal("2.0"), withdraw_expr_2
        )


class TestBitMLPutExpression:
    def test_instantiation(self) -> None:
        deposit_id_1 = "d1"
        deposit_id_2 = "d2"
        participant_1 = "p1"
        withdraw_expr = BitMLWithdrawExpression(participant_1)
        put_expr = BitMLPutExpression([deposit_id_1, deposit_id_2], withdraw_expr)

        assert put_expr.deposit_ids == (deposit_id_1, deposit_id_2)
        assert put_expr.branch == withdraw_expr


class TestBitMLPutRevealIfExpression:
    def test_instantiation(self) -> None:
        deposit_id_1 = "d1"
        deposit_id_2 = "d2"
        secret_id_1 = "s1"
        secret_id_2 = "s2"
        participant_1 = "p1"
        withdraw_expr = BitMLWithdrawExpression(participant_1)
        put_reveal_if_expr = BitMLPutRevealExpression(
            [deposit_id_1, deposit_id_2],
            [secret_id_1, secret_id_2],
            withdraw_expr,
        )

        assert put_reveal_if_expr.deposit_ids == (deposit_id_1, deposit_id_2)
        assert put_reveal_if_expr.secret_ids == (secret_id_1, secret_id_2)
        assert put_reveal_if_expr.branch == withdraw_expr


class TestBitMLRevealIfExpression:
    def test_instantiation(self) -> None:
        secret_id_1 = "s1"
        secret_id_2 = "s2"
        participant_1 = "p1"
        predicate = EqualTo(BitMLExpressionInt(1), BitMLExpressionSecret(secret_id_1))
        withdraw_expr = BitMLWithdrawExpression(participant_1)
        reveal_if_expr = BitMLRevealIfExpression(
            [secret_id_1, secret_id_2], predicate, withdraw_expr
        )

        assert reveal_if_expr.secret_ids == (secret_id_1, secret_id_2)
        assert reveal_if_expr.predicate == predicate
        assert reveal_if_expr.branch == withdraw_expr


class TestBitMLRevealExpression:
    def test_instantiation(self) -> None:
        secret_id_1 = "s1"
        secret_id_2 = "s2"
        participant_1 = "p1"
        withdraw_expr = BitMLWithdrawExpression(participant_1)
        reveal_if_expr = BitMLRevealExpression(
            [secret_id_1, secret_id_2], withdraw_expr
        )

        assert reveal_if_expr.secret_ids == (secret_id_1, secret_id_2)
        assert reveal_if_expr.branch == withdraw_expr


class TestLogicalPredicates:
    def test_plus_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        plus_predicate = atom_1 + atom_2

        assert isinstance(plus_predicate, Plus)
        assert plus_predicate.left == atom_1
        assert plus_predicate.right == atom_2

    def test_minus_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        minus_predicate = atom_1 - atom_2

        assert isinstance(minus_predicate, Minus)
        assert minus_predicate.left == atom_1
        assert minus_predicate.right == atom_2

    def test_equal_to_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        equal_to_predicate = EqualTo(atom_1, atom_2)

        assert isinstance(equal_to_predicate, EqualTo)
        assert equal_to_predicate.left == atom_1
        assert equal_to_predicate.right == atom_2

    def test_not_equal_to_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        not_equal_to_predicate = NotEqualTo(atom_1, atom_2)

        assert isinstance(not_equal_to_predicate, NotEqualTo)
        assert not_equal_to_predicate.left == atom_1
        assert not_equal_to_predicate.right == atom_2

    def test_less_than_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        less_than_predicate = LessThan(atom_1, atom_2)

        assert isinstance(less_than_predicate, LessThan)
        assert less_than_predicate.left == atom_1
        assert less_than_predicate.right == atom_2

    def test_less_than_or_equal_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        less_than_or_equal_predicate = LessThanOrEqual(atom_1, atom_2)

        assert isinstance(less_than_or_equal_predicate, LessThanOrEqual)
        assert less_than_or_equal_predicate.left == atom_1
        assert less_than_or_equal_predicate.right == atom_2

    def test_greater_than_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        greater_than_predicate = GreaterThan(atom_1, atom_2)

        assert isinstance(greater_than_predicate, GreaterThan)
        assert greater_than_predicate.left == atom_1
        assert greater_than_predicate.right == atom_2

    def test_greater_than_or_equal_predicate(self) -> None:
        atom_1 = BitMLExpressionInt(1)
        atom_2 = BitMLExpressionSecret("a")
        greater_than_or_equal_predicate = GreaterThanOrEqual(atom_1, atom_2)

        assert isinstance(greater_than_or_equal_predicate, GreaterThanOrEqual)
        assert greater_than_or_equal_predicate.left == atom_1
        assert greater_than_or_equal_predicate.right == atom_2

    def test_and_predicate(self) -> None:
        predicate1 = EqualTo(BitMLExpressionInt(5), BitMLExpressionInt(5))
        predicate2 = EqualTo(BitMLExpressionInt(3), BitMLExpressionInt(3))
        and_predicate = predicate1 & predicate2

        assert isinstance(and_predicate, And)
        assert and_predicate.left == predicate1
        assert and_predicate.right == predicate2

    def test_or_predicate(self) -> None:
        predicate1 = EqualTo(BitMLExpressionInt(5), BitMLExpressionInt(5))
        predicate2 = EqualTo(BitMLExpressionInt(3), BitMLExpressionInt(4))
        or_predicate = predicate1 | predicate2

        assert isinstance(or_predicate, Or)
        assert or_predicate.left == predicate1
        assert or_predicate.right == predicate2

    def test_not_predicate(self) -> None:
        predicate = EqualTo(BitMLExpressionInt(5), BitMLExpressionInt(5))
        not_predicate = ~predicate

        assert isinstance(not_predicate, Not)
        assert not_predicate.arg == predicate

    def test_between_predicate(self) -> None:
        atom = BitMLExpressionSecret("a")
        left_bound = BitMLExpressionInt(1)
        right_bound = BitMLExpressionInt(10)
        between_predicate = Between(atom, left_bound, right_bound)

        assert between_predicate.arg == atom
        assert between_predicate.left == left_bound
        assert between_predicate.right == right_bound

    def test_invalid_between_predicate(self) -> None:
        with pytest.raises(DataClassFieldValidationError):
            Between(
                BitMLExpressionSecret("invalid_atom!"),
                BitMLExpressionInt(1),
                BitMLExpressionInt(10),
            )
