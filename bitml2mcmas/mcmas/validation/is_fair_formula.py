"""Implement the validation for fair formulae."""

from functools import singledispatch
from typing import Any

from bitml2mcmas.helpers.misc import CaseNotHandledError
from bitml2mcmas.helpers.validation import _Processor
from bitml2mcmas.mcmas.exceptions import McmasValidationError
from bitml2mcmas.mcmas.formula import (
    DiamondUntilFormula,
    _BaseAtomicFormula,
    _BaseBinaryFormula,
    _BaseDiamondFormula,
    _BaseUnaryFormula,
)


class _IsFairFormula(_Processor):
    def process(self, value: Any) -> Any:
        if not is_fair_formula(value):
            raise McmasValidationError(f"object {value!r} is not a valid fair formula")
        return value


@singledispatch
def is_fair_formula(obj: object) -> bool:
    raise CaseNotHandledError(is_fair_formula.__name__, obj)  # type: ignore[attr-defined]


@is_fair_formula.register
def _is_fair_formula_unary(f: _BaseUnaryFormula) -> bool:
    return is_fair_formula(f.arg)


@is_fair_formula.register
def _is_fair_formula_binary(f: _BaseBinaryFormula) -> bool:
    return is_fair_formula(f.left) and is_fair_formula(f.right)


@is_fair_formula.register
def _is_fair_formula_atomic(f: _BaseAtomicFormula) -> bool:
    return True


@is_fair_formula.register
def _is_fair_formula_diamond(f: _BaseDiamondFormula) -> bool:
    return False


@is_fair_formula.register
def _is_fair_formula_diamond_until(f: DiamondUntilFormula) -> bool:
    return False
