from collections.abc import Sequence

from bitml2mcmas.compiler._private.terms import CONTRACT_FUNDS, TermNaming
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import BooleanVarType, IntegerRangeVarType, VarDefinition
from bitml2mcmas.mcmas.boolcond import (
    BooleanCondition,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    IntAtom,
)


class AddDeposits(Transformer):
    def apply(self) -> None:
        self._handle_env()

    def _handle_env(self):
        self.env.add_env_obs_var(self.contract_funds_vardef)
        self.env.add_env_obs_vars(self.participant_total_deposits_vardefs)
        self.env.add_env_obs_vars(self.volatile_deposit_status_vardefs)

        self.builder.add_initial_state_boolean_condition(
            self.contract_funds_initial_state_condition
        )
        self.builder.add_initial_state_boolean_conditions(
            self.participant_total_deposits_initial_state_conditions
        )
        self.builder.add_initial_state_boolean_conditions(
            self.volatile_deposit_status_initial_state_condition
        )

    @property
    def vartype_total_deposits(self):
        return IntegerRangeVarType(0, self.wrapper.total_deposit_amount)

    @property
    def contract_funds_vardef(self) -> VarDefinition:
        vartype_total_deposits = self.vartype_total_deposits
        contract_funds_vardef = VarDefinition(CONTRACT_FUNDS, vartype_total_deposits)
        return contract_funds_vardef

    @property
    def contract_funds_initial_state_condition(self) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(CONTRACT_FUNDS),
            IntAtom(self.wrapper.total_persistent_deposit_amount),
        )

    @property
    def participant_total_deposits_vardefs(self) -> Sequence[VarDefinition]:
        result = []
        for participant_id in self.wrapper.participant_ids:
            varname = TermNaming.participant_total_deposits(participant_id)
            vardef = VarDefinition(varname, self.vartype_total_deposits)
            result.append(vardef)
        return result

    @property
    def participant_total_deposits_initial_state_conditions(
        self,
    ) -> Sequence[BooleanCondition]:
        result = []
        # initial participant total funds set to volatile deposits
        for participant_id in self.wrapper.participant_ids:
            varname = TermNaming.participant_total_deposits(participant_id)
            voldeposits = self.wrapper.volatile_deposits_by_participant_id.get(
                participant_id, []
            )
            total_deposits = sum([int(vd.amount) for vd in voldeposits])
            result.append(EqualTo(EnvironmentIdAtom(varname), IntAtom(total_deposits)))

        return result

    @property
    def volatile_deposit_status_vardefs(self) -> Sequence[VarDefinition]:
        result = []
        # volatile deposits spent or not
        for deposit_name in self.wrapper.volatile_deposit_names:
            vardef = VarDefinition(
                TermNaming.deposit_spent_var(deposit_name), BooleanVarType()
            )
            result.append(vardef)
        return result

    @property
    def volatile_deposit_status_initial_state_condition(
        self,
    ) -> Sequence[BooleanCondition]:
        result = []
        for deposit_name in self.wrapper.volatile_deposit_names:
            result.append(
                EqualTo(
                    EnvironmentIdAtom(TermNaming.deposit_spent_var(deposit_name)),
                    FalseBoolValue(),
                )
            )
        return result
