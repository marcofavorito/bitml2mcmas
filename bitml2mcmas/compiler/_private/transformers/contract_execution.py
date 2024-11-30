import operator
from abc import ABC, abstractmethod
from collections import deque
from collections.abc import Sequence
from functools import reduce

from bitml2mcmas.bitml.ast import (
    BitMLChoiceExpression,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLRevealExpression,
    BitMLSplitExpression,
    BitMLWithdrawExpression,
)
from bitml2mcmas.compiler._private.contract_graph import BitMLNode
from bitml2mcmas.compiler._private.contract_wrapper import ContractWrapper
from bitml2mcmas.compiler._private.mcmas_builder import AgentBuilder
from bitml2mcmas.compiler._private.mcmas_objects import McmasObjects
from bitml2mcmas.compiler._private.terms import (
    CONTRACT_FUNDS,
    DELAY,
    NOP,
    TIME,
    BitMLExprStatus,
    PublicSecretValues,
    TermNaming,
)
from bitml2mcmas.compiler._private.transformers.base import Transformer
from bitml2mcmas.mcmas.ast import (
    BooleanVarType,
    Effect,
    EnumVarType,
    EvolutionRule,
    ProtocolRule,
    VarDefinition, EvaluationRule,
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AddExpr,
    AgentActionEqualToConstraint,
    BooleanCondition,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    GreaterThanOrEqual,
    IdAtom,
    IntAtom,
    SubtractExpr,
    TrueBoolValue,
)


class _AbstractBitMLNodeWrapper(ABC):
    def __init__(
        self, node: BitMLNode, wrapper: ContractWrapper, objects: McmasObjects
    ):
        self.__node = node
        self.__wrapper = wrapper
        self.__objects = objects

    @property
    def node(self):
        return self.__node

    @property
    def wrapper(self):
        return self.__wrapper

    @property
    def objects(self):
        return self.__objects

    @property
    def enabled_condition(self) -> BooleanCondition:
        condition = self.is_parent_executed_condition & self.is_disabled
        return self._apply_auth_and_after_conditions(condition)

    @property
    def vardefs(self) -> list[VarDefinition]:
        result = []

        # add variables for guards, if any
        for auth in self.node.auths:
            auth_varname = TermNaming.authorized_by_variable(
                self.node.full_node_id, auth
            )
            result.append(VarDefinition(auth_varname, BooleanVarType()))
            # TODO: should auth be considered always enabled?

        # add enabled variable for main expr
        result.append(self.vardef_expr_status)

        return result

    @property
    def vardef_expr_status(self) -> VarDefinition:
        main_expr_status_varname = TermNaming.expression_node_id_status(
            self.node.full_node_id
        )
        vartype = EnumVarType(BitMLExprStatus.values())
        return VarDefinition(main_expr_status_varname, vartype)

    @property
    def initial_conditions(self) -> Sequence[BooleanCondition]:
        result = []

        # add variables for guards, if any
        for auth in self.node.auths:
            auth_varname = TermNaming.authorized_by_variable(
                self.node.full_node_id, auth
            )
            result.append(EqualTo(EnvironmentIdAtom(auth_varname), FalseBoolValue()))

        # add variable for main expr
        main_expr_status_varname = TermNaming.expression_node_id_status(
            self.node.full_node_id
        )
        result.append(
            EqualTo(
                EnvironmentIdAtom(main_expr_status_varname),
                IdAtom(BitMLExprStatus.DISABLED.value),
            )
        )

        return result

    @property
    def auth_condition(self) -> BooleanCondition | None:
        if len(self.node.auths) == 0:
            return None

        conditions = []
        for auth in self.node.auths:
            authorized_by_variable = TermNaming.authorized_by_variable(
                self.node.full_node_id, auth
            )
            authorizer = TermNaming.agent_name_from_participant_name(auth)
            authorize_action = TermNaming.authorize_action(self.node.full_node_id)
            already_authorized = EqualTo(
                IdAtom(authorized_by_variable), TrueBoolValue()
            )
            authorized_now = AgentActionEqualToConstraint(authorizer, authorize_action) & self.objects.get_is_agent_scheduled_condition_for_env(auth)
            conditions.append(already_authorized | authorized_now)

        return reduce(operator.and_, conditions)

    @property
    def after_condition(self) -> BooleanCondition | None:
        if len(self.node.afters) == 0:
            return None

        # get maximum timeout of node
        max_timeout = max(self.node.afters)
        previous_t = max_timeout - 1
        time_greater_than_t = GreaterThanOrEqual(IdAtom(TIME), IntAtom(max_timeout))
        previous_time_and_delay = EqualTo(
            IdAtom(TIME), IntAtom(previous_t)
        ) & ActionEqualToConstraint(DELAY)
        return time_greater_than_t | previous_time_and_delay

    def _apply_auth_and_after_conditions(
        self, condition: BooleanCondition
    ) -> BooleanCondition:
        auth_condition = self.auth_condition
        if auth_condition is not None:
            condition &= auth_condition

        after_condition = self.after_condition
        if after_condition is not None:
            condition &= after_condition

        return condition

    def _check_at_least_one_other_choice_children_executed(self) -> BooleanCondition | None:
        assert self.node.parent is not None and type(self.node.parent.expression) == BitMLChoiceExpression

        # check if at least one operand of the parent's node choice expression has been executed.
        or_clauses = []
        for branch_node in self.node.parent.children:
            if branch_node == self.node:
                continue
            wrapped_branch = wrap(branch_node, self.wrapper, self.objects)
            is_executed = wrapped_branch.is_executed_now_or_earlier
            or_clauses.append(is_executed)

        disable_condition = reduce(operator.or_, or_clauses)
        return disable_condition

    def _check_all_other_choice_children_not_executed(self, condition: BooleanCondition) -> BooleanCondition:
        if self.node.parent is None or type(self.node.parent.expression) != BitMLChoiceExpression:
            # do nothing
            return condition

        # check if at least one operand of the parent's node choice expression has been executed.
        or_clauses = []
        for branch_node in self.node.parent.children:
            if branch_node == self.node:
                continue
            wrapped_branch = wrap(branch_node, self.wrapper, self.objects)
            is_executed = wrapped_branch.is_executed_now_or_earlier
            or_clauses.append(~is_executed)

        enable_condition = reduce(operator.and_, or_clauses)
        return condition & enable_condition

    @property
    def is_disabled(self) -> BooleanCondition:
        return EqualTo(
            IdAtom(self.status_varname), IdAtom(BitMLExprStatus.DISABLED.value)
        )

    @property
    def status_varname(self) -> str:
        return TermNaming.expression_node_id_status(self.node.full_node_id)

    @property
    def exec_action_name(self) -> str:
        return TermNaming.exec_expression_node_id(self.node.full_node_id)

    @property
    def is_already_executed(self) -> BooleanCondition:
        return EqualTo(
            IdAtom(self.status_varname), IdAtom(BitMLExprStatus.EXECUTED.value)
        )

    @property
    def is_not_executed(self) -> BooleanCondition:
        return ~EqualTo(IdAtom(self.status_varname), IdAtom(BitMLExprStatus.EXECUTED.value))

    @property
    def is_exec_action_called_from_any_participant(self) -> BooleanCondition:
        # any participant can append transaction on the blockchain
        clauses = []
        exec_parent_action_name = TermNaming.exec_expression_node_id(
            self.node.full_node_id
        )
        for participant_id in self.wrapper.participant_ids:
            agent_name = TermNaming.agent_name_from_participant_name(participant_id)
            exec_parent_action_condition = AgentActionEqualToConstraint(
                agent_name, exec_parent_action_name
            )
            clauses.append(
                exec_parent_action_condition
                & self.objects.get_is_agent_scheduled_condition_for_env(participant_id)
            )
        return reduce(operator.or_, clauses)

    @property
    def is_executed_now_or_earlier(self):
        return (
            self.is_already_executed | self.is_exec_action_called_from_any_participant
        )

    @property
    def is_enabled(self):
        return EqualTo(
            EnvironmentIdAtom(self.status_varname),
            IdAtom(BitMLExprStatus.ENABLED.value),
        )

    @property
    def is_parent_executed_condition(self) -> BooleanCondition:
        if self.node.parent is None:
            return self.objects.initialized_now_or_already_initialized

        # first, determine whether the parent node is a choice expression:
        if isinstance(self.node.parent.expression, BitMLChoiceExpression):
            # in that case, we have to check the node above
            parent = self.node.parent.parent
            if parent is None:
                # case when choice is the root expression
                return self.objects.initialized_now_or_already_initialized
        else:
            parent = self.node.parent

        parent = wrap(parent, self.wrapper, self.objects)
        is_executed_cond = parent.is_executed_now_or_earlier
        return is_executed_cond

    @property
    @abstractmethod
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        raise NotImplementedError

    @property
    @abstractmethod
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        raise NotImplementedError

    @property
    def evolution_rules_is_disabled(self) -> Sequence[EvolutionRule]:
        if self.node.parent is None or type(self.node.parent.expression) != BitMLChoiceExpression:
            return []

        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.DISABLED.value))
        condition = self._check_at_least_one_other_choice_children_executed()
        return [EvolutionRule([effect], condition)]

    @property
    def get_exec_action_from_any_participant(self) -> BooleanCondition:
        clauses = []
        for participant_id in self.wrapper.participant_ids:
            agent_name = TermNaming.agent_name_from_participant_name(participant_id)
            is_scheduled = self.objects.get_is_agent_scheduled_condition_for_env(
                participant_id
            )
            exec_action = self.exec_action_name
            is_exec_action = AgentActionEqualToConstraint(agent_name, exec_action)
            clauses.append(is_scheduled & is_exec_action)
        condition = reduce(operator.or_, clauses)
        return condition

    @property
    def auth_evolution_rules(self) -> Sequence[EvolutionRule]:
        result = []
        for auth in self.node.auths:
            authorized_by_variable = TermNaming.authorized_by_variable(
                self.node.full_node_id, auth
            )
            authorizer = TermNaming.agent_name_from_participant_name(auth)
            authorize_action = TermNaming.authorize_action(self.node.full_node_id)
            authorized_now = AgentActionEqualToConstraint(authorizer, authorize_action)
            is_scheduled = self.objects.get_is_agent_scheduled_condition_for_env(auth)

            effect = Effect(authorized_by_variable, TrueBoolValue())
            result.append(EvolutionRule([effect], authorized_now & is_scheduled))
        return result

    @property
    def evolution_rule_is_executed(self) -> EvolutionRule:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.EXECUTED.value))
        return EvolutionRule([effect], self.is_exec_action_called_from_any_participant)

    @property
    def evaluation_rules(self) -> Sequence[EvaluationRule]:
        result = []

        for status in BitMLExprStatus:
            status_varname = TermNaming.expression_node_id_status(self.node.full_node_id)
            evaluation_rule = EvaluationRule(
                f"{self.node.full_node_id}_is_{status.value}",
                EqualTo(EnvironmentIdAtom(status_varname), IdAtom(status.value))
            )
            result.append(evaluation_rule)

        for auth in self.node.auths:
            authorized_by_varname = TermNaming.authorized_by_variable(self.node.full_node_id, auth)
            evaluation_rule = EvaluationRule(
                f"{self.node.full_node_id}_is_authorized_by_{auth}",
                EqualTo(EnvironmentIdAtom(authorized_by_varname), TrueBoolValue())
            )
            result.append(evaluation_rule)

        return result


class BitMLWithdrawNodeWrapper(_AbstractBitMLNodeWrapper):
    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        result = []
        exec_action_condition = self.get_exec_action_from_any_participant

        # withdraw all contract funds
        contract_funds_var = CONTRACT_FUNDS
        new_contract_fund_effect = Effect(
            contract_funds_var,
            SubtractExpr(IdAtom(contract_funds_var), IntAtom(int(self.node.funds))),
        )
        new_contract_fund_er = EvolutionRule(
            [new_contract_fund_effect], exec_action_condition
        )
        result.append(new_contract_fund_er)

        # transfer contract funds to destination address
        total_deposit_var = TermNaming.participant_total_deposits(
            self.node.expression.participant_id
        )
        new_total_deposit_effect = Effect(
            total_deposit_var,
            AddExpr(IdAtom(total_deposit_var), IntAtom(int(self.node.funds))),
        )
        new_total_deposit_er = EvolutionRule(
            [new_total_deposit_effect], exec_action_condition
        )
        result.append(new_total_deposit_er)

        # update status of expression node
        result.append(self.evolution_rule_is_executed)

        return result

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.ENABLED.value))
        condition = self.is_parent_executed_condition & self.is_disabled
        condition = self._apply_auth_and_after_conditions(condition)
        condition = self._check_all_other_choice_children_not_executed(condition)
        return [EvolutionRule([effect], condition)]


class BitMLChoiceNodeWrapper(_AbstractBitMLNodeWrapper):
    @property
    def vardefs(self) -> list[VarDefinition]:
        return []

    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        return []

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        return []

    @property
    def evaluation_rules(self) -> Sequence[EvaluationRule]:
        return []

    @property
    def initial_conditions(self) -> Sequence[BooleanCondition]:
        return []


class BitMLSplitNodeWrapper(_AbstractBitMLNodeWrapper):
    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        return [self.evolution_rule_is_executed]

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.ENABLED.value))
        condition = self.is_parent_executed_condition & self.is_disabled
        condition = self._apply_auth_and_after_conditions(condition)
        condition = self._check_all_other_choice_children_not_executed(condition)
        return [EvolutionRule([effect], condition)]


class _AbstractBitMLPutRevealNodeWrapper(_AbstractBitMLNodeWrapper):
    @property
    def evolution_rules_exec_action_put(self) -> Sequence[EvolutionRule]:
        result = []
        exec_action_condition = self.get_exec_action_from_any_participant

        # contract funds are increased
        contract_funds_var = CONTRACT_FUNDS
        new_contract_fund_effect = Effect(
            contract_funds_var,
            AddExpr(
                IdAtom(contract_funds_var), IntAtom(self.total_volatile_deposits_amount)
            ),
        )
        new_contract_fund_er = EvolutionRule(
            [new_contract_fund_effect], exec_action_condition
        )
        result.append(new_contract_fund_er)

        # volatile deposits become spent
        for deposit_id in self.node.expression.deposit_ids:
            # update spent status
            deposit_spent_var = TermNaming.deposit_spent_var_from_id(deposit_id)
            deposit_spent_effect = Effect(deposit_spent_var, TrueBoolValue())
            result.append(EvolutionRule([deposit_spent_effect], exec_action_condition))

            # decrease participant funds
            deposit = self.wrapper.volatile_deposits_by_id[deposit_id]
            participant_id = deposit.participant_id
            amount = deposit.amount
            participant_funds_varname = TermNaming.participant_total_deposits(
                participant_id
            )
            participant_funds_effect = Effect(
                participant_funds_varname,
                SubtractExpr(IdAtom(participant_funds_varname), IntAtom(amount)),
            )
            result.append(
                EvolutionRule([participant_funds_effect], exec_action_condition)
            )

        return result

    @property
    def total_volatile_deposits_amount(self) -> int:
        return sum(
            self.wrapper.volatile_deposits_by_id[deposit_id].amount
            for deposit_id in self.node.expression.deposit_ids
        )

    @property
    def are_volatile_deposits_unspent(self) -> BooleanCondition:
        clauses = []
        for deposit_id in self.node.expression.deposit_ids:
            deposit_spent_var = TermNaming.deposit_spent_var_from_id(deposit_id)
            clauses.append(EqualTo(IdAtom(deposit_spent_var), FalseBoolValue()))

        return reduce(operator.and_, clauses)

    @property
    def are_secrets_revealed(self) -> BooleanCondition:
        clauses = []
        for secret_id in self.node.expression.secret_ids:
            secret = self.wrapper.secrets_by_id[secret_id]
            secret_status = TermNaming.secret_name_with_prefix_public(secret_id)
            agent_name = TermNaming.agent_name_from_participant_name(
                secret.participant_id
            )
            reveal_action = TermNaming.reveal_action(secret_id)

            already_revealed = EqualTo(
                IdAtom(secret_status), IdAtom(PublicSecretValues.VALID.value)
            )
            revealed_now = AgentActionEqualToConstraint(
                agent_name, reveal_action
            ) & self.objects.get_is_agent_scheduled_condition_for_env(
                secret.participant_id
            )
            clauses.append(already_revealed | revealed_now)

        return reduce(operator.and_, clauses)


class BitMLPutNodeWrapper(_AbstractBitMLPutRevealNodeWrapper):
    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        return [self.evolution_rule_is_executed, *self.evolution_rules_exec_action_put]

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.ENABLED.value))
        condition = (
            self.is_parent_executed_condition
            & self.is_disabled
            & self.are_volatile_deposits_unspent
        )
        condition = self._apply_auth_and_after_conditions(condition)
        condition = self._check_all_other_choice_children_not_executed(condition)
        return [EvolutionRule([effect], condition)]


class BitMLRevealNodeWrapper(_AbstractBitMLPutRevealNodeWrapper):
    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        return [self.evolution_rule_is_executed]

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.ENABLED.value))
        condition = (
            self.is_parent_executed_condition
            & self.is_disabled
            & self.are_secrets_revealed
        )
        condition = self._apply_auth_and_after_conditions(condition)
        condition = self._check_all_other_choice_children_not_executed(condition)
        return [EvolutionRule([effect], condition)]


class BitMLPutRevealNodeWrapper(_AbstractBitMLPutRevealNodeWrapper):
    @property
    def evolution_rules_exec_action(self) -> Sequence[EvolutionRule]:
        return [self.evolution_rule_is_executed, *self.evolution_rules_exec_action_put]

    @property
    def evolution_rules_is_enabled(self) -> Sequence[EvolutionRule]:
        effect = Effect(self.status_varname, IdAtom(BitMLExprStatus.ENABLED.value))
        condition = (
            self.is_parent_executed_condition
            & self.is_disabled
            & self.are_secrets_revealed
            & self.are_volatile_deposits_unspent
        )
        condition = self._apply_auth_and_after_conditions(condition)
        condition = self._check_all_other_choice_children_not_executed(condition)
        return [EvolutionRule([effect], condition)]


def wrap(
    node: BitMLNode, wrapper: ContractWrapper, objects: McmasObjects
) -> _AbstractBitMLNodeWrapper:
    match node.expression:
        case BitMLWithdrawExpression():
            return BitMLWithdrawNodeWrapper(node, wrapper, objects)
        case BitMLChoiceExpression():
            return BitMLChoiceNodeWrapper(node, wrapper, objects)
        case BitMLPutExpression():
            return BitMLPutNodeWrapper(node, wrapper, objects)
        case BitMLRevealExpression():
            return BitMLRevealNodeWrapper(node, wrapper, objects)
        case BitMLPutRevealExpression():
            return BitMLPutRevealNodeWrapper(node, wrapper, objects)
        case BitMLSplitExpression():
            return BitMLSplitNodeWrapper(node, wrapper, objects)
        case _:
            raise ValueError(f"case {node.expression!r} not handled")


class AddContractExecution(Transformer):
    def apply(self) -> None:
        for node in self.wrapper.graph.nodes:
            self._handle_node(node)

    def _handle_node(self, node: BitMLNode):
        wrapped = wrap(node, self.wrapper, self.objects)

        self.env.add_env_obs_vars(wrapped.vardefs)
        self.env.add_evolution_rules(wrapped.evolution_rules_exec_action)
        self.env.add_evolution_rules(wrapped.auth_evolution_rules)
        self.env.add_evolution_rules(wrapped.evolution_rules_is_enabled)
        self.env.add_evolution_rules(wrapped.evolution_rules_is_disabled)
        self.builder.add_evaluation_rules(wrapped.evaluation_rules)

        self._process_agents(wrapped)

        self.builder.add_initial_state_boolean_conditions(wrapped.initial_conditions)

    def _process_agents(self, wrapped_node: _AbstractBitMLNodeWrapper):
        for participant_id, ag_builder in self.get_agent_builders():
            self._process_agent(wrapped_node, participant_id, ag_builder)

    def _process_agent(
        self,
        wrapped_node: _AbstractBitMLNodeWrapper,
        participant_id: str,
        ag_builder: AgentBuilder,
    ):
        # anyone can execute a node
        self._add_exec_action_for_agent(wrapped_node, participant_id, ag_builder)

        # add authorization
        self._add_authorization_action_for_agent(
            wrapped_node, participant_id, ag_builder
        )

    def _add_exec_action_for_agent(
        self,
        wrapped_node: _AbstractBitMLNodeWrapper,
        participant_id: str,
        ag_builder: AgentBuilder,
    ):
        if isinstance(wrapped_node.node.expression, BitMLChoiceExpression):
            # choice nodes have no associated action
            return

        ag_builder.add_action(wrapped_node.exec_action_name)

        condition = wrapped_node.is_enabled

        if self.wrapper.has_timeouts:
            condition &= self.objects.get_agent_done_is_false_with_env(participant_id)

        ag_builder.add_protocol_rule(
            ProtocolRule(condition, {wrapped_node.exec_action_name, NOP})
        )

    def _add_authorization_action_for_agent(
        self,
        wrapped_node: _AbstractBitMLNodeWrapper,
        participant_id: str,
        ag_builder: AgentBuilder,
    ):
        if participant_id in wrapped_node.node.auths:
            authorize_action = TermNaming.authorize_action(
                wrapped_node.node.full_node_id
            )
            authorized_by_var = TermNaming.authorized_by_variable(
                wrapped_node.node.full_node_id, participant_id
            )
            authorized_by_is_false = EqualTo(
                EnvironmentIdAtom(authorized_by_var), FalseBoolValue()
            )
            ag_builder.add_action(authorize_action)

            protocol_condition = (
                authorized_by_is_false & self.objects.contract_initialized_to_true
            )
            if self.wrapper.has_timeouts:
                protocol_condition &= self.objects.get_agent_done_is_false_with_env(
                    participant_id
                )

            ag_builder.add_protocol_rule(
                ProtocolRule(
                    protocol_condition,
                    {authorize_action, NOP},
                )
            )
