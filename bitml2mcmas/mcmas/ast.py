"""Core abstractions for the BitML abstract syntax tree."""

import dataclasses
from collections.abc import Sequence
from enum import Enum
from typing import AbstractSet, Annotated, Any, Union, cast

from bitml2mcmas.helpers.misc import assert_
from bitml2mcmas.helpers.validation import (
    AllowNone,
    SequenceConstraint,
    SetConstraint,
    TypeIs,
    _BaseDataClass,
    _Processor,
)
from bitml2mcmas.mcmas.boolcond import (
    BooleanCondition,
    Expression,
)
from bitml2mcmas.mcmas.custom_types import IdOrEnv, McmasId
from bitml2mcmas.mcmas.exceptions import McmasValidationError
from bitml2mcmas.mcmas.formula import FormulaType
from bitml2mcmas.mcmas.validation.is_agent_evolution_condition import (
    _IsAgentEvolutionCondition,
)
from bitml2mcmas.mcmas.validation.is_agent_protocol_condition import (
    _IsAgentProtocolCondition,
    is_agent_protocol_condition,
)
from bitml2mcmas.mcmas.validation.is_env_evolution_condition import (
    _IsEnvEvolutionCondition,
)
from bitml2mcmas.mcmas.validation.is_env_protocol_condition import (
    _IsEnvProtocolCondition,
    is_env_protocol_condition,
)
from bitml2mcmas.mcmas.validation.is_fair_formula import _IsFairFormula
from bitml2mcmas.mcmas.validation.is_initial_state_condition import (
    _IsInitialStateCondition,
)


class Semantics(Enum):
    MULTI_ASSIGNMENT = "MultiAssignment"
    SINGLE_ASSIGNMENT = "SingleAssignment"


@dataclasses.dataclass(frozen=True)
class BooleanVarType:
    pass


@dataclasses.dataclass(frozen=True)
class IntegerRangeVarType(_BaseDataClass):
    lower: Annotated[int, TypeIs(int)]
    upper: Annotated[int, TypeIs(int)]

    def __post_init__(self) -> None:
        super().__post_init__()
        self._lower_bound_smaller_than_upper_bound()

    def _lower_bound_smaller_than_upper_bound(self) -> None:
        if not (self.lower < self.upper):
            raise McmasValidationError(
                f"integer range type not valid: expected lower bound {self.lower!r} smaller than upper bound {self.upper!r}"
            )


@dataclasses.dataclass(frozen=True)
class EnumVarType(_BaseDataClass):
    values: Annotated[
        AbstractSet[McmasId], SetConstraint(min_items=1, item_type=McmasId)
    ]


VarType = Union[BooleanVarType, IntegerRangeVarType, EnumVarType]


@dataclasses.dataclass(frozen=True)
class VarDefinition(_BaseDataClass):
    varname: McmasId
    vartype: VarType


@dataclasses.dataclass(frozen=True)
class _UniqueVarDefinitions(_Processor):
    min_items: int | None = None

    def process(self, value: Any) -> Any:
        value = SequenceConstraint(
            min_items=self.min_items, item_type=VarDefinition
        ).process(value)
        all_varnames_list = [vardef.varname for vardef in value]
        SequenceConstraint(unique_items=True).process(all_varnames_list)
        return value


@dataclasses.dataclass(frozen=True)
class AgentActions(_BaseDataClass):
    actions: Annotated[
        AbstractSet[McmasId], SetConstraint(min_items=1, item_type=McmasId)
    ]


@dataclasses.dataclass(frozen=True)
class ProtocolRule(_BaseDataClass):
    condition: Annotated[BooleanCondition, TypeIs(BooleanCondition)]
    enabled_actions: Annotated[
        AbstractSet[McmasId], SetConstraint(min_items=1, item_type=McmasId)
    ]


@dataclasses.dataclass(frozen=True)
class Protocol(_BaseDataClass):
    rules: Annotated[
        Sequence[ProtocolRule] | None,
        AllowNone(SequenceConstraint(min_items=1, item_type=ProtocolRule)),
    ]
    other_rule: Annotated[
        AbstractSet[McmasId] | None,
        AllowNone(SetConstraint(min_items=1, item_type=McmasId)),
    ]


@dataclasses.dataclass(frozen=True)
class Effect:
    varname: McmasId
    value: Expression


@dataclasses.dataclass(frozen=True)
class EvolutionRule(_BaseDataClass):
    effects: Annotated[
        Sequence[Effect], SequenceConstraint(min_items=1, item_type=Effect)
    ]
    condition: Annotated[BooleanCondition, TypeIs(BooleanCondition)]


@dataclasses.dataclass(frozen=True)
class EvaluationRule:
    prop_id: McmasId
    condition: Annotated[BooleanCondition, TypeIs(BooleanCondition)]


@dataclasses.dataclass(frozen=True)
class _UniqueEvaluationRuleDefinitions(_Processor):
    min_items: int | None = None

    def process(self, value: Any) -> Any:
        value = SequenceConstraint(
            min_items=self.min_items, item_type=EvaluationRule
        ).process(value)
        all_proposition_list = [eval_rule.prop_id for eval_rule in value]
        SequenceConstraint(unique_items=True).process(all_proposition_list)
        return value


@dataclasses.dataclass(frozen=True)
class Group(_BaseDataClass):
    group_name: McmasId
    agents: Annotated[
        AbstractSet[IdOrEnv], SetConstraint(min_items=1, item_type=IdOrEnv)
    ]


class _IsEnvProtocol(_Processor):
    def process(self, value: Any) -> Any:
        assert_(isinstance(value, Protocol))
        protocol = cast(Protocol, value)
        if protocol.rules is not None:
            for rule in protocol.rules:
                if not is_env_protocol_condition(rule.condition):
                    raise McmasValidationError(
                        f"boolean condition {rule.condition!r} is not a valid boolean condition for environment protocol rules"
                    )
        return protocol


_ObsVarDef = Annotated[
    Sequence[VarDefinition] | None, AllowNone(_UniqueVarDefinitions(min_items=0))
]
_EnvVarDef = Annotated[
    Sequence[VarDefinition] | None, AllowNone(_UniqueVarDefinitions(min_items=0))
]
_EnvRedStatesDef = Annotated[
    BooleanCondition | None,
    AllowNone(TypeIs(BooleanCondition)),
    AllowNone(_IsEnvProtocolCondition()),
]
_EnvActionsDef = Annotated[
    AbstractSet[McmasId], SetConstraint(min_items=0, item_type=McmasId)
]
_EnvProtocolDef = Annotated[Protocol, TypeIs(Protocol), _IsEnvProtocol()]
_EnvEvolutionDef = Annotated[
    Sequence[EvolutionRule],
    SequenceConstraint(
        min_items=0, item_type=Annotated[EvolutionRule, _IsEnvEvolutionCondition()]
    ),
]


@dataclasses.dataclass(frozen=True)
class Environment(_BaseDataClass):
    obs_var_definitions: _ObsVarDef
    env_var_definitions: _EnvVarDef
    env_red_definitions: _EnvRedStatesDef
    env_action_definitions: _EnvActionsDef
    env_protocol_definition: _EnvProtocolDef
    env_evolution_definition: _EnvEvolutionDef


class _IsAgentProtocol(_Processor):
    def process(self, value: Any) -> Any:
        assert_(isinstance(value, Protocol))
        value = cast(Protocol, value)
        if value.rules is None and value.other_rule is None:
            raise McmasValidationError("agent protocols must define at least one rule")

        protocol = cast(Protocol, value)
        if protocol.rules is not None:
            for rule in protocol.rules:
                if not is_agent_protocol_condition(rule.condition):
                    raise McmasValidationError(
                        f"boolean condition {rule.condition!r} is not a valid boolean condition for agent protocol rules"
                    )
        return value


_LobsVarDef = Annotated[
    Sequence[McmasId] | None,
    AllowNone(SequenceConstraint(min_items=0, item_type=McmasId, unique_items=True)),
]
_AgentVarDef = Annotated[Sequence[VarDefinition], _UniqueVarDefinitions(min_items=1)]
_RedStatesDef = Annotated[
    BooleanCondition | None,
    AllowNone(TypeIs(BooleanCondition)),
    AllowNone(_IsAgentProtocolCondition()),
]
_ActionDef = Annotated[
    AbstractSet[McmasId], SetConstraint(min_items=1, item_type=McmasId)
]
_AgentProtocol = Annotated[Protocol, TypeIs(Protocol), _IsAgentProtocol()]
_AgentEvolutionDef = Annotated[
    Sequence[EvolutionRule],
    SequenceConstraint(
        min_items=0, item_type=Annotated[EvolutionRule, _IsAgentEvolutionCondition()]
    ),
]


@dataclasses.dataclass(frozen=True)
class Agent(_BaseDataClass):
    name: McmasId
    lobs_var_definitions: _LobsVarDef
    agent_var_definitions: _AgentVarDef
    agent_red_definitions: _RedStatesDef
    agent_action_definitions: _ActionDef
    agent_protocol_definition: _AgentProtocol
    agent_evolution_definition: _AgentEvolutionDef


_EvaluationRules = Annotated[
    Sequence[EvaluationRule],
    SequenceConstraint(min_items=1, item_type=EvaluationRule),
    _UniqueEvaluationRuleDefinitions(min_items=1),
]
_InitStates = Annotated[
    BooleanCondition,
    TypeIs(BooleanCondition),
    _IsInitialStateCondition(),
]
_Groups = Annotated[Sequence[Group], SequenceConstraint(min_items=1, item_type=Group)]
_FairFormulae = Annotated[
    Sequence[FormulaType],
    SequenceConstraint(
        min_items=0,
        item_type=Annotated[FormulaType, TypeIs(FormulaType), _IsFairFormula()],
    ),
]
_Formulae = Annotated[
    Sequence[FormulaType], SequenceConstraint(min_items=0, item_type=FormulaType)
]


@dataclasses.dataclass(frozen=True)
class InterpretedSystem(_BaseDataClass):
    semantics: Annotated[Semantics | None, TypeIs(Semantics)]
    environment: Annotated[Environment | None, TypeIs(Environment, type(None))]
    agents: Annotated[Sequence[Agent], SequenceConstraint(min_items=1, item_type=Agent)]
    evaluation_rules: _EvaluationRules
    initial_states_boolean_condition: _InitStates
    groups: _Groups
    fair_formulae: _FairFormulae
    formulae: _Formulae
