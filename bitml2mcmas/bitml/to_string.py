"""Convert a BitML contract into string."""

from functools import singledispatch
from textwrap import indent

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
    BitMLPutRevealIfExpression,
    BitMLRevealExpression,
    BitMLRevealIfExpression,
    BitMLSecretPrecondition,
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
    _BinaryExpression,
    _BinaryPredicate,
    _BooleanConnectivePredicate,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.exceptions import BitMLDispatchError

_INDENTATION = " " * 2
LANG_BITML = "#lang bitml"


@singledispatch
def to_string(obj: object) -> str:
    raise BitMLDispatchError(obj, "BitMLExpression")


@to_string.register
def bitml_contract_to_string(contract: BitMLContract) -> str:
    header = LANG_BITML
    participants_str = "\n".join([to_string(p) for p in contract.participants])
    preconditions_str = "\n".join([to_string(prec) for prec in contract.preconditions])
    preconditions_clause_str = (
        "(pre\n" + indent(preconditions_str, _INDENTATION) + "\n)"
    )
    contract_root_str = to_string(contract.contract_root)
    return (
        f"{header}\n"
        "\n"
        f"{participants_str}\n"
        f"\n"
        "(contract\n"
        f"{indent(preconditions_clause_str, _INDENTATION)}\n"
        f"{indent(contract_root_str, _INDENTATION)}\n"
        ")\n"
    )


@to_string.register
def participant_to_string(participant: BitMLParticipant) -> str:
    return f'(participant "{participant.identifier}" "{participant.pubkey}")'


@to_string.register
def tx_to_string(tx: BitMLTransactionOutput) -> str:
    return f"{tx.tx_identifier}@{tx.tx_output_index}"


@to_string.register
def deposit_precondition(deposit: BitMLDepositPrecondition) -> str:
    return f'(deposit "{deposit.participant_id}" {deposit.amount} "{tx_to_string(deposit.tx)}")'


@to_string.register
def volatile_deposit_precondition(vol_deposit: BitMLVolatileDepositPrecondition) -> str:
    return f'(vol-deposit "{vol_deposit.participant_id}" {vol_deposit.deposit_id} {vol_deposit.amount} "{tx_to_string(vol_deposit.tx)}")'


@to_string.register
def fee_precondition(fee: BitMLFeePrecondition) -> str:
    return f'(fee "{fee.participant_id}" {fee.fee_amount} "{tx_to_string(fee.tx)}")'


@to_string.register
def secret_precondition(secret: BitMLSecretPrecondition) -> str:
    return (
        f'(secret "{secret.participant_id}" {secret.secret_id} "{secret.secret_hash}")'
    )


@to_string.register
def withdraw_to_string(expr: BitMLWithdrawExpression) -> str:
    return f'(withdraw "{expr.participant_id}")'


@to_string.register
def after_to_string(expr: BitMLAfterExpression) -> str:
    return f"(after {expr.timeout} {to_string(expr.branch)})"


@to_string.register
def choice_to_string(expr: BitMLChoiceExpression) -> str:
    choices_str = "\n".join([to_string(branch) for branch in expr.choices])
    return "(choice\n" + indent(choices_str, prefix=_INDENTATION) + "\n)"


@to_string.register
def authorization_to_string(expr: BitMLAuthorizationExpression) -> str:
    return f'(auth "{expr.participant_id}" {to_string(expr.branch)})'


@to_string.register
def split_to_string(expr: BitMLSplitExpression) -> str:
    body = "\n".join(
        [
            f"({split_branch.amount} -> {to_string(split_branch.branch)})"
            for split_branch in expr.branches
        ]
    )
    return "(split\n" + indent(body, prefix=_INDENTATION) + "\n)"


@to_string.register
def put_to_string(expr: BitMLPutExpression) -> str:
    deposit_ids_str = "(" + " ".join(expr.deposit_ids) + ")"
    return f"(put {deposit_ids_str} {to_string(expr.branch)})"


@to_string.register
def put_reveal_to_string(expr: BitMLPutRevealExpression) -> str:
    deposit_ids_str = "(" + " ".join(expr.deposit_ids) + ")"
    secret_ids_str = "(" + " ".join(expr.secret_ids) + ")"
    return f"(putreveal {deposit_ids_str} {secret_ids_str} {to_string(expr.branch)})"


@to_string.register
def put_reveal_if_to_string(expr: BitMLPutRevealIfExpression) -> str:
    deposit_ids_str = "(" + " ".join(expr.deposit_ids) + ")"
    secret_ids_str = "(" + " ".join(expr.secret_ids) + ")"
    predicate_str = to_string(expr.predicate)
    return f"(putrevealif {deposit_ids_str} {secret_ids_str} (pred {predicate_str}) {to_string(expr.branch)})"


@to_string.register
def reveal_if_to_string(expr: BitMLRevealIfExpression) -> str:
    secret_ids_str = "(" + " ".join(expr.secret_ids) + ")"
    predicate_to_string = to_string(expr.predicate)
    return f"(revealif {secret_ids_str} (pred {predicate_to_string}) {to_string(expr.branch)})"


@to_string.register
def reveal_to_string(expr: BitMLRevealExpression) -> str:
    secret_ids_str = "(" + " ".join(expr.secret_ids) + ")"
    return f"(reveal {secret_ids_str} {to_string(expr.branch)})"


@to_string.register
def atom_int_to_string(expr: BitMLExpressionInt) -> str:
    return str(expr.value)


@to_string.register
def atom_secret_to_string(expr: BitMLExpressionSecret) -> str:
    return str(expr.secret_id)


def _binary_expression_to_string(expr: _BinaryExpression, symbol: str) -> str:
    left_str = to_string(expr.left)
    right_str = to_string(expr.right)
    return f"({symbol} {left_str} {right_str})"


@to_string.register
def plus_to_string(expr: Plus) -> str:
    return _binary_expression_to_string(expr, "+")


@to_string.register
def minus_to_string(expr: Minus) -> str:
    return _binary_expression_to_string(expr, "-")


def _binary_predicate_to_string(expr: _BinaryPredicate, symbol: str) -> str:
    left_str = to_string(expr.left)
    right_str = to_string(expr.right)
    return f"({symbol} {left_str} {right_str})"


@to_string.register
def equal_to_to_string(expr: EqualTo) -> str:
    return _binary_predicate_to_string(expr, "=")


@to_string.register
def not_equal_to_to_string(expr: NotEqualTo) -> str:
    return _binary_predicate_to_string(expr, "!=")


@to_string.register
def less_than_to_string(expr: LessThan) -> str:
    return _binary_predicate_to_string(expr, "<")


@to_string.register
def less_than_or_equal_to_string(expr: LessThanOrEqual) -> str:
    return _binary_predicate_to_string(expr, "<=")


@to_string.register
def greater_than_to_string(expr: GreaterThan) -> str:
    return _binary_predicate_to_string(expr, ">")


@to_string.register
def greater_than_or_equal_to_string(expr: GreaterThanOrEqual) -> str:
    return _binary_predicate_to_string(expr, ">=")


@to_string.register
def between_to_string(expr: Between) -> str:
    return f"(between {to_string(expr.arg)} {to_string(expr.left)} {to_string(expr.right)})"


@to_string.register
def not_to_string(expr: Not) -> str:
    return f"(not {to_string(expr.arg)})"


def _boolean_connective_predicate_to_string(
    expr: _BooleanConnectivePredicate, symbol: str
) -> str:
    left_str = to_string(expr.left)
    right_str = to_string(expr.right)
    return f"({symbol} {left_str} {right_str})"


@to_string.register
def and_to_string(expr: And) -> str:
    return _boolean_connective_predicate_to_string(expr, "and")


@to_string.register
def or_to_string(expr: Or) -> str:
    return _boolean_connective_predicate_to_string(expr, "or")
