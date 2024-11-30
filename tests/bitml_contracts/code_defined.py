from decimal import Decimal

import pytest

from bitml2mcmas.bitml.ast import (
    And,
    Between,
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLDepositPrecondition,
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
from bitml2mcmas.bitml.core import BitMLContract


@pytest.fixture(scope="session")
def bitml_contracts_examples_escrow() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0a"),
            BitMLParticipant(identifier="B", pubkey="0b"),
            BitMLParticipant(identifier="M", pubkey="0e"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLAuthorizationExpression(
                    participant_id="A",
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
                BitMLAuthorizationExpression(
                    participant_id="B",
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLAuthorizationExpression(
                    participant_id="A",
                    branch=BitMLSplitExpression(
                        branches=(
                            BitMLSplitBranch(
                                amount=Decimal("1"),
                                branch=BitMLWithdrawExpression(participant_id="M"),
                            ),
                            BitMLSplitBranch(
                                amount=Decimal("1"),
                                branch=BitMLChoiceExpression(
                                    choices=(
                                        BitMLAuthorizationExpression(
                                            participant_id="M",
                                            branch=BitMLWithdrawExpression(
                                                participant_id="A"
                                            ),
                                        ),
                                        BitMLAuthorizationExpression(
                                            participant_id="M",
                                            branch=BitMLWithdrawExpression(
                                                participant_id="B"
                                            ),
                                        ),
                                    )
                                ),
                            ),
                        )
                    ),
                ),
                BitMLAuthorizationExpression(
                    participant_id="B",
                    branch=BitMLSplitExpression(
                        branches=(
                            BitMLSplitBranch(
                                amount=Decimal("1"),
                                branch=BitMLWithdrawExpression(participant_id="M"),
                            ),
                            BitMLSplitBranch(
                                amount=Decimal("1"),
                                branch=BitMLChoiceExpression(
                                    choices=(
                                        BitMLAuthorizationExpression(
                                            participant_id="M",
                                            branch=BitMLWithdrawExpression(
                                                participant_id="A"
                                            ),
                                        ),
                                        BitMLAuthorizationExpression(
                                            participant_id="M",
                                            branch=BitMLWithdrawExpression(
                                                participant_id="B"
                                            ),
                                        ),
                                    )
                                ),
                            ),
                        )
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_examples_mutual_tc() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0a"),
            BitMLParticipant(identifier="B", pubkey="0b"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
            BitMLSecretPrecondition(
                participant_id="B", secret_id="b1", secret_hash="0001b"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealExpression(
                    secret_ids=("a1",),
                    branch=BitMLChoiceExpression(
                        choices=(
                            BitMLRevealExpression(
                                secret_ids=("b1",),
                                branch=BitMLSplitExpression(
                                    branches=(
                                        BitMLSplitBranch(
                                            amount=Decimal("1"),
                                            branch=BitMLWithdrawExpression(
                                                participant_id="A"
                                            ),
                                        ),
                                        BitMLSplitBranch(
                                            amount=Decimal("1"),
                                            branch=BitMLWithdrawExpression(
                                                participant_id="B"
                                            ),
                                        ),
                                    )
                                ),
                            ),
                            BitMLAfterExpression(
                                timeout=2,
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                        )
                    ),
                ),
                BitMLAfterExpression(
                    timeout=1, branch=BitMLWithdrawExpression(participant_id="B")
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_examples_timed_commitment() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0a"),
            BitMLParticipant(identifier="B", pubkey="0b"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealExpression(
                    secret_ids=("a1",),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLAfterExpression(
                    timeout=1, branch=BitMLWithdrawExpression(participant_id="B")
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_auth_ambiguity() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
            BitMLParticipant(
                identifier="B1",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A",
                secret_id="a",
                secret_hash="ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb",
            ),
            BitMLSecretPrecondition(
                participant_id="A",
                secret_id="a1",
                secret_hash="ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bc",
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealExpression(
                    secret_ids=("a",),
                    branch=BitMLAuthorizationExpression(
                        participant_id="B1",
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLRevealExpression(
                    secret_ids=("a1",),
                    branch=BitMLAuthorizationExpression(
                        participant_id="B",
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_bitml_test2() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA1", tx_output_index=0),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="B",
                deposit_id="txa",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txVA", tx_output_index=2),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="00a"
            ),
        ],
        contract=BitMLAuthorizationExpression(
            participant_id="A",
            branch=BitMLAuthorizationExpression(
                participant_id="B",
                branch=BitMLAfterExpression(
                    timeout=10,
                    branch=BitMLPutRevealExpression(
                        deposit_ids=("txa",),
                        secret_ids=("a",),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_bitml_test3() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA1", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("2"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLAuthorizationExpression(
            participant_id="A",
            branch=BitMLAuthorizationExpression(
                participant_id="B",
                branch=BitMLAfterExpression(
                    timeout=30,
                    branch=BitMLAfterExpression(
                        timeout=20, branch=BitMLWithdrawExpression(participant_id="B")
                    ),
                ),
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_bitml_test4() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA1", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("2"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLAuthorizationExpression(
                    participant_id="B",
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLAfterExpression(
                    timeout=30, branch=BitMLWithdrawExpression(participant_id="B")
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_split_test() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("4"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            )
        ],
        contract=BitMLSplitExpression(
            branches=(
                BitMLSplitBranch(
                    amount=Decimal("2"),
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
                BitMLSplitBranch(
                    amount=Decimal("2"),
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_8p() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
            BitMLParticipant(
                identifier="C",
                pubkey="03e969a9e8080b7515d4bbeaf253978b33226dd3c4fbc987d9b67fb2e5380cca9f",
            ),
            BitMLParticipant(
                identifier="D",
                pubkey="033ed7a4e8386a38333d6b7db03f532edece48ef3160688d73091644ecf0754910",
            ),
            BitMLParticipant(
                identifier="E",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="F",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af31",
            ),
            BitMLParticipant(
                identifier="G",
                pubkey="03e969a9e8080b7515d4bbeaf253978b33226dd3c4fbc987d9b67fb2e5380cca9d",
            ),
            BitMLParticipant(
                identifier="H",
                pubkey="033ed7a4e8386a38333d6b7db03f532edece48ef3160688d73091644ecf0754911",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("7"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("7"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="C",
                amount=Decimal("7"),
                tx=BitMLTransactionOutput(tx_identifier="txC", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="D",
                amount=Decimal("7"),
                tx=BitMLTransactionOutput(tx_identifier="txD", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A",
                secret_id="a1",
                secret_hash="c51b66bced5e4491001bd702669770dccf440982",
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealIfExpression(
                    secret_ids=("a1",),
                    predicate=EqualTo(
                        left=BitMLExpressionSecret(secret_id="a1"),
                        right=BitMLExpressionInt(value=0),
                    ),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLAfterExpression(
                    timeout=10, branch=BitMLWithdrawExpression(participant_id="A")
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_auth() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe0",
            ),
            BitMLParticipant(
                identifier="A1",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="A2",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe2",
            ),
            BitMLParticipant(
                identifier="A3",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe3",
            ),
            BitMLParticipant(
                identifier="A4",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe4",
            ),
            BitMLParticipant(
                identifier="A5",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe5",
            ),
            BitMLParticipant(
                identifier="A6",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe6",
            ),
            BitMLParticipant(
                identifier="A7",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe7",
            ),
            BitMLParticipant(
                identifier="A8",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe8",
            ),
            BitMLParticipant(
                identifier="A9",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe9",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            )
        ],
        contract=BitMLAuthorizationExpression(
            participant_id="A1",
            branch=BitMLAuthorizationExpression(
                participant_id="A2",
                branch=BitMLAuthorizationExpression(
                    participant_id="A3",
                    branch=BitMLAuthorizationExpression(
                        participant_id="A4",
                        branch=BitMLAuthorizationExpression(
                            participant_id="A5",
                            branch=BitMLAuthorizationExpression(
                                participant_id="A6",
                                branch=BitMLAuthorizationExpression(
                                    participant_id="A7",
                                    branch=BitMLAuthorizationExpression(
                                        participant_id="A8",
                                        branch=BitMLAuthorizationExpression(
                                            participant_id="A9",
                                            branch=BitMLWithdrawExpression(
                                                participant_id="A"
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_multiple_secrets() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="aaa"
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="b", secret_hash="bbb"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealIfExpression(
                    secret_ids=("a", "b"),
                    predicate=Not(
                        arg=LessThan(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionSecret(secret_id="b"),
                        )
                    ),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLRevealIfExpression(
                    secret_ids=("a", "b"),
                    predicate=LessThan(
                        left=BitMLExpressionSecret(secret_id="a"),
                        right=Minus(
                            left=BitMLExpressionSecret(secret_id="b"),
                            right=BitMLExpressionInt(value=1),
                        ),
                    ),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_put() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="B",
                deposit_id="txb",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txVA", tx_output_index=2),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="B",
                deposit_id="txb2",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txVB", tx_output_index=2),
            ),
        ],
        contract=BitMLPutExpression(
            deposit_ids=("txb", "txb2"),
            branch=BitMLWithdrawExpression(participant_id="A"),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_revealif_complex_condition() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
            BitMLParticipant(
                identifier="C",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af31",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="000a"
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("0"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="B", secret_id="b", secret_hash="000b"
            ),
            BitMLSecretPrecondition(
                participant_id="C", secret_id="c", secret_hash="000c"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealIfExpression(
                    secret_ids=("a", "b"),
                    predicate=Or(
                        left=GreaterThanOrEqual(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=1),
                        ),
                        right=Between(
                            arg=BitMLExpressionSecret(secret_id="a"),
                            left=BitMLExpressionInt(value=0),
                            right=Plus(
                                left=BitMLExpressionSecret(secret_id="a"),
                                right=BitMLExpressionInt(value=1),
                            ),
                        ),
                    ),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLRevealIfExpression(
                    secret_ids=("b", "c"),
                    predicate=And(
                        left=GreaterThan(
                            left=BitMLExpressionSecret(secret_id="b"),
                            right=BitMLExpressionSecret(secret_id="c"),
                        ),
                        right=LessThanOrEqual(
                            left=BitMLExpressionSecret(secret_id="b"),
                            right=BitMLExpressionSecret(secret_id="c"),
                        ),
                    ),
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_secrets_split() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="aaa"
            ),
        ],
        contract=BitMLSplitExpression(
            branches=(
                BitMLSplitBranch(
                    amount=Decimal("0.5"),
                    branch=BitMLChoiceExpression(
                        choices=(
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=EqualTo(
                                    left=BitMLExpressionSecret(secret_id="a"),
                                    right=BitMLExpressionInt(value=1),
                                ),
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=NotEqualTo(
                                    left=BitMLExpressionSecret(secret_id="a"),
                                    right=BitMLExpressionInt(value=2),
                                ),
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                        )
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.5"),
                    branch=BitMLRevealExpression(
                        secret_ids=("a",),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_secrets() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
            BitMLParticipant(
                identifier="C",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af31",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="000a"
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("0"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="B", secret_id="b", secret_hash="000b"
            ),
            BitMLSecretPrecondition(
                participant_id="C", secret_id="c", secret_hash="000c"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLPutRevealExpression(
                    deposit_ids=(),
                    secret_ids=("a",),
                    branch=BitMLSplitExpression(
                        branches=(
                            BitMLSplitBranch(
                                amount=Decimal("0.5"),
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                            BitMLSplitBranch(
                                amount=Decimal("0.5"),
                                branch=BitMLWithdrawExpression(participant_id="B"),
                            ),
                        )
                    ),
                ),
                BitMLPutRevealExpression(
                    deposit_ids=(),
                    secret_ids=("b", "c"),
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_secrets2() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
            BitMLParticipant(
                identifier="B1",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="aaa"
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLRevealIfExpression(
                    secret_ids=("a",),
                    predicate=Not(
                        arg=LessThan(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=5),
                        )
                    ),
                    branch=BitMLChoiceExpression(
                        choices=(
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=Not(
                                    arg=LessThan(
                                        left=BitMLExpressionSecret(secret_id="a"),
                                        right=BitMLExpressionInt(value=10),
                                    )
                                ),
                                branch=BitMLAuthorizationExpression(
                                    participant_id="B",
                                    branch=BitMLWithdrawExpression(participant_id="A"),
                                ),
                            ),
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=LessThan(
                                    left=BitMLExpressionSecret(secret_id="a"),
                                    right=BitMLExpressionInt(value=7),
                                ),
                                branch=BitMLAuthorizationExpression(
                                    participant_id="B1",
                                    branch=BitMLWithdrawExpression(participant_id="A"),
                                ),
                            ),
                        )
                    ),
                ),
                BitMLRevealIfExpression(
                    secret_ids=("a",),
                    predicate=LessThan(
                        left=BitMLExpressionSecret(secret_id="a"),
                        right=BitMLExpressionInt(value=4),
                    ),
                    branch=BitMLChoiceExpression(
                        choices=(
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=LessThan(
                                    left=BitMLExpressionSecret(secret_id="a"),
                                    right=BitMLExpressionInt(value=7),
                                ),
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                            BitMLRevealIfExpression(
                                secret_ids=("a",),
                                predicate=NotEqualTo(
                                    left=BitMLExpressionSecret(secret_id="a"),
                                    right=BitMLExpressionInt(value=5),
                                ),
                                branch=BitMLWithdrawExpression(participant_id="A"),
                            ),
                        )
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_split_5secrets() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("5"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="aaa1"
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a2", secret_hash="aaa2"
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a3", secret_hash="aaa3"
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a5", secret_hash="aaa5"
            ),
        ],
        contract=BitMLSplitExpression(
            branches=(
                BitMLSplitBranch(
                    amount=Decimal("1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a1",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a1"),
                            right=BitMLExpressionInt(value=1),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("4"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a5",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a5"),
                            right=BitMLExpressionInt(value=5),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_split_round() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="0339bd7fade9167e09681d68c5fc80b72166fe55bbb84211fd12bde1d57247fbe1",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="034a7192e922118173906555a39f28fa1e0b65657fc7f403094da4f85701a5f809",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(
                    tx_identifier="txid2e647d8566f00a08d276488db4f4e2d9f82dd82ef161c2078963d8deb2965e35",
                    tx_output_index=1,
                ),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="aaa"
            ),
        ],
        contract=BitMLSplitExpression(
            branches=(
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=1),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=2),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=3),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=4),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=5),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=6),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=7),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=8),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=EqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=9),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
                BitMLSplitBranch(
                    amount=Decimal("0.1"),
                    branch=BitMLRevealIfExpression(
                        secret_ids=("a",),
                        predicate=NotEqualTo(
                            left=BitMLExpressionSecret(secret_id="a"),
                            right=BitMLExpressionInt(value=1),
                        ),
                        branch=BitMLWithdrawExpression(participant_id="A"),
                    ),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_volatile() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="A",
                deposit_id="x",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=1),
            ),
        ],
        contract=BitMLPutExpression(
            deposit_ids=("x",), branch=BitMLWithdrawExpression(participant_id="B")
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_original_test_volatile2() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(
                identifier="A",
                pubkey="029c5f6f5ef0095f547799cb7861488b9f4282140d59a6289fbc90c70209c1cced",
            ),
            BitMLParticipant(
                identifier="B",
                pubkey="022c3afb0b654d3c2b0e2ffdcf941eaf9b6c2f6fcf14672f86f7647fa7b817af30",
            ),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a", secret_hash="aaa"
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="A",
                deposit_id="x",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=1),
            ),
        ],
        contract=BitMLWithdrawExpression(participant_id="B"),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_after_auth_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLAfterExpression(
            timeout=1,
            branch=BitMLAuthorizationExpression(
                participant_id="A", branch=BitMLWithdrawExpression(participant_id="B")
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_after_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLAfterExpression(
            timeout=1, branch=BitMLWithdrawExpression(participant_id="B")
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_auth_reveal_after_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
        ],
        contract=BitMLAfterExpression(
            timeout=1,
            branch=BitMLRevealExpression(
                secret_ids=("a1",),
                branch=BitMLAuthorizationExpression(
                    participant_id="B",
                    branch=BitMLAfterExpression(
                        timeout=1, branch=BitMLWithdrawExpression(participant_id="A")
                    ),
                ),
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_auth_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLAuthorizationExpression(
            participant_id="A", branch=BitMLWithdrawExpression(participant_id="B")
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_choice_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLChoiceExpression(
            choices=(
                BitMLWithdrawExpression(participant_id="A"),
                BitMLWithdrawExpression(participant_id="B"),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_double_auth_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLAuthorizationExpression(
            participant_id="A",
            branch=BitMLAuthorizationExpression(
                participant_id="B", branch=BitMLWithdrawExpression(participant_id="B")
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_put_reveal_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="A",
                deposit_id="txa1",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=1),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="B",
                deposit_id="txb1",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=1),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
            BitMLSecretPrecondition(
                participant_id="B", secret_id="b1", secret_hash="0001b"
            ),
        ],
        contract=BitMLPutRevealExpression(
            deposit_ids=("txa1", "txb1"),
            secret_ids=("a1", "b1"),
            branch=BitMLWithdrawExpression(participant_id="A"),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_put_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="A",
                deposit_id="txa1",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=1),
            ),
            BitMLVolatileDepositPrecondition(
                participant_id="B",
                deposit_id="txb1",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=1),
            ),
        ],
        contract=BitMLPutExpression(
            deposit_ids=("txa1", "txb1"),
            branch=BitMLWithdrawExpression(participant_id="A"),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_reveal_choice_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
        ],
        contract=BitMLRevealExpression(
            secret_ids=("a1",),
            branch=BitMLChoiceExpression(
                choices=(
                    BitMLWithdrawExpression(participant_id="A"),
                    BitMLWithdrawExpression(participant_id="B"),
                )
            ),
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_reveal_one_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
        ],
        contract=BitMLRevealExpression(
            secret_ids=("a1",), branch=BitMLWithdrawExpression(participant_id="A")
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_reveal_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
            BitMLSecretPrecondition(
                participant_id="A", secret_id="a1", secret_hash="0001a"
            ),
            BitMLSecretPrecondition(
                participant_id="B", secret_id="b1", secret_hash="0001b"
            ),
        ],
        contract=BitMLRevealExpression(
            secret_ids=("a1", "b1"), branch=BitMLWithdrawExpression(participant_id="A")
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_split_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLSplitExpression(
            branches=(
                BitMLSplitBranch(
                    amount=Decimal("1"),
                    branch=BitMLWithdrawExpression(participant_id="A"),
                ),
                BitMLSplitBranch(
                    amount=Decimal("1"),
                    branch=BitMLWithdrawExpression(participant_id="B"),
                ),
            )
        ),
    )


@pytest.fixture(scope="session")
def bitml_contracts_tests_withdraw() -> BitMLContract:
    return BitMLContract(
        participants=(
            BitMLParticipant(identifier="A", pubkey="0"),
            BitMLParticipant(identifier="B", pubkey="1"),
        ),
        preconditions=[
            BitMLDepositPrecondition(
                participant_id="A",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txA", tx_output_index=0),
            ),
            BitMLDepositPrecondition(
                participant_id="B",
                amount=Decimal("1"),
                tx=BitMLTransactionOutput(tx_identifier="txB", tx_output_index=0),
            ),
        ],
        contract=BitMLWithdrawExpression(participant_id="A"),
    )
