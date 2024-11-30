"""Compile a BitML contract into a MCMAS program."""

import itertools
from collections.abc import Sequence

from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.compiler._private.contract_wrapper import ContractWrapper
from bitml2mcmas.compiler._private.mcmas_builder import MCMASBuilder
from bitml2mcmas.compiler._private.terms import PARTICIPANTS_GROUP, ENV_GROUP, PARTICIPANTS_AND_ENV_GROUP
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.compiler._private.transformers.contract_execution import (
    AddContractExecution,
)
from bitml2mcmas.compiler._private.transformers.contract_initialization import (
    AddContractInitialization,
)
from bitml2mcmas.compiler._private.transformers.deposits import AddDeposits
from bitml2mcmas.compiler._private.transformers.last_action import AddLastAction
from bitml2mcmas.compiler._private.transformers.scheduling import AddSchedulingActions
from bitml2mcmas.compiler._private.transformers.secrets import AddSecrets
from bitml2mcmas.compiler._private.transformers.time_progression import (
    AddTimeProgression,
)
from bitml2mcmas.compiler.check_supported import check_supported
from bitml2mcmas.mcmas.ast import EvaluationRule, Group, InterpretedSystem, VarDefinition, BooleanVarType, \
    EvolutionRule, Effect
from bitml2mcmas.mcmas.boolcond import AttributeIdAtom, FalseBoolValue, EqualTo, TrueBoolValue, IdAtom
from bitml2mcmas.mcmas.custom_types import ENVIRONMENT, McmasId
from bitml2mcmas.mcmas.formula import FormulaType
from typing import AbstractSet


class Compiler:
    def __init__(
        self,
        contract: BitMLContract,
        formulae: Sequence[FormulaType],
        evaluation_rules: Sequence[EvaluationRule] | None = None,
        groups: set[Group] | None = None,
    ) -> None:
        self.__contract = contract
        self.__formulae = formulae
        self.__evaluation_rules = evaluation_rules
        self.__groups = groups

        check_supported(self.__contract)
        self._check_nb_formulae()

        self.__wrapper = ContractWrapper(self.__contract)
        self.__builder: MCMASBuilder | None = None

    @property
    def evaluation_rules(self) -> tuple[EvaluationRule]:
        return (
            self.__evaluation_rules if self.__evaluation_rules is not None else tuple()
        )

    @property
    def groups(self) -> AbstractSet[Group]:
        return (
            self.__groups if self.__groups is not None else set()
        )

    def _check_nb_formulae(self) -> None:
        if len(self.__formulae) == 0:
            raise ValueError("required at least one formula for the compilation")

    def compile(self) -> InterpretedSystem:
        self.__builder = MCMASBuilder()

        self._apply(AddSchedulingActions)
        self._apply(AddTimeProgression)
        self._apply(AddDeposits)
        self._apply(AddSecrets)
        self._apply(AddContractInitialization)
        self._apply(AddContractExecution)

        # this must be the last transformation since it requires the actions to be already defined
        self._apply(AddLastAction)

        self._add_groups()
        self._add_formulae()
        self._add_evaluation_rules()
        self._add_dummy_agent_vars()
        return self.__builder.compile()

    def _apply(self, cls: type[Transformer]):
        cls(self.__wrapper, self.__builder).apply()

    def _add_groups(self):
        agent_names = set(self.__builder.agent_names)
        self.__builder.add_group(Group(PARTICIPANTS_GROUP, agent_names))
        self.__builder.add_group(Group(ENV_GROUP, {ENVIRONMENT}))
        self.__builder.add_group(Group(PARTICIPANTS_AND_ENV_GROUP, agent_names.union({ENVIRONMENT})))

        # add all combinations of participants and environment
        for k in range(1, len(agent_names)):
            for comb in itertools.combinations(agent_names, k):
                group_name = "__".join(sorted(comb))
                self.__builder.add_group(Group(group_name, set(comb)))

        self.__builder.add_groups(self.groups)


    def _add_formulae(self):
        self.__builder.add_formulae(self.__formulae)

    def _add_evaluation_rules(self):
        self.__builder.add_evaluation_rules(self.evaluation_rules)

    @property
    def _dummy_varname(self):
        return "dummy"

    @property
    def _dummy_agent_var(self):
        return VarDefinition(self._dummy_varname, BooleanVarType())

    def _add_dummy_agent_vars(self):
        """Add dummy agent variables, if the number of variables is empty (MCMAS requires at least one var)."""
        for agent_name in self.__builder.agent_names:
            agent_builder = self.__builder.get_agent_builder(agent_name)
            if len(agent_builder.agent_var_definitions) == 0:
                agent_builder.add_agent_var(self._dummy_agent_var)
                dummy_initial_cond = EqualTo(AttributeIdAtom(agent_name, self._dummy_varname), FalseBoolValue())
                self.__builder.add_initial_state_boolean_condition(dummy_initial_cond)
                dummy_er = EvolutionRule([Effect(self._dummy_varname, FalseBoolValue())],
                                         EqualTo(IdAtom(self._dummy_varname), FalseBoolValue()))
                agent_builder.add_evolution_rule(dummy_er)
