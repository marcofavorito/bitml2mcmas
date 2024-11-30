"""Tests for the bitml.core module."""

from decimal import Decimal

from bitml2mcmas.bitml.ast import (
    BitMLDepositPrecondition,
    BitMLParticipant,
    BitMLTransactionOutput,
    BitMLWithdrawExpression,
)
from bitml2mcmas.bitml.core import BitMLContract


class TestBitMLContract:
    def test_bitml_contract_instantiation(self) -> None:
        participant_id = "participant_id"
        participant_pubkey = "0123456"
        participant = BitMLParticipant(participant_id, participant_pubkey)
        precondition = BitMLDepositPrecondition(
            participant_id, Decimal(100), BitMLTransactionOutput("tx_id", 0)
        )
        contract_expr = BitMLWithdrawExpression("participant_id")
        contract = BitMLContract([participant], [precondition], contract_expr)

        assert isinstance(contract.contract_root, BitMLWithdrawExpression)
