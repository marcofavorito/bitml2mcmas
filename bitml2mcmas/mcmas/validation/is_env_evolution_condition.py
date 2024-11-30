"""Implement the validation for boolean conditions in environment evolution rules."""

from functools import singledispatch
from typing import Any, cast

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


class _IsEnvEvolutionCondition(_Processor):
    def process(self, value: Any) -> Any:
        value = cast("EvolutionRule", value)  # type: ignore[name-defined]
        if not is_env_evolution_condition(value.condition):
            raise McmasValidationError(
                f"object {value.condition!r} is not a valid boolean condition for environment evolutions"
            )
        return value


@singledispatch
def is_env_evolution_condition(obj: object) -> bool:
    raise CaseNotHandledError(is_env_evolution_condition.__name__, obj)  # type: ignore[attr-defined]


@is_env_evolution_condition.register
def _is_env_evolution_condition_and(f: AndBooleanCondition) -> bool:
    return is_env_evolution_condition(f.left) and is_env_evolution_condition(f.right)


@is_env_evolution_condition.register
def _is_env_evolution_condition_or(f: OrBooleanCondition) -> bool:
    return is_env_evolution_condition(f.left) and is_env_evolution_condition(f.right)


@is_env_evolution_condition.register
def _is_env_evolution_condition_not(f: NotBooleanCondition) -> bool:
    return is_env_evolution_condition(f.arg)


@is_env_evolution_condition.register
def _is_env_evolution_condition_binary_expression(f: _BaseBinaryExpr) -> bool:
    return is_env_evolution_condition(f.left) and is_env_evolution_condition(f.right)


@is_env_evolution_condition.register
def _is_env_evolution_condition_binary_bool_condition(f: _BinaryBoolCondition) -> bool:
    return is_env_evolution_condition(f.left) and is_env_evolution_condition(f.right)


@is_env_evolution_condition.register
def _is_env_evolution_condition_bitnot(f: BitNot) -> bool:
    return is_env_evolution_condition(f.arg)


@is_env_evolution_condition.register
def _is_env_evolution_condition_id_atom(f: IdAtom) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_int_atom(f: IntAtom) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_false_bool_value(f: FalseBoolValue) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_true_bool_value(f: TrueBoolValue) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_action_equal_to_constraint(
    f: ActionEqualToConstraint,
) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_agent_action_equal_to_constraint(
    f: AgentActionEqualToConstraint,
) -> bool:
    return True


@is_env_evolution_condition.register
def _is_env_evolution_condition_environment_action_equal_to_constraint(
    f: EnvironmentActionEqualToConstraint,
) -> bool:
    return False


@is_env_evolution_condition.register
def _is_env_evolution_condition_attribute_id_atom(f: AttributeIdAtom) -> bool:
    return False


@is_env_evolution_condition.register
def _is_env_evolution_condition_environment_id_atom(f: EnvironmentIdAtom) -> bool:
    return False
