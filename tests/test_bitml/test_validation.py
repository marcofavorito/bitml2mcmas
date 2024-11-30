"""Tests for the bitml.validation module."""

from collections.abc import Sequence
from decimal import Decimal

import pytest

from bitml2mcmas.bitml.ast import (
    BitMLDepositPrecondition,
    BitMLExpression,
    BitMLParticipant,
    BitMLPreconditionExpression,
    BitMLPutExpression,
    BitMLRevealExpression,
    BitMLSecretPrecondition,
    BitMLSplitBranch,
    BitMLSplitExpression,
    BitMLTransactionOutput,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.exceptions import (
    BitMLParticipantAlreadyDefinedError,
    BitMLParticipantNotDefinedError,
    BitMLSecretHashAlreadyCommitted,
    BitMLSecretIdAlreadyDefinedError,
    BitMLSecretIdNotDefinedError,
    BitMLSplitExpressionInputOutpuInconsistencyError,
    BitMLTxAlreadyLockedError,
    BitMLValidationError,
    BitMLVolatileDepositAlreadyDefined,
    BitMLVolatileDepositIdNotDefinedError,
    BitMLVolatileDepositsAlreadySpentError,
)
from bitml2mcmas.helpers.validation import DataClassFieldValidationError

PARTICIPANT_A_ID = "A"
PARTICIPANT_B_ID = "B"
PARTICIPANT_C_ID = "C"
PARTICIPANT_A = BitMLParticipant(PARTICIPANT_A_ID, "000a")
PARTICIPANT_B = BitMLParticipant(PARTICIPANT_B_ID, "000b")
PARTICIPANT_C = BitMLParticipant(PARTICIPANT_C_ID, "000c")

TX_A = BitMLTransactionOutput("txA", 0)
TX_B = BitMLTransactionOutput("txB", 0)
TX_C = BitMLTransactionOutput("txC", 0)

VOLATILE_DEPOSIT_A_ID = "vol_dep_A"
VOLATILE_DEPOSIT_B_ID = "vol_dep_B"
VOLATILE_DEPOSIT_C_ID = "vol_dep_C"

SECRET_A_ID = "secret_a"
SECRET_B_ID = "secret_b"
SECRET_C_ID = "secret_c"

SECRET_HASH_1 = "00001"
SECRET_HASH_2 = "00002"
SECRET_HASH_3 = "00003"

WITHDRAW_A = BitMLWithdrawExpression(PARTICIPANT_A_ID)
WITHDRAW_B = BitMLWithdrawExpression(PARTICIPANT_B_ID)


class BaseTestValidationError:
    participants: Sequence[BitMLParticipant]
    preconditions: Sequence[BitMLPreconditionExpression]
    contract: BitMLExpression = WITHDRAW_A

    expected_exception: type[BitMLValidationError]

    def build_contract(self) -> BitMLContract:
        return BitMLContract(self.participants, self.preconditions, self.contract)

    def test_main(self) -> None:
        with pytest.raises(self.expected_exception):
            self.build_contract()


class TestBitMLParticipantNotDefinedError(BaseTestValidationError):
    participants = []
    preconditions = []

    expected_exception = BitMLParticipantNotDefinedError


class TestBitMLParticipantAlreadyDefinedError(BaseTestValidationError):
    participants = [PARTICIPANT_A, PARTICIPANT_A]
    preconditions = []

    expected_exception = BitMLParticipantAlreadyDefinedError


class TestBitMLTxAlreadyLockedError(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = [
        BitMLDepositPrecondition(PARTICIPANT_A_ID, Decimal(1), TX_A),
        BitMLDepositPrecondition(PARTICIPANT_A_ID, Decimal(1), TX_A),
    ]

    expected_exception = BitMLTxAlreadyLockedError


class TestBitMLVolatileDepositIdNotDefinedError(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = []
    contract = BitMLPutExpression([VOLATILE_DEPOSIT_A_ID], WITHDRAW_A)

    expected_exception = BitMLVolatileDepositIdNotDefinedError


class TestBitMLVolatileDepositAlreadyDefined(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = [
        BitMLVolatileDepositPrecondition(
            PARTICIPANT_A_ID, VOLATILE_DEPOSIT_A_ID, Decimal(1), TX_A
        ),
        BitMLVolatileDepositPrecondition(
            PARTICIPANT_A_ID, VOLATILE_DEPOSIT_A_ID, Decimal(1), TX_B
        ),
    ]

    expected_exception = BitMLVolatileDepositAlreadyDefined


class TestBitMLSecretIdAlreadyDefinedError(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = [
        BitMLSecretPrecondition(PARTICIPANT_A_ID, SECRET_A_ID, SECRET_HASH_1),
        BitMLSecretPrecondition(PARTICIPANT_A_ID, SECRET_A_ID, SECRET_HASH_2),
    ]

    expected_exception = BitMLSecretIdAlreadyDefinedError


class TestBitMLSecretHashAlreadyCommitted(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = [
        BitMLSecretPrecondition(PARTICIPANT_A_ID, SECRET_A_ID, SECRET_HASH_1),
        BitMLSecretPrecondition(PARTICIPANT_A_ID, SECRET_B_ID, SECRET_HASH_1),
    ]

    expected_exception = BitMLSecretHashAlreadyCommitted


class TestBitMLSecretIdNotDefinedError(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = []
    contract = BitMLRevealExpression([SECRET_A_ID], WITHDRAW_A)

    expected_exception = BitMLSecretIdNotDefinedError


class TestBitMLSplitExpressionInputOutpuInconsistencyError(BaseTestValidationError):
    participants = [PARTICIPANT_A, PARTICIPANT_B]
    preconditions = [BitMLDepositPrecondition(PARTICIPANT_A_ID, Decimal(1), TX_A)]
    contract = BitMLSplitExpression(
        [
            BitMLSplitBranch(Decimal("0.1"), WITHDRAW_A),
            BitMLSplitBranch(Decimal("0.1"), WITHDRAW_B),
        ]
    )

    expected_exception = BitMLSplitExpressionInputOutpuInconsistencyError


class TestBitMLVolatileDepositsAlreadySpentError(BaseTestValidationError):
    participants = [PARTICIPANT_A]
    preconditions = [
        BitMLVolatileDepositPrecondition(
            PARTICIPANT_A_ID, VOLATILE_DEPOSIT_A_ID, Decimal(1), TX_A
        )
    ]
    contract = BitMLPutExpression(
        [VOLATILE_DEPOSIT_A_ID], BitMLPutExpression([VOLATILE_DEPOSIT_A_ID], WITHDRAW_A)
    )

    expected_exception = BitMLVolatileDepositsAlreadySpentError


def test_initialization_of_participant_with_reserved_keyword() -> None:
    with pytest.raises(DataClassFieldValidationError):
        BitMLParticipant("withdraw", "00")
