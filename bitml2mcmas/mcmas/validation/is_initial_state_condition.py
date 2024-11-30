"""Implement the validation for boolean conditions in initial states."""

from functools import singledispatch
from typing import Any

from bitml2mcmas.helpers.misc import CaseNotHandledError
from bitml2mcmas.helpers.validation import _Processor
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AgentActionEqualToConstraint,
    AndBooleanCondition,
    AttributeIdAtom,
    BitNot,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    IdAtom,
    IntAtom,
    NotBooleanCondition,
    OrBooleanCondition,
    TrueBoolValue,
    _BaseBinaryExpr,
    _BinaryBoolCondition,
)
from bitml2mcmas.mcmas.exceptions import McmasValidationError


class _IsInitialStateCondition(_Processor):
    def process(self, value: Any) -> Any:
        if not is_initial_state_condition(value):
            raise McmasValidationError(
                f"object {value!r} is not a valid boolean condition for environment protocols"
            )
        return value


@singledispatch
def is_initial_state_condition(obj: object) -> bool:
    raise CaseNotHandledError(is_initial_state_condition.__name__, obj)  # type: ignore[attr-defined]


@is_initial_state_condition.register
def _is_initial_state_condition_and(f: AndBooleanCondition) -> bool:
    return is_initial_state_condition(f.left) and is_initial_state_condition(f.right)


@is_initial_state_condition.register
def _is_initial_state_condition_or(f: OrBooleanCondition) -> bool:
    return is_initial_state_condition(f.left) and is_initial_state_condition(f.right)


@is_initial_state_condition.register
def _is_initial_state_condition_not(f: NotBooleanCondition) -> bool:
    return is_initial_state_condition(f.arg)


@is_initial_state_condition.register
def _is_initial_state_condition_equal_to(f: EqualTo) -> bool:
    left, right = f.left, f.right
    is_left_valid = isinstance(left, (AttributeIdAtom, EnvironmentIdAtom))
    is_right_valid = isinstance(
        right,
        (
            AttributeIdAtom,
            EnvironmentIdAtom,
            TrueBoolValue,
            FalseBoolValue,
            IntAtom,
            IdAtom,
        ),
    )
    return is_left_valid and is_right_valid


@is_initial_state_condition.register
def _is_initial_state_condition_binary_expression(f: _BaseBinaryExpr) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_binary_bool_condition(f: _BinaryBoolCondition) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_bitnot(f: BitNot) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_id_atom(f: IdAtom) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_int_atom(f: IntAtom) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_false_bool_value(f: FalseBoolValue) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_true_bool_value(f: TrueBoolValue) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_action_equal_to_constraint(
    f: ActionEqualToConstraint,
) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_agent_action_equal_to_constraint(
    f: AgentActionEqualToConstraint,
) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_environment_action_equal_to_constraint(
    f: EnvironmentActionEqualToConstraint,
) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_attribute_id_atom(f: AttributeIdAtom) -> bool:
    return False


@is_initial_state_condition.register
def _is_initial_state_condition_environment_id_atom(f: EnvironmentIdAtom) -> bool:
    return False
