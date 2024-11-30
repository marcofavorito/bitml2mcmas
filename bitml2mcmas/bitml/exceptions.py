"""Package-specific exceptions."""

from collections.abc import Collection
from decimal import Decimal

from bitml2mcmas.bitml.ast import (
    BitMLDeposit,
    BitMLSecretPrecondition,
    BitMLTransactionOutput,
)
from bitml2mcmas.bitml.custom_types import TermString


class BitMLException(Exception):
    pass


class BitMLValidationError(BitMLException):
    pass


class BitMLParticipantNotDefinedError(BitMLValidationError):
    def __init__(self, participant_id: str) -> None:
        super().__init__(f"participant with identifier {participant_id} is not defined")


class BitMLParticipantAlreadyDefinedError(BitMLValidationError):
    def __init__(self, participant_id: str) -> None:
        super().__init__(
            f'participant with identifier "{participant_id}" already defined'
        )


class BitMLTxAlreadyLockedError(BitMLValidationError):
    def __init__(
        self,
        tx: BitMLTransactionOutput,
        other_deposit_precondition: BitMLDeposit,
    ) -> None:
        super().__init__(
            f"transaction output {tx} already locked in deposit {other_deposit_precondition}"
        )


class BitMLVolatileDepositIdNotDefinedError(BitMLValidationError):
    def __init__(self, volatile_deposit_id: str) -> None:
        super().__init__(
            f'volatile deposit with identifier "{volatile_deposit_id}" is not defined'
        )


class BitMLVolatileDepositAlreadyDefined(BitMLValidationError):
    def __init__(self, volatile_deposit_id: str) -> None:
        super().__init__(
            f'volatile deposit with identifier "{volatile_deposit_id}" is already defined'
        )


class BitMLSecretIdAlreadyDefinedError(BitMLValidationError):
    def __init__(
        self, secret_id: str, other_secret_precondition: BitMLSecretPrecondition
    ) -> None:
        super().__init__(
            f'secret "{secret_id}" already used by precondition {other_secret_precondition}'
        )


class BitMLSecretHashAlreadyCommitted(BitMLValidationError):
    def __init__(self, secret_bytes: str, other_secret_id: str):
        super().__init__(
            f"hash \"{secret_bytes}\" already committed by secret '{other_secret_id}'"
        )


class BitMLSecretIdNotDefinedError(BitMLValidationError):
    def __init__(self, secret_id: str) -> None:
        super().__init__(f'secret with identifier "{secret_id}" is not defined')


class BitMLSplitExpressionInputOutpuInconsistencyError(BitMLValidationError):
    def __init__(self, input_amount: Decimal, output_amount: Decimal):
        super().__init__(
            f"split spends {input_amount} BTC but it receives {output_amount} BTC"
        )


class BitMLVolatileDepositsAlreadySpentError(BitMLValidationError):
    def __init__(self, already_spent_deposits: Collection[TermString]):
        super().__init__(
            f"volatile deposits already spent: {tuple(sorted(already_spent_deposits))}"
        )


class BitMLDispatchError(BitMLException):
    def __init__(self, obj: object, expected_type: type | str) -> None:
        expected_type_str = (
            expected_type
            if isinstance(expected_type, str)
            else expected_type.__class__.__name__
        )
        super().__init__(
            f"cannot handle object {obj} of type {type(obj)} as {expected_type_str}"
        )


class BitMLExpressionNotSupportedByCompilerError(BitMLException):
    def __init__(self, obj: object) -> None:
        super().__init__(
            f"BitML expression {obj!r} is not supported by the BitML-to-MCMAS compiler"
        )
