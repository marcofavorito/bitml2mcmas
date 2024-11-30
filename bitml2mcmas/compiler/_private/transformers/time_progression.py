import operator
from collections.abc import Sequence
from functools import reduce

from bitml2mcmas.compiler._private.terms import (
    DELAY,
    NOP,
    TIME,
    TIME_PROGRESSES_FOREVER,
    TIME_REACHES_MAXIMUM,
    TermNaming,
)
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import (
    BooleanVarType,
    Effect,
    EvaluationRule,
    EvolutionRule,
    IntegerRangeVarType,
    ProtocolRule,
    VarDefinition,
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AddExpr,
    AgentActionEqualToConstraint,
    AttributeIdAtom,
    BooleanCondition,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    IdAtom,
    IntAtom,
    LessThan,
    TrueBoolValue, GreaterThanOrEqual,
)
from bitml2mcmas.mcmas.formula import AtomicFormula, FormulaType


class AddTimeProgression(Transformer):
    def apply(self) -> None:
        if not self.wrapper.has_timeouts:
            return

        self._handle_env()
        for participant_id in self.wrapper.participant_ids:
            self._handle_agent(participant_id)

        self.builder.add_evaluation_rules(self.evaluation_rules_for_time_progression)
        self.builder.add_fairness_formulae(self.fairness_formulae_for_time_progression)

    def _handle_env(self):
        env = self.builder.env

        env.add_env_obs_var(self.time_vardef)
        env.add_env_vars(self.agent_done_vardefs)

        env.add_action(DELAY)

        env.add_action_to_other_protocol_rule(DELAY)

        env.add_evolution_rules(self.evolution_rules_done_to_false)
        env.add_evolution_rules(self.evolution_rules_done_to_true)
        env.add_evolution_rules(self.evolution_rules_increase_time)

        self.builder.add_initial_state_boolean_condition(self.time_equal_to_zero)
        self.builder.add_initial_state_boolean_conditions(
            self.agent_done_initial_state_condition_clauses
        )

    def _handle_agent(self, participant_id: str):
        agent_builder = self.agent_builder_by_participant_id(participant_id)
        agent_done_varname = TermNaming.agent_done_varname(participant_id)
        agent_builder.add_lobs_var(agent_done_varname)

    @property
    def time_vardef(self) -> VarDefinition:
        return VarDefinition(
            TIME, IntegerRangeVarType(0, self.wrapper.graph.max_timeout)
        )

    @property
    def time_equal_to_zero(self) -> BooleanCondition:
        return EqualTo(EnvironmentIdAtom(TIME), IntAtom(0))

    @property
    def time_less_than_max_timeout(self) -> BooleanCondition:
        max_timeout = self.wrapper.graph.max_timeout
        return LessThan(IdAtom(TIME), IntAtom(max_timeout))

    @property
    def time_less_than_max_timeout_with_env(self) -> BooleanCondition:
        max_timeout = self.wrapper.graph.max_timeout
        return LessThan(EnvironmentIdAtom(TIME), IntAtom(max_timeout))

    @property
    def time_equal_to_max(self) -> BooleanCondition:
        return EqualTo(EnvironmentIdAtom(TIME), IntAtom(self.wrapper.graph.max_timeout))

    def get_time_greater_than_x(self, timeout: int):
        return GreaterThanOrEqual(EnvironmentIdAtom(TIME), IntAtom(timeout))

    @property
    def agent_done_vardefs(self) -> Sequence[VarDefinition]:
        result = []
        for participant_id in self.wrapper.participant_ids:
            vardef = self.get_agent_done_vardef_for_agent(participant_id)
            result.append(vardef)
        return tuple(result)

    @property
    def agent_done_varnames(self) -> Sequence[str]:
        return tuple(
            [
                TermNaming.agent_done_varname(participant_id)
                for participant_id in self.wrapper.participant_ids
            ]
        )

    def get_agent_done_vardef_for_agent(self, participant_id: str) -> VarDefinition:
        agent_done_varname = TermNaming.agent_done_varname(participant_id)
        agent_done_vardef = VarDefinition(agent_done_varname, BooleanVarType())
        return agent_done_vardef

    @property
    def protocol_rule_delay_action(self) -> ProtocolRule:
        condition_clauses = [
            EqualTo(IdAtom(varname), TrueBoolValue())
            for varname in self.agent_done_varnames
        ]

        time_less_than_max_timeout = self.time_less_than_max_timeout
        condition_clauses.append(time_less_than_max_timeout)

        condition = reduce(operator.and_, condition_clauses)
        enabled_actions = {DELAY}
        return ProtocolRule(condition, enabled_actions)

    @property
    def evolution_rules_increase_time(self) -> Sequence[EvolutionRule]:
        result = []

        increase_time_condition = ActionEqualToConstraint(DELAY) & self.objects.all_agent_done_are_true & self.time_less_than_max_timeout
        effect = Effect(TIME, AddExpr(IdAtom(TIME), IntAtom(1)))
        result.append(EvolutionRule([effect], increase_time_condition))

        return result

    @property
    def evolution_rules_done_to_false(self) -> Sequence[EvolutionRule]:
        result = []

        # var done to false
        effects = [
            Effect(varname, FalseBoolValue()) for varname in self.agent_done_varnames
        ]
        condition = ActionEqualToConstraint(DELAY)
        condition &= self.objects.all_agent_done_are_true

        for effect in effects:
            er = EvolutionRule([effect], condition)
            result.append(er)

        return result

    @property
    def evolution_rules_done_to_true(self) -> Sequence[EvolutionRule]:
        result = []

        for participant_id in self.wrapper.participant_ids:
            agent_name = TermNaming.agent_name_from_participant_name(participant_id)
            varname = TermNaming.agent_done_varname(participant_id)
            effect = Effect(varname, TrueBoolValue())

            condition = self.objects.get_is_agent_scheduled_condition_for_env(participant_id)
            condition &= AgentActionEqualToConstraint(agent_name, NOP)
            condition &= self.objects.get_agent_done_is_false(participant_id)

            er = EvolutionRule([effect], condition)
            result.append(er)

        return result

    @property
    def agent_done_initial_state_condition_clauses(self) -> Sequence[BooleanCondition]:
        result = []
        for agent_done_varname in self.agent_done_varnames:
            result.append(
                EqualTo(EnvironmentIdAtom(agent_done_varname), FalseBoolValue())
            )
        return result

    def get_time_progression_evolution_rule_for_agent(
        self, participant_id: str
    ) -> Sequence[EvolutionRule]:
        agent_done_varname = self.objects.get_agent_done_varname(participant_id)

        # if agent action is nop, set agent done to true
        effs1 = [Effect(agent_done_varname, TrueBoolValue())]
        cond1 = (
            self.objects.get_is_agent_scheduled_condition(participant_id)
            & self.objects.get_agent_done_is_false(participant_id)
            & ActionEqualToConstraint(NOP)
        )
        er1 = EvolutionRule(effs1, cond1)

        # if env action is delay, set agent done to false
        effs2 = [Effect(agent_done_varname, FalseBoolValue())]
        cond2 = EnvironmentActionEqualToConstraint(DELAY)
        er2 = EvolutionRule(effs2, cond2)

        return tuple([er1, er2])

    def get_agent_done_initial_state_condition_for_agent(
        self, participant_id: str
    ) -> BooleanCondition:
        agent_done_varname = self.objects.get_agent_done_varname(participant_id)
        agent_name = TermNaming.agent_name_from_participant_name(participant_id)
        return EqualTo(
            AttributeIdAtom(agent_name, agent_done_varname), FalseBoolValue()
        )

    @property
    def evaluation_rules_for_time_progression(self) -> Sequence[EvaluationRule]:
        result = []

        time_equal_to_max = self.time_equal_to_max
        last_action_equal_to_delay = self.objects.last_action_equal_to_delay

        time_progresses_forever_er = EvaluationRule(
            TIME_PROGRESSES_FOREVER, time_equal_to_max | last_action_equal_to_delay
        )
        result.append(time_progresses_forever_er)

        time_equal_to_max_er = EvaluationRule(TIME_REACHES_MAXIMUM, time_equal_to_max)
        result.append(time_equal_to_max_er)

        for timeout in self.wrapper.graph.timeouts:
            result.append(
                EvaluationRule(
                    TermNaming.timeout_has_expired(timeout),
                    self.get_time_greater_than_x(timeout)
                )
            )

        for participant_id in self.wrapper.participant_ids:
            result.append(
                EvaluationRule(
                    TermNaming.agent_done_prop(participant_id),
                    EqualTo(EnvironmentIdAtom(TermNaming.agent_done_varname(participant_id)), TrueBoolValue())
                )
            )

        return result

    @property
    def fairness_formulae_for_time_progression(self) -> Sequence[FormulaType]:
        return tuple([AtomicFormula(TIME_PROGRESSES_FOREVER)])
