from collections.abc import Sequence

from bitml2mcmas.compiler._private.terms import LAST_ACTION, NOP, TermNaming
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import EvaluationRule, Protocol, ProtocolRule
from bitml2mcmas.mcmas.boolcond import EnvironmentIdAtom, EqualTo, IdAtom, FalseBoolValue
from bitml2mcmas.mcmas.formula import AtomicFormula, FormulaType


class AddSchedulingActions(Transformer):
    def apply(self) -> None:
        scheduling_actions = self.objects.scheduling_actions
        self.builder.env.add_actions(scheduling_actions)

        if not self.wrapper.has_timeouts:
            self.builder.env.add_actions_to_other_protocol_rule(scheduling_actions)

        for participant_id, agent_builder in self.get_agent_builders():
            agent_builder.add_action(NOP)
            agent_builder.add_action_to_other_protocol_rule(NOP)
            if self.wrapper.has_timeouts:
                self.builder.env.add_protocol_rule(self.get_protocol_rule_for_agent(participant_id))


        self.builder.add_evaluation_rules(self.evaluation_rules_for_scheduling)
        self.builder.add_fairness_formulae(self.fairness_formulae_for_scheduling)

    def get_protocol_rule_for_agent(self, participant_id: str) -> ProtocolRule:
        agent_is_done_varname = TermNaming.agent_done_varname(participant_id)
        scheduling_action = TermNaming.scheduling_action_from_participant_id(participant_id)
        return ProtocolRule(
            EqualTo(IdAtom(agent_is_done_varname), FalseBoolValue()),
            {scheduling_action}
        )

    @property
    def evaluation_rules_for_scheduling(self) -> Sequence[EvaluationRule]:
        result = []
        # agent A is scheduled -> last_action is schedule_agent_A
        for agent in self.wrapper.participant_ids:
            scheduling_action = TermNaming.scheduling_action_from_participant_id(agent)
            action_prop = TermNaming.action_with_prefix(scheduling_action)
            result.append(
                EvaluationRule(
                    TermNaming.scheduling_prop_from_participant_id(agent),
                    EqualTo(EnvironmentIdAtom(LAST_ACTION), IdAtom(action_prop)),
                )
            )
        return result

    @property
    def fairness_formulae_for_scheduling(self) -> Sequence[FormulaType]:
        result = []
        # each agent is scheduled infinitely often
        for participant_id in self.wrapper.participant_ids:
            formula = AtomicFormula(
                TermNaming.scheduling_prop_from_participant_id(participant_id)
            )
            result.append(formula)
        return tuple(result)
