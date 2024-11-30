import operator
from collections.abc import Sequence
from functools import reduce


from bitml2mcmas.compiler._private.terms import DELAY, LAST_ACTION, NOP, TermNaming, UNSET_ACTION
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import Effect, EnumVarType, EvolutionRule, VarDefinition
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AttributeIdAtom,
    BooleanCondition,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    IdAtom,
)


class AddLastAction(Transformer):
    @property
    def env_actions(self):
        return self.builder.env.env_actions

    def apply(self) -> None:
        self.builder.env.add_env_var(self.last_action_vardef)
        self.builder.env.add_evolution_rules(self.last_action_evolution_rules)
        self.builder.add_initial_state_boolean_condition(
            self.last_action_initial_state_clause
        )

        # for participant_id in self.wrapper.participant_ids:
        #     self._handle_participant(participant_id)

    def _handle_participant(self, participant_id: str):
        agent_builder = self.agent_builder_by_participant_id(participant_id)
        agent_builder.add_agent_var(
            self.get_last_action_vardef_for_agent(participant_id)
        )
        agent_builder.add_evolution_rules(
            self.get_last_action_evolution_rules_for_agent(participant_id)
        )

        initial_state_clause = self.get_last_action_initial_state_clause_for_agent(
            participant_id
        )
        self.builder.add_initial_state_boolean_condition(initial_state_clause)

    @property
    def last_action_vardef(self) -> VarDefinition:
        last_action_values = {TermNaming.action_with_prefix(action) for action in self.env_actions}
        last_action_values.add(UNSET_ACTION)
        last_action_vartype = EnumVarType(last_action_values)
        last_action_vardef = VarDefinition(LAST_ACTION, last_action_vartype)
        return last_action_vardef

    @property
    def last_action_evolution_rules(self) -> Sequence[EvolutionRule]:
        result = []
        for action in self.env_actions:
            action_prop = TermNaming.action_with_prefix(action)
            er = EvolutionRule(
                [Effect(LAST_ACTION, IdAtom(action_prop))],
                ActionEqualToConstraint(action),
            )
            result.append(er)
        return result

    @property
    def last_action_initial_state_clause(self) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(LAST_ACTION), IdAtom(UNSET_ACTION)
        )

    def get_last_action_vardef_for_agent(self, participant_id: str) -> VarDefinition:
        agent_actions = self.agent_actions_participant_id(participant_id)
        last_action_vartype = EnumVarType(
            {TermNaming.action_with_prefix(action) for action in agent_actions}
        )
        last_action_vardef = VarDefinition(LAST_ACTION, last_action_vartype)
        return last_action_vardef

    def get_last_action_evolution_rules_for_agent(
        self, participant_id: str
    ) -> Sequence[EvolutionRule]:
        result = []
        agent_actions = self.agent_actions_participant_id(participant_id)
        for action in agent_actions:
            if action == NOP:
                # this must be handled differently
                continue
            action_prop = TermNaming.action_with_prefix(action)
            er = EvolutionRule(
                [Effect(LAST_ACTION, IdAtom(action_prop))],
                self.objects.get_is_agent_scheduled_condition(participant_id)
                & ActionEqualToConstraint(action),
            )
            result.append(er)

        # in case agent is not scheduled, set last_action to nop
        # negations in preconditions are not supported for evolution rules...
        clauses = []
        for other_participant_id in self.wrapper.participant_ids:
            if other_participant_id == participant_id:
                continue
            clauses.append(
                self.objects.get_is_agent_scheduled_condition(other_participant_id)
            )
        condition = reduce(operator.or_, clauses)

        # ... or, if the agent is scheduled and the action is NOP...
        condition |= self.objects.get_is_agent_scheduled_condition(
            participant_id
        ) & ActionEqualToConstraint(NOP)

        # ... or, if the environment action is DELAY or NOP
        condition |= EnvironmentActionEqualToConstraint(NOP)
        if self.wrapper.has_timeouts:
            condition |= EnvironmentActionEqualToConstraint(DELAY)

        action_nop = TermNaming.action_with_prefix(NOP)
        er = EvolutionRule([Effect(LAST_ACTION, IdAtom(action_nop))], condition)
        result.append(er)

        return result

    def get_last_action_initial_state_clause_for_agent(
        self, participant_id: str
    ) -> BooleanCondition:
        agent_name = TermNaming.agent_name_from_participant_name(participant_id)
        return EqualTo(
            AttributeIdAtom(agent_name, LAST_ACTION),
            IdAtom(TermNaming.action_with_prefix(NOP)),
        )
