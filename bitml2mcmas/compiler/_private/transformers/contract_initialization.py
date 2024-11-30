from bitml2mcmas.bitml.ast import BitMLSecretPrecondition
from bitml2mcmas.compiler._private.mcmas_builder import AgentBuilder
from bitml2mcmas.compiler._private.terms import (
    CONTRACT_INITIALIZED,
    CONTRACT_IS_INITIALIZED,
    INITIALIZE_CONTRACT,
    NOP,
    PublicSecretValues,
    TermNaming,
)
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import (
    BooleanVarType,
    Effect,
    EvaluationRule,
    EvolutionRule,
    ProtocolRule,
    VarDefinition,
)
from bitml2mcmas.mcmas.boolcond import (
    BooleanCondition,
    EnvironmentIdAtom,
    EqualTo,
    IdAtom,
    TrueBoolValue,
)
from bitml2mcmas.mcmas.formula import AtomicFormula, FormulaType


class AddContractInitialization(Transformer):
    def apply(self) -> None:
        self.env.add_env_obs_var(self.contract_initialized_vardef)

        self.env.add_evolution_rule(self.evolution_rule_initialize_contract)

        for participant_id, ag_builder in self.get_agent_builders():
            self._handle_agent(participant_id, ag_builder)

        self.builder.add_initial_state_boolean_condition(
            self.objects.contract_initialized_to_false
        )

        self.builder.add_evaluation_rule(self.evaluation_rule_contract_is_initialized)

        # TODO: understand issues with this fairness condition
        # self.builder.add_fairness_formula(self.contract_is_initialized_fairness_formula)

    def _handle_agent(self, participant_id: str, ag_builder: AgentBuilder) -> None:
        ag_builder.add_action(INITIALIZE_CONTRACT)
        ag_builder.add_protocol_rule(self.get_protocol_rule_initialize_contract(participant_id))

    @property
    def contract_initialized_vardef(self) -> VarDefinition:
        return VarDefinition(CONTRACT_INITIALIZED, BooleanVarType())

    def get_protocol_rule_initialize_contract(self, participant_id: str) -> ProtocolRule:
        condition = self.objects.contract_initialized_to_false
        if self.wrapper.has_timeouts:
            condition &= self.objects.get_agent_done_is_false_with_env(participant_id)
        if self.wrapper.has_secrets:
            condition &= self.objects.secret_all_committed_or_revealed_condition
        return ProtocolRule(
            condition,
            {INITIALIZE_CONTRACT, NOP},
        )

    def get_is_public_secret_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.COMMITTED.value),
        )

    @property
    def evolution_rule_initialize_contract(self) -> EvolutionRule:
        contract_initialization_condition = (
            self.objects.contract_initialized_to_false_for_env
        )

        if self.wrapper.has_secrets:
            contract_initialization_condition &= (
                self.objects.secret_all_committed_or_revealed_condition_for_env
            )

        # any participant took action initialize_contract (and it is scheduled)
        initialize_contract_action_taken = (
            self.objects.get_some_scheduled_agent_calls_action_condition(
                INITIALIZE_CONTRACT
            )
        )
        contract_initialization_condition &= initialize_contract_action_taken

        er = EvolutionRule(
            [Effect(CONTRACT_INITIALIZED, TrueBoolValue())],
            contract_initialization_condition,
        )
        return er

    @property
    def evaluation_rule_contract_is_initialized(self):
        return EvaluationRule(
            CONTRACT_IS_INITIALIZED,
            EqualTo(EnvironmentIdAtom(CONTRACT_INITIALIZED), TrueBoolValue()),
        )

    @property
    def contract_is_initialized_fairness_formula(self) -> FormulaType:
        return AtomicFormula(CONTRACT_IS_INITIALIZED)
