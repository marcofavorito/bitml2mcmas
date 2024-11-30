"""Class to handle the building of a MCMAS program from a BitML contract."""

import operator
from collections.abc import Collection, Sequence
from functools import reduce
from typing import AbstractSet

from bitml2mcmas.mcmas.ast import (
    Agent,
    Environment,
    EvaluationRule,
    EvolutionRule,
    Group,
    InterpretedSystem,
    Protocol,
    ProtocolRule,
    Semantics,
    VarDefinition,
)
from bitml2mcmas.mcmas.boolcond import BooleanCondition
from bitml2mcmas.mcmas.custom_types import McmasId
from bitml2mcmas.mcmas.formula import FormulaType


class EnvBuilder:
    def __init__(self) -> None:
        self.__env_obs_var_definitions = []
        self.__env_var_definitions = []
        self.__env_red_definitions = None
        self.__env_actions = set()
        self.__env_protocol_rules = []
        self.__env_protocol_other_rule = set()
        self.__env_evolution_definition = []

    @property
    def env_obs_var_definitions(self) -> Sequence[VarDefinition]:
        return tuple(self.__env_obs_var_definitions)

    @property
    def env_var_definitions(self) -> Sequence[VarDefinition]:
        return tuple(self.__env_var_definitions)

    @property
    def env_red_definitions(self):
        return self.__env_red_definitions

    @property
    def env_actions(self) -> AbstractSet[McmasId]:
        return frozenset(self.__env_actions)

    @property
    def env_protocol_rules(self) -> Sequence[ProtocolRule] | None:
        return (
            tuple(self.__env_protocol_rules)
            if len(self.__env_protocol_rules) > 0
            else None
        )

    @property
    def env_protocol_other_rule(self) -> AbstractSet[McmasId] | None:
        return (
            frozenset(self.__env_protocol_other_rule)
            if len(self.__env_protocol_other_rule) > 0
            else None
        )

    @property
    def env_protocol_definition(self) -> Protocol:
        return Protocol(self.env_protocol_rules, self.env_protocol_other_rule)

    @property
    def env_evolution_definition(self) -> Sequence[EvolutionRule]:
        return tuple(self.__env_evolution_definition)

    def compile(self) -> Environment:
        return Environment(
            self.env_obs_var_definitions,
            self.env_var_definitions,
            self.env_red_definitions,
            self.env_actions,
            self.env_protocol_definition,
            self.env_evolution_definition,
        )

    def add_env_obs_var(self, vardef: VarDefinition) -> None:
        self.__env_obs_var_definitions.append(vardef)

    def add_env_obs_vars(self, vardefs: Sequence[VarDefinition]) -> None:
        self.__env_obs_var_definitions.extend(vardefs)

    def add_env_var(self, vardef: VarDefinition) -> None:
        self.__env_var_definitions.append(vardef)

    def add_env_vars(self, vardefs: Sequence[VarDefinition]) -> None:
        self.__env_var_definitions.extend(vardefs)

    @env_red_definitions.setter
    def env_red_definitions(self, env_red_def: BooleanCondition | None) -> None:
        self.__env_red_definitions = env_red_def

    def add_action(self, action: McmasId) -> None:
        self.__env_actions.add(action)

    def add_actions(self, actions: Collection[McmasId]) -> None:
        self.__env_actions.update(actions)

    def add_protocol_rule(self, protocol_rule: ProtocolRule) -> None:
        self.__env_protocol_rules.append(protocol_rule)

    def add_protocol_rules(self, protocol_rules: Sequence[ProtocolRule]) -> None:
        self.__env_protocol_rules.extend(protocol_rules)

    def add_action_to_other_protocol_rule(self, action: McmasId) -> None:
        self.__env_protocol_other_rule.add(action)

    def add_actions_to_other_protocol_rule(self, actions: Collection[McmasId]) -> None:
        self.__env_protocol_other_rule.update(actions)

    def add_evolution_rule(self, evolution_rule: EvolutionRule) -> None:
        self.__env_evolution_definition.append(evolution_rule)

    def add_evolution_rules(self, evolution_rules: Sequence[EvolutionRule]) -> None:
        self.__env_evolution_definition.extend(evolution_rules)


class AgentBuilder:
    def __init__(self) -> None:
        self.__agent_name = None

        self.__agent_lobs_var_definitions = set()
        self.__agent_var_definitions = []
        self.__agent_red_definitions = None
        self.__agent_actions = set()
        self.__agent_protocol_rules = []
        self.__agent_protocol_other_rule = set()
        self.__agent_evolution_rules = []

    @property
    def agent_name(self) -> str:
        return self.__agent_name

    @agent_name.setter
    def agent_name(self, s: str) -> None:
        self.__agent_name = s

    @property
    def lobs_var_definitions(self) -> Sequence[McmasId]:
        return tuple(self.__agent_lobs_var_definitions)

    @property
    def agent_var_definitions(self) -> Sequence[VarDefinition]:
        return tuple(self.__agent_var_definitions)

    @property
    def agent_red_definitions(self) -> None:
        return self.__agent_red_definitions

    @property
    def agent_actions(self) -> AbstractSet[McmasId]:
        return frozenset(self.__agent_actions)

    @property
    def agent_protocol_rules(self) -> Sequence[ProtocolRule]:
        return tuple(self.__agent_protocol_rules)

    @property
    def agent_protocol_other_rule(self) -> AbstractSet[McmasId] | None:
        return (
            frozenset(self.__agent_protocol_other_rule)
            if len(self.__agent_protocol_other_rule) > 0
            else None
        )

    @property
    def agent_protocol_definition(self):
        return Protocol(self.agent_protocol_rules, self.agent_protocol_other_rule)

    @property
    def agent_evolution_definition(self):
        return self.__agent_evolution_rules

    def compile(self) -> Agent:
        return Agent(
            self.agent_name,
            self.lobs_var_definitions,
            self.agent_var_definitions,
            self.agent_red_definitions,
            self.agent_actions,
            self.agent_protocol_definition,
            self.agent_evolution_definition,
        )

    def add_lobs_var(self, varname: McmasId) -> None:
        self.__agent_lobs_var_definitions.add(varname)

    def add_lobs_vars(self, varnames: Collection[McmasId]) -> None:
        self.__agent_lobs_var_definitions.update(varnames)

    def add_agent_var(self, vardef: VarDefinition) -> None:
        self.__agent_var_definitions.append(vardef)

    def add_agent_vars(self, vardefs: Collection[VarDefinition]) -> None:
        self.__agent_var_definitions.extend(vardefs)

    @agent_red_definitions.setter
    def agent_red_definitions(self, agent_red_def: BooleanCondition | None):
        self.__agent_red_definitions = agent_red_def

    def add_action(self, action: McmasId) -> None:
        self.__agent_actions.add(action)

    def add_actions(self, actions: Collection[McmasId]) -> None:
        self.__agent_actions.update(actions)

    def add_protocol_rule(self, protocol_rule: ProtocolRule) -> None:
        self.__agent_protocol_rules.append(protocol_rule)

    def add_protocol_rules(self, protocol_rules: Sequence[ProtocolRule]) -> None:
        self.__agent_protocol_rules.extend(protocol_rules)

    def add_action_to_other_protocol_rule(self, action: McmasId) -> None:
        self.__agent_protocol_other_rule.add(action)

    def add_actions_to_other_protocol_rule(self, actions: Collection[McmasId]) -> None:
        self.__agent_protocol_other_rule.update(actions)

    def add_evolution_rule(self, evolution_rule: EvolutionRule) -> None:
        self.__agent_evolution_rules.append(evolution_rule)

    def add_evolution_rules(self, evolution_rules: Sequence[EvolutionRule]) -> None:
        self.__agent_evolution_rules.extend(evolution_rules)


class MCMASBuilder:
    def __init__(self) -> None:
        self.__env_builder = EnvBuilder()
        self.__agent_builders_by_name = {}

        self.__semantics = Semantics.SINGLE_ASSIGNMENT
        self.__initial_states_boolean_conditions = []
        self.__evaluation_rules: list[EvaluationRule] = []
        self.__groups: list[Group] = []
        self.__fairness_formulae: list[FormulaType] = []
        self.__formulae: list[FormulaType] = []

    @property
    def agent_names(self) -> AbstractSet[McmasId]:
        return frozenset(self.__agent_builders_by_name.keys())

    @property
    def semantics(self) -> Semantics:
        return self.__semantics

    @property
    def env(self) -> EnvBuilder:
        return self.__env_builder

    def get_agent_builder(self, agent_name: str) -> AgentBuilder:
        builder = self.__agent_builders_by_name.setdefault(agent_name, AgentBuilder())
        builder.agent_name = agent_name
        return builder

    @property
    def initial_states_boolean_condition(self) -> BooleanCondition:
        return reduce(operator.and_, self.__initial_states_boolean_conditions)

    @property
    def evaluation_rules(self) -> Sequence[EvaluationRule]:
        return tuple(self.__evaluation_rules)

    @property
    def groups(self) -> Sequence[Group]:
        return self.__groups

    @property
    def fairness_formulae(self) -> Sequence[FormulaType]:
        return tuple(self.__fairness_formulae)

    @property
    def formulae(self) -> Sequence[FormulaType]:
        return tuple(self.__formulae)

    def add_initial_state_boolean_condition(self, cond: BooleanCondition) -> None:
        self.__initial_states_boolean_conditions.append(cond)

    def add_initial_state_boolean_conditions(
        self, conds: Sequence[BooleanCondition]
    ) -> None:
        self.__initial_states_boolean_conditions.extend(conds)

    def add_evaluation_rule(self, evaluation_rule: EvaluationRule) -> None:
        self.__evaluation_rules.append(evaluation_rule)

    def add_evaluation_rules(self, evaluation_rules: Sequence[EvaluationRule]) -> None:
        self.__evaluation_rules.extend(evaluation_rules)

    def add_group(self, group: Group) -> None:
        self.__groups.append(group)

    def add_groups(self, groups: Collection[Group]) -> None:
        self.__groups.extend(groups)

    def add_fairness_formula(self, formula: FormulaType) -> None:
        self.__fairness_formulae.append(formula)

    def add_fairness_formulae(self, formulae: Sequence[FormulaType]) -> None:
        self.__fairness_formulae.extend(formulae)

    def add_formula(self, formula: FormulaType) -> None:
        self.__formulae.append(formula)

    def add_formulae(self, formulae: Sequence[FormulaType]) -> None:
        self.__formulae.extend(formulae)

    def compile(self) -> InterpretedSystem:
        env = self.__env_builder.compile()
        agents = [b.compile() for b in self.__agent_builders_by_name.values()]
        system = InterpretedSystem(
            semantics=self.semantics,
            environment=env,
            agents=agents,
            evaluation_rules=self.evaluation_rules,
            initial_states_boolean_condition=self.initial_states_boolean_condition,
            groups=self.groups,
            fair_formulae=self.fairness_formulae,
            formulae=self.formulae,
        )
        return system
