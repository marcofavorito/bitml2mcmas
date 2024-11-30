import operator
from collections.abc import Sequence
from functools import reduce
from typing import cast

from bitml2mcmas.bitml.ast import BitMLSecretPrecondition
from bitml2mcmas.compiler._private.terms import (
    NOP,
    PrivateSecretValues,
    PublicSecretValues,
    TermNaming,
)
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import (
    Effect,
    EnumVarType,
    EvaluationRule,
    EvolutionRule,
    ProtocolRule,
    VarDefinition,
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AgentActionEqualToConstraint,
    AttributeIdAtom,
    BooleanCondition,
    EnvironmentIdAtom,
    EqualTo,
    IdAtom,
)
from bitml2mcmas.mcmas.formula import AtomicFormula, OrFormula


class AddSecrets(Transformer):
    def apply(self) -> None:
        self._handle_env()
        for participant_id in self.wrapper.secrets_by_participant_id.keys():
            self._handle_participant(participant_id)

        self.builder.add_evaluation_rules(self.evaluation_rules_for_secrets)

        # TODO: seems that fairness conditions work only when on Environment states
        # self.builder.add_fairness_formulae(self.fairness_formulae_for_secrets)

    def _handle_env(self):
        self.env.add_env_obs_vars(self.public_secret_vardefs)

        for secret in self.wrapper.secrets:
            evolution_rules = self.get_public_secret_evolution_rules(secret)
            self.env.add_evolution_rules(evolution_rules)

            secret_initial_state_condition = (
                self.get_public_secret_initial_state_condition(secret)
            )
            self.builder.add_initial_state_boolean_condition(
                secret_initial_state_condition
            )

    def _handle_participant(self, participant_id: str):
        agent_builder = self.agent_builder_by_participant_id(participant_id)
        agent_builder.add_agent_vars(
            self.get_private_secret_vardefs_of_participant(participant_id)
        )

        for secret in self.wrapper.get_secrets_of_participant(participant_id):
            agent_builder.add_action(
                TermNaming.valid_commitment_action(secret.secret_id)
            )
            agent_builder.add_action(
                TermNaming.invalid_commitment_action(secret.secret_id)
            )
            agent_builder.add_action(TermNaming.reveal_action(secret.secret_id))

            agent_builder.add_protocol_rule(
                self.get_protocol_rule_private_secret_commitment(secret)
            )
            agent_builder.add_protocol_rule(
                self.get_protocol_rule_private_secret_reveal(secret)
            )

            agent_builder.add_evolution_rule(
                self.get_evolution_rule_valid_commitment_action(secret)
            )
            agent_builder.add_evolution_rule(
                self.get_evolution_rule_invalid_commitment_action(secret)
            )

            self.builder.add_initial_state_boolean_condition(
                self.get_private_secret_not_committed_with_agent(secret)
            )

    @property
    def public_secret_vardefs(self) -> Sequence[VarDefinition]:
        result = []
        for secret in self.wrapper.secrets:
            public_secret_vardef = self.get_public_secret_var_definition(
                secret.secret_id
            )
            result.append(public_secret_vardef)
        return result

    def get_public_secret_var_definition(self, secret_id: str) -> VarDefinition:
        secret_value_vartype = EnumVarType(PublicSecretValues.values())
        secret_value_varname = TermNaming.secret_name_with_prefix_public(secret_id)
        secret_value_vardef = VarDefinition(secret_value_varname, secret_value_vartype)
        return secret_value_vardef

    def get_is_valid_commitment_action(self, secret: BitMLSecretPrecondition):
        agent_of_secret = TermNaming.agent_name_from_participant_name(
            secret.participant_id
        )
        valid_commitment_action = TermNaming.valid_commitment_action(secret.secret_id)
        return AgentActionEqualToConstraint(agent_of_secret, valid_commitment_action)

    def get_is_invalid_commitment_action(self, secret: BitMLSecretPrecondition):
        agent_of_secret = TermNaming.agent_name_from_participant_name(
            secret.participant_id
        )
        invalid_commitment_action = TermNaming.invalid_commitment_action(
            secret.secret_id
        )
        return AgentActionEqualToConstraint(agent_of_secret, invalid_commitment_action)

    def get_public_secret_committed_evolution_rule(
        self, secret: BitMLSecretPrecondition
    ):
        agent_is_scheduled = self.objects.get_is_agent_scheduled_condition_for_env(
            secret.participant_id
        )
        secret_is_not_committed = self.get_is_public_secret_not_committed(secret)
        action_is_valid_commitment = self.get_is_valid_commitment_action(secret)
        action_is_invalid_commitment = self.get_is_invalid_commitment_action(secret)
        public_secret_varname = TermNaming.secret_name_with_prefix_public(
            secret.secret_id
        )
        er = EvolutionRule(
            [Effect(public_secret_varname, IdAtom(PublicSecretValues.COMMITTED.value))],
            secret_is_not_committed
            & (action_is_valid_commitment | action_is_invalid_commitment)
            & agent_is_scheduled,
        )
        return er

    def get_public_secret_evolution_rules(
        self, secret: BitMLSecretPrecondition
    ) -> Sequence[EvolutionRule]:
        er1 = self.get_public_secret_committed_evolution_rule(secret)
        er2 = self.get_evolution_rule_reveal_action(secret)
        return [er1, er2]

    @property
    def secret_all_committed_condition(self) -> BooleanCondition | None:
        if len(self.wrapper.secrets) == 0:
            return None

        conditions = [
            self.get_is_public_secret_committed(secret)
            for secret in self.wrapper.secrets
        ]
        return cast(BooleanCondition, reduce(operator.and_, conditions))

    def get_public_secret_initial_state_condition(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(
                TermNaming.secret_name_with_prefix_public(secret.secret_id)
            ),
            IdAtom(PublicSecretValues.NOT_COMMITTED.value),
        )

    def get_is_public_secret_not_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.NOT_COMMITTED.value),
        )

    def get_is_public_secret_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.COMMITTED.value),
        )

    def get_private_secret_var_definition(self, secret_id: str) -> VarDefinition:
        secret_value_vartype = EnumVarType(PrivateSecretValues.values())
        secret_value_varname = TermNaming.secret_name_with_prefix_private(secret_id)
        secret_value_vardef = VarDefinition(secret_value_varname, secret_value_vartype)
        return secret_value_vardef

    def get_private_secret_vardefs_of_participant(
        self, participant_id
    ) -> Sequence[VarDefinition]:
        result = []
        for secret in self.wrapper.get_secrets_of_participant(participant_id):
            private_secret_vardef = self.get_private_secret_var_definition(
                secret.secret_id
            )
            result.append(private_secret_vardef)
        return result

    def get_private_secret_is_not_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        secret_status_variable = TermNaming.secret_name_with_prefix_private(
            secret.secret_id
        )
        return EqualTo(
            IdAtom(secret_status_variable),
            IdAtom(PrivateSecretValues.NOT_COMMITTED.value),
        )

    def get_private_secret_is_valid(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        secret_status_variable = TermNaming.secret_name_with_prefix_private(
            secret.secret_id
        )
        return EqualTo(
            IdAtom(secret_status_variable),
            IdAtom(PrivateSecretValues.VALID.value),
        )

    def get_private_secret_is_valid_for_env(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        agent_name = TermNaming.agent_name_from_participant_name(secret.participant_id)
        secret_status_variable = TermNaming.secret_name_with_prefix_private(
            secret.secret_id
        )
        return EqualTo(
            AttributeIdAtom(agent_name, secret_status_variable),
            IdAtom(PrivateSecretValues.VALID.value),
        )

    def get_private_secret_not_committed_with_agent(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        agent_name = TermNaming.agent_name_from_participant_name(secret.participant_id)
        return EqualTo(
            AttributeIdAtom(
                agent_name,
                TermNaming.secret_name_with_prefix_private(secret.secret_id),
            ),
            IdAtom(PrivateSecretValues.NOT_COMMITTED.value),
        )

    def get_protocol_rule_private_secret_commitment(
        self, secret: BitMLSecretPrecondition
    ) -> ProtocolRule:
        contract_initialized_to_false = self.objects.contract_initialized_to_false

        valid_commitment_action = TermNaming.valid_commitment_action(secret.secret_id)
        invalid_commitment_action = TermNaming.invalid_commitment_action(
            secret.secret_id
        )

        secret_is_not_committed = self.get_private_secret_is_not_committed(secret)
        condition = contract_initialized_to_false & secret_is_not_committed

        if self.wrapper.has_timeouts:
            condition &= self.objects.get_agent_done_is_false_with_env(secret.participant_id)

        rule = ProtocolRule(
            condition, {valid_commitment_action, invalid_commitment_action, NOP}
        )
        return rule

    def get_protocol_rule_private_secret_reveal(self, secret: BitMLSecretPrecondition):
        reveal_action = TermNaming.reveal_action(secret.secret_id)

        secret_is_valid = self.objects.get_is_private_secret_valid(secret)
        not_already_revealed = EqualTo(
            EnvironmentIdAtom(
                TermNaming.secret_name_with_prefix_public(secret.secret_id)
            ),
            IdAtom(PublicSecretValues.COMMITTED.value),
        )

        condition = secret_is_valid & not_already_revealed

        # add check if agent is done when time progression is enabled
        if self.wrapper.has_timeouts:
            agent_done_is_false = self.objects.get_agent_done_is_false_with_env(
                secret.participant_id
            )
            condition &= agent_done_is_false

        rule = ProtocolRule(condition, {reveal_action, NOP})
        return rule

    def get_evolution_rule_valid_commitment_action(
        self, secret: BitMLSecretPrecondition
    ) -> EvolutionRule:
        contract_initialized_to_false = self.objects.contract_initialized_to_false
        secret_varname = TermNaming.secret_name_with_prefix_private(secret.secret_id)
        is_secret_not_committed = EqualTo(
            IdAtom(secret_varname), IdAtom(PrivateSecretValues.NOT_COMMITTED.value)
        )

        # add valid commitment action
        valid_commitment_action = TermNaming.valid_commitment_action(secret.secret_id)
        is_valid_commitment_action = ActionEqualToConstraint(valid_commitment_action)
        er = EvolutionRule(
            [Effect(secret_varname, IdAtom(PrivateSecretValues.VALID.value))],
            is_valid_commitment_action
            & is_secret_not_committed
            & contract_initialized_to_false
            & self.objects.get_is_agent_scheduled_condition(secret.participant_id),
        )
        return er

    def get_evolution_rule_invalid_commitment_action(
        self, secret: BitMLSecretPrecondition
    ):
        # add invalid commitment action
        contract_initialized_to_false = self.objects.contract_initialized_to_false
        secret_varname = TermNaming.secret_name_with_prefix_private(secret.secret_id)
        is_secret_not_committed = EqualTo(
            IdAtom(secret_varname), IdAtom(PrivateSecretValues.NOT_COMMITTED.value)
        )
        invalid_commitment_action = TermNaming.invalid_commitment_action(
            secret.secret_id
        )
        is_invalid_commitment_action = ActionEqualToConstraint(
            invalid_commitment_action
        )
        er = EvolutionRule(
            [Effect(secret_varname, IdAtom(PrivateSecretValues.INVALID.value))],
            is_invalid_commitment_action
            & is_secret_not_committed
            & contract_initialized_to_false
            & self.objects.get_is_agent_scheduled_condition(secret.participant_id),
        )
        return er

    def get_evolution_rule_reveal_action(
        self, secret: BitMLSecretPrecondition
    ) -> EvolutionRule:
        secret_varname = TermNaming.secret_name_with_prefix_public(secret.secret_id)
        agent_name = TermNaming.agent_name_from_participant_name(secret.participant_id)
        reveal_action = TermNaming.reveal_action(secret.secret_id)
        is_reveal_action_scheduled = AgentActionEqualToConstraint(
            agent_name, reveal_action
        ) & self.objects.get_is_agent_scheduled_condition_for_env(secret.participant_id)
        not_already_revealed = EqualTo(
            IdAtom(secret_varname), IdAtom(PublicSecretValues.COMMITTED.value)
        )

        effect_valid = Effect(secret_varname, IdAtom(PublicSecretValues.VALID.value))
        condition = is_reveal_action_scheduled & not_already_revealed

        return EvolutionRule([effect_valid], condition)

    @property
    def evaluation_rules_for_secrets(self) -> Sequence[EvaluationRule]:
        # evaluations for secret commitments: eventually, each secret is committed
        result = []
        for secret in self.wrapper.secrets:
            owner_agent_name = TermNaming.agent_name_from_participant_name(secret.participant_id)

            private_secret_name = TermNaming.secret_name_with_prefix_private(secret.secret_id)
            for private_value in PrivateSecretValues:
                prop_name = TermNaming.private_secret_is_x_prop(secret.secret_id, private_value)
                er_private_secret = EvaluationRule(prop_name, EqualTo(AttributeIdAtom(owner_agent_name, private_secret_name), IdAtom(private_value.value)))
                result.append(er_private_secret)

            public_secret_name = TermNaming.secret_name_with_prefix_public(secret.secret_id)
            for public_value in PublicSecretValues:
                prop_name = TermNaming.public_secret_is_x_prop(secret.secret_id, public_value)
                er_public_secret = EvaluationRule(prop_name, EqualTo(EnvironmentIdAtom(public_secret_name), IdAtom(public_value.value)))
                result.append(er_public_secret)

        return result

    @property
    def fairness_formulae_for_secrets(self):
        result = []
        for secret in self.wrapper.secrets:
            committed = AtomicFormula(TermNaming.public_secret_is_x_prop(secret.secret_id, PublicSecretValues.COMMITTED))
            valid = AtomicFormula(TermNaming.public_secret_is_x_prop(secret.secret_id, PublicSecretValues.VALID))
            result.append(OrFormula(committed, valid))
        return result
