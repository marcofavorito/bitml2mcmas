"""Implement the validation for boolean conditions in agent protocol rules."""

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


class _IsAgentProtocolCondition(_Processor):
    def process(self, value: Any) -> Any:
        if not is_agent_protocol_condition(value):
            raise McmasValidationError(
                f"object {value!r} is not a valid boolean condition for agent protocols"
            )
        return value


@singledispatch
def is_agent_protocol_condition(obj: object) -> bool:
    raise CaseNotHandledError(is_agent_protocol_condition.__name__, obj)  # type: ignore[attr-defined]


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_and(f: AndBooleanCondition) -> bool:
    return is_agent_protocol_condition(f.left) and is_agent_protocol_condition(f.right)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_or(f: OrBooleanCondition) -> bool:
    return is_agent_protocol_condition(f.left) and is_agent_protocol_condition(f.right)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_not(f: NotBooleanCondition) -> bool:
    return is_agent_protocol_condition(f.arg)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_binary_expression(f: _BaseBinaryExpr) -> bool:
    return is_agent_protocol_condition(f.left) and is_agent_protocol_condition(f.right)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_binary_bool_condition(f: _BinaryBoolCondition) -> bool:
    return is_agent_protocol_condition(f.left) and is_agent_protocol_condition(f.right)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_bitnot(f: BitNot) -> bool:
    return is_agent_protocol_condition(f.arg)


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_id_atom(f: IdAtom) -> bool:
    return True


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_int_atom(f: IntAtom) -> bool:
    return True


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_false_bool_value(f: FalseBoolValue) -> bool:
    return True


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_true_bool_value(f: TrueBoolValue) -> bool:
    return True


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_action_equal_to_constraint(
    f: ActionEqualToConstraint,
) -> bool:
    return False


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_agent_action_equal_to_constraint(
    f: AgentActionEqualToConstraint,
) -> bool:
    return False


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_environment_action_equal_to_constraint(
    f: EnvironmentActionEqualToConstraint,
) -> bool:
    return False


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_attribute_id_atom(f: AttributeIdAtom) -> bool:
    return False


@is_agent_protocol_condition.register
def _is_agent_protocol_condition_environment_id_atom(f: EnvironmentIdAtom) -> bool:
    return True
