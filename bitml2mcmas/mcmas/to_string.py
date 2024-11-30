"""Transform a MCMAS program to string."""

from collections.abc import Callable, Collection, Sequence
from functools import singledispatch
from textwrap import indent
from typing import AbstractSet

from bitml2mcmas.helpers.misc import CaseNotHandledError
from bitml2mcmas.mcmas.ast import (
    Agent,
    BooleanVarType,
    Effect,
    EnumVarType,
    Environment,
    EvaluationRule,
    EvolutionRule,
    Group,
    IntegerRangeVarType,
    InterpretedSystem,
    Protocol,
    ProtocolRule,
    VarDefinition,
    _EnvRedStatesDef,
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AddExpr,
    AgentActionEqualToConstraint,
    AndBooleanCondition,
    AttributeIdAtom,
    BitAnd,
    BitNot,
    BitOr,
    BitXor,
    BooleanCondition,
    DivideExpr,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    GreaterThan,
    GreaterThanOrEqual,
    IdAtom,
    IntAtom,
    LessThan,
    LessThanOrEqual,
    MultiplyExpr,
    NotBooleanCondition,
    NotEqualTo,
    OrBooleanCondition,
    SubtractExpr,
    TrueBoolValue,
    _BinaryBoolCondition,
)
from bitml2mcmas.mcmas.custom_types import ENVIRONMENT, McmasId
from bitml2mcmas.mcmas.formula import (
    AFFormula,
    AGFormula,
    AndFormula,
    AtomicFormula,
    AUntilFormula,
    AXFormula,
    DiamondAlwaysFormula,
    DiamondEventuallyFormula,
    DiamondNextFormula,
    DiamondUntilFormula,
    EFFormula,
    EGFormula,
    EnvGreenStatesAtomicFormula,
    EnvRedStatesAtomicFormula,
    EUntilFormula,
    EXFormula,
    FormulaType,
    GreenStatesAtomicFormula,
    NotFormula,
    OrFormula,
    RedStatesAtomicFormula, ImpliesFormula,
)

_DEFAULT_INDENTATION = "  "


@singledispatch
def boolcond_to_string(obj: object) -> str:
    raise CaseNotHandledError(boolcond_to_string.__name__, obj)  # type: ignore[attr-defined]


@boolcond_to_string.register
def boolcond_to_string_subtract(f: SubtractExpr) -> str:
    return f"({boolcond_to_string(f.left)} - {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_add(f: AddExpr) -> str:
    return f"({boolcond_to_string(f.left)} + {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_multiply(f: MultiplyExpr) -> str:
    return f"({boolcond_to_string(f.left)} * {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_divide(f: DivideExpr) -> str:
    return f"({boolcond_to_string(f.left)} / {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_bitor(f: BitOr) -> str:
    return f"({boolcond_to_string(f.left)} | {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_bitand(f: BitAnd) -> str:
    return f"({boolcond_to_string(f.left)} & {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_bitxor(f: BitXor) -> str:
    return f"({boolcond_to_string(f.left)} ^ {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_bitnot(f: BitNot) -> str:
    return f"(~{formula_to_string(f.arg)})"


@boolcond_to_string.register
def boolcond_to_string_binary_bool_condition(f: _BinaryBoolCondition) -> str:
    return boolcond_to_string(f.left) and boolcond_to_string(f.right)


@boolcond_to_string.register
def boolcond_to_string_equal_to(f: EqualTo) -> str:
    return f"({boolcond_to_string(f.left)} = {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_not_equal_to(f: NotEqualTo) -> str:
    return f"({boolcond_to_string(f.left)} != {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_less_than(f: LessThan) -> str:
    return f"({boolcond_to_string(f.left)} < {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_less_than_or_equal(f: LessThanOrEqual) -> str:
    return f"({boolcond_to_string(f.left)} <= {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_greater_than(f: GreaterThan) -> str:
    return f"({boolcond_to_string(f.left)} > {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_greater_than_or_equal(f: GreaterThanOrEqual) -> str:
    return f"({boolcond_to_string(f.left)} >= {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_and(f: AndBooleanCondition) -> str:
    return f"({boolcond_to_string(f.left)} and {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_or(f: OrBooleanCondition) -> str:
    return f"({boolcond_to_string(f.left)} or {boolcond_to_string(f.right)})"


@boolcond_to_string.register
def boolcond_to_string_not(f: NotBooleanCondition) -> str:
    return f"(!{boolcond_to_string(f.arg)})"


@boolcond_to_string.register
def boolcond_to_string_id_atom(f: IdAtom) -> str:
    return f.value


@boolcond_to_string.register
def boolcond_to_string_int_atom(f: IntAtom) -> str:
    return str(f.value)


@boolcond_to_string.register
def boolcond_to_string_false_bool_value(f: FalseBoolValue) -> str:
    return "false"


@boolcond_to_string.register
def boolcond_to_string_true_bool_value(f: TrueBoolValue) -> str:
    return "true"


@boolcond_to_string.register
def boolcond_to_string_action_equal_to_constraint(f: ActionEqualToConstraint) -> str:
    return f"(Action = {f.action_value})"


@boolcond_to_string.register
def boolcond_to_string_agent_action_equal_to_constraint(
    f: AgentActionEqualToConstraint,
) -> str:
    return f"({f.agent}.Action = {f.action_value})"


@boolcond_to_string.register
def boolcond_to_string_environment_action_equal_to_constraint(
    f: EnvironmentActionEqualToConstraint,
) -> str:
    return f"({ENVIRONMENT}.Action = {f.action_value})"


@boolcond_to_string.register
def boolcond_to_string_attribute_id_atom(f: AttributeIdAtom) -> str:
    return f"{f.mcmas_object}.{f.attribute}"


@boolcond_to_string.register
def boolcond_to_string_environment_id_atom(f: EnvironmentIdAtom) -> str:
    return f"{ENVIRONMENT}.{f.attribute}"


@singledispatch
def formula_to_string(obj: object) -> str:
    raise CaseNotHandledError(formula_to_string.__name__, obj)  # type: ignore[attr-defined]


@formula_to_string.register
def formula_to_string_ag(f: AGFormula) -> str:
    return f"(AG ({formula_to_string(f.arg)}))"


@formula_to_string.register
def formula_to_string_eg(f: EGFormula) -> str:
    return f"(EG {formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_ax(f: AXFormula) -> str:
    return f"(AX {formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_ex(f: EXFormula) -> str:
    return f"(EX {formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_af(f: AFFormula) -> str:
    return f"(AF {formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_ef(f: EFFormula) -> str:
    return f"(EF {formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_auntil(f: AUntilFormula) -> str:
    return f"(A {formula_to_string(f.left)} U {formula_to_string(f.right)})"


@formula_to_string.register
def formula_to_string_euntil(f: EUntilFormula) -> str:
    return f"(E {formula_to_string(f.left)} U {formula_to_string(f.right)})"


@formula_to_string.register
def formula_to_string_diamond_next(f: DiamondNextFormula) -> str:
    return f"(<{f.group_id}>X({formula_to_string(f.arg)}))"


@formula_to_string.register
def formula_to_string_diamond_eventually(f: DiamondEventuallyFormula) -> str:
    return f"(<{f.group_id}>F({formula_to_string(f.arg)}))"


@formula_to_string.register
def formula_to_string_diamond_always(f: DiamondAlwaysFormula) -> str:
    return f"(<{f.group_id}>G({formula_to_string(f.arg)}))"


@formula_to_string.register
def formula_to_string_xxx(f: DiamondUntilFormula) -> str:
    return f"(<{f.group_id}>({formula_to_string(f.left)} U {formula_to_string(f.right)}))"


@formula_to_string.register
def formula_to_string_atomic_formula(f: AtomicFormula) -> str:
    return f.id


@formula_to_string.register
def formula_to_string_green_states_atomic(f: GreenStatesAtomicFormula) -> str:
    return f"{f.id}.GreenStates"


@formula_to_string.register
def formula_to_string_red_states_atomic(f: RedStatesAtomicFormula) -> str:
    return f"{f.id}.RedStates"


@formula_to_string.register
def formula_to_string_environment_green_states_atomic(
    f: EnvGreenStatesAtomicFormula,
) -> str:
    return f"{ENVIRONMENT}.GreenStates"


@formula_to_string.register
def formula_to_string_environment_red_states_atomic(
    f: EnvRedStatesAtomicFormula,
) -> str:
    return f"{ENVIRONMENT}.RedStates"


@formula_to_string.register
def formula_to_string_not_formula(f: NotFormula) -> str:
    return f"(!{formula_to_string(f.arg)})"


@formula_to_string.register
def formula_to_string_and_formula(f: AndFormula) -> str:
    return f"({formula_to_string(f.left)} and {formula_to_string(f.right)})"


@formula_to_string.register
def formula_to_string_or_formula(f: OrFormula) -> str:
    return f"({formula_to_string(f.left)} or {formula_to_string(f.right)})"


@formula_to_string.register
def formula_to_string_or_formula(f: ImpliesFormula) -> str:
    return f"({formula_to_string(f.left)}) -> ({formula_to_string(f.right)})"


@singledispatch
def var_type_to_string(var_type: object) -> str:
    raise CaseNotHandledError(boolcond_to_string.__name__, var_type)  # type: ignore[attr-defined]


@var_type_to_string.register
def boolean_var_type_to_string(var_type: BooleanVarType) -> str:
    return "boolean"


@var_type_to_string.register
def integer_var_type_to_string(var_type: IntegerRangeVarType) -> str:
    return f"{var_type.lower}..{var_type.upper}"


@var_type_to_string.register
def enum_var_type_to_string(var_type: EnumVarType) -> str:
    return "{" + ", ".join(sorted([v for v in var_type.values])) + "}"


def _make_section(section_name: str, content: str, with_colon: bool = True) -> str:
    return (
        f"{section_name}{':' if with_colon else ''}\n"
        f"{indent(content, _DEFAULT_INDENTATION)}\n"
        f"end {section_name}"
    )


def var_definition_to_string(vardef: VarDefinition) -> str:
    return f"{vardef.varname}: {var_type_to_string(vardef.vartype)}"


def _list_of_mcmas_ids(ids: Collection[McmasId]) -> str:
    return ", ".join(sorted(ids))


def _var_definitions_to_string(
    var_definitions: Sequence[VarDefinition],
    section_name: str,
    vardef_to_string: Callable,
) -> str:
    var_defs_strings = [vardef_to_string(vardef) for vardef in var_definitions]
    var_defs_body = ";\n".join(var_defs_strings) + ";"
    return _make_section(section_name, var_defs_body)


def _obs_var_defs_to_string(obs_var_definitions: Sequence[VarDefinition] | None) -> str:
    if obs_var_definitions is None:
        return ""
    return _var_definitions_to_string(
        obs_var_definitions, "Obsvars", var_definition_to_string
    )


def _var_defs_to_string(vars_definitions: Sequence[VarDefinition] | None) -> str:
    if vars_definitions is None:
        return ""
    return _var_definitions_to_string(
        vars_definitions, "Vars", var_definition_to_string
    )


def _red_states_to_string(red_states: _EnvRedStatesDef) -> str:
    if red_states is None:
        return ""

    condition_str = boolcond_to_string(red_states)
    return _make_section("RedStates", condition_str)


def _actions_to_string(actions: AbstractSet[McmasId]) -> str:
    action_list = _list_of_mcmas_ids(actions)
    return f"Actions = {{{action_list}}};"


def _protocol_rule_to_str(protocol_rule: ProtocolRule) -> str:
    boolcond_str = boolcond_to_string(protocol_rule.condition)
    action_list_str = _list_of_mcmas_ids(protocol_rule.enabled_actions)
    return f"{boolcond_str}: {{{action_list_str}}};"


def _other_rule_to_str(actions: AbstractSet[McmasId]) -> str:
    action_list_str = _list_of_mcmas_ids(actions)
    return f"Other: {{{action_list_str}}};"


def _protocol_to_string(protocol: Protocol | None) -> str:
    if protocol is None:
        return ""

    rules_str_list = []
    if protocol.rules is not None:
        for rule in protocol.rules:
            rules_str_list.append(_protocol_rule_to_str(rule))

    if protocol.other_rule is not None:
        other_rule_str = _other_rule_to_str(protocol.other_rule)
        rules_str_list.append(other_rule_str)

    protocol_content = "\n".join(rules_str_list)
    return _make_section("Protocol", protocol_content)


def _effects_to_string(effects: Sequence[Effect]) -> str:
    effects_str = []
    for effect in effects:
        effect_str = f"{effect.varname} = {boolcond_to_string(effect.value)}"
        effects_str.append(effect_str)

    return " and ".join(effects_str)


def _evolution_rule_to_string(evolution_rule: EvolutionRule) -> str:
    effects_str = _effects_to_string(evolution_rule.effects)
    condition_str = boolcond_to_string(evolution_rule.condition)
    return f"{effects_str} if {condition_str};"


def _evolution_to_string(evolution_rules: Sequence[EvolutionRule]) -> str:
    evolution_rules_str = "\n".join(map(_evolution_rule_to_string, evolution_rules))
    return _make_section("Evolution", evolution_rules_str)


def _environment_to_string(env: Environment | None) -> str:
    if env is None:
        return ""

    opening = f"Agent {ENVIRONMENT}\n"

    obs_var_section = _obs_var_defs_to_string(env.obs_var_definitions)
    vars_section = _var_defs_to_string(env.env_var_definitions)
    red_states_section = _red_states_to_string(env.env_red_definitions)
    action_def_section = _actions_to_string(env.env_action_definitions)
    protocol_section = _protocol_to_string(env.env_protocol_definition)
    evolution_section = _evolution_to_string(env.env_evolution_definition)

    env_body = (
        f"{obs_var_section}\n"
        f"{vars_section}\n"
        f"{red_states_section}\n"
        f"{action_def_section}\n"
        f"{protocol_section}\n"
        f"{evolution_section}\n"
    )

    closing = "end Agent\n"

    return opening + indent(env_body, prefix=_DEFAULT_INDENTATION) + closing


def _lobs_vars_to_string(lobs_vars: Sequence[McmasId] | None) -> str:
    if lobs_vars is None:
        return ""

    return f"Lobsvars = {{{_list_of_mcmas_ids(lobs_vars)}}};"


def _agent_to_string(agent: Agent) -> str:
    opening = f"Agent {agent.name}\n"

    lobs_var_section = _lobs_vars_to_string(agent.lobs_var_definitions)
    vars_section = _var_defs_to_string(agent.agent_var_definitions)
    red_states_section = _red_states_to_string(agent.agent_red_definitions)
    action_def_section = _actions_to_string(agent.agent_action_definitions)
    protocol_section = _protocol_to_string(agent.agent_protocol_definition)
    evolution_section = _evolution_to_string(agent.agent_evolution_definition)

    agent_body = (
        f"{lobs_var_section}\n"
        f"{vars_section}\n"
        f"{red_states_section}\n"
        f"{action_def_section}\n"
        f"{protocol_section}\n"
        f"{evolution_section}\n"
    )

    closing = "end Agent"

    return opening + indent(agent_body, prefix=_DEFAULT_INDENTATION) + closing


def _evaluation_rule_to_string(evaluation_rule: EvaluationRule) -> str:
    condition_str = boolcond_to_string(evaluation_rule.condition)
    return f"{evaluation_rule.prop_id} if {condition_str}"


def _evaluation_to_string(evaluation_rules: Sequence[EvaluationRule]) -> str:
    content_str = ";\n".join(map(_evaluation_rule_to_string, evaluation_rules)) + ";"
    return _make_section("Evaluation", content_str, with_colon=False)


def _initial_states_to_string(initial_states: BooleanCondition) -> str:
    content_str = boolcond_to_string(initial_states) + ";"
    return _make_section("InitStates", content_str, with_colon=False)


def _group_line_to_string(group: Group) -> str:
    return f"{group.group_name} = {{{_list_of_mcmas_ids(group.agents)}}};"


def _groups_to_string(groups: Sequence[Group]) -> str:
    content = "\n".join(map(_group_line_to_string, groups))
    return _make_section("Groups", content, with_colon=False)


def _formulae_to_string(section_name: str, formulae: Sequence[FormulaType]) -> str:
    formulae_str = map(lambda f: formula_to_string(f) + ";", formulae)
    content = "\n".join(formulae_str)
    return _make_section(section_name, content, with_colon=False)


def interpreted_system_to_string(program: InterpretedSystem) -> str:
    semantics_str = (
        f"Semantics={program.semantics.value};" if program.semantics is not None else ""
    )
    environment_str = _environment_to_string(program.environment)

    agents_str = "\n".join(map(_agent_to_string, program.agents))
    evaluation_str = _evaluation_to_string(program.evaluation_rules)
    initial_states_str = _initial_states_to_string(
        program.initial_states_boolean_condition
    )
    groups_str = _groups_to_string(program.groups)
    fair_formulae_str = _formulae_to_string("Fairness", program.fair_formulae)
    formulae_str = _formulae_to_string("Formulae", program.formulae)

    program_str = (
        f"{semantics_str}\n"
        f"{environment_str}\n"
        f"{agents_str}\n"
        f"{evaluation_str}\n"
        f"{initial_states_str}\n"
        f"{groups_str}\n"
        f"{fair_formulae_str}\n"
        f"{formulae_str}"
    )

    return program_str
