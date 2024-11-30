"""Check a BitML contract is supported by our compiler."""

from functools import singledispatch

from bitml2mcmas.bitml.ast import (
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLDepositPrecondition,
    BitMLFeePrecondition,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLPutRevealIfExpression,
    BitMLRevealExpression,
    BitMLRevealIfExpression,
    BitMLSecretPrecondition,
    BitMLSplitExpression,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.exceptions import BitMLExpressionNotSupportedByCompilerError
from bitml2mcmas.helpers.misc import CaseNotHandledError


@singledispatch
def check_supported(obj: object) -> None:
    raise CaseNotHandledError(boolcond_to_string.__name__, obj)  # type: ignore[attr-defined]


def _raise_not_supported(cls: type) -> None:
    raise BitMLExpressionNotSupportedByCompilerError(cls)


@check_supported.register
def _check_supported_contract(contract: BitMLContract) -> None:
    for precondition in contract.preconditions:
        check_supported(precondition)

    check_supported(contract.contract_root)


@check_supported.register
def _check_supported_deposit_precondition(
    precondition: BitMLDepositPrecondition,
) -> None:
    pass


@check_supported.register
def _check_supported_volatile_deposit_precondition(
    precondition: BitMLVolatileDepositPrecondition,
) -> None:
    pass


@check_supported.register
def _check_supported_fee_precondition(precondition: BitMLFeePrecondition) -> None:
    raise BitMLExpressionNotSupportedByCompilerError(precondition)


@check_supported.register
def _check_secret_precondition(precondition: BitMLSecretPrecondition) -> None:
    pass


@check_supported.register
def _check_bitml_withdraw_expression(expr: BitMLWithdrawExpression) -> None:
    pass


@check_supported.register
def _check_bitml_after_expression(expr: BitMLAfterExpression) -> None:
    check_supported(expr.branch)


@check_supported.register
def _check_bitml_choice_expression(expr: BitMLChoiceExpression) -> None:
    for choice in expr.choices:
        check_supported(choice)


@check_supported.register
def _check_bitml_authorization_expression(expr: BitMLAuthorizationExpression) -> None:
    check_supported(expr.branch)


@check_supported.register
def _check_bitml_split_expression(expr: BitMLSplitExpression) -> None:
    for split_branch in expr.branches:
        check_supported(split_branch.branch)


@check_supported.register
def _check_bitml_put_expression(expr: BitMLPutExpression) -> None:
    check_supported(expr.branch)


@check_supported.register
def _check_bitml_putreveal_expression(expr: BitMLPutRevealExpression) -> None:
    check_supported(expr.branch)


@check_supported.register
def _check_bitml_putrevealif_expression(expr: BitMLPutRevealIfExpression) -> None:
    _raise_not_supported(type(expr))


@check_supported.register
def _check_bitml_revealif_expression(expr: BitMLRevealIfExpression) -> None:
    _raise_not_supported(type(expr))


@check_supported.register
def _check_bitml_reveal_expression(expr: BitMLRevealExpression) -> None:
    check_supported(expr.branch)
