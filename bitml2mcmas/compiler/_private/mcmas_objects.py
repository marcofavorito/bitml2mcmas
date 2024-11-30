import operator
from functools import reduce
from typing import cast

from bitml2mcmas.bitml.ast import BitMLSecretPrecondition
from bitml2mcmas.compiler._private.contract_wrapper import ContractWrapper
from bitml2mcmas.compiler._private.terms import (
    CONTRACT_INITIALIZED,
    DELAY,
    INITIALIZE_CONTRACT,
    LAST_ACTION,
    PrivateSecretValues,
    PublicSecretValues,
    TermNaming
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AgentActionEqualToConstraint,
    BooleanCondition,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    IdAtom,
    TrueBoolValue, OrBooleanCondition,
)
from bitml2mcmas.mcmas.custom_types import McmasId


class McmasObjects:
    def __init__(self, wrapper: ContractWrapper) -> None:
        self.__wrapper = wrapper

    @property
    def wrapper(self):
        return self.__wrapper

    def get_scheduling_action_for_agent(self, participant_id: str) -> McmasId:
        return TermNaming.scheduling_action_from_participant_id(participant_id)

    @property
    def scheduling_actions(self) -> set[McmasId]:
        return set(
            TermNaming.scheduling_action_from_participant_id(participant_id)
            for participant_id in self.wrapper.participant_ids
        )

    def get_is_agent_scheduled_condition(self, participant_id: str) -> BooleanCondition:
        scheduling_action_for_agent = self.get_scheduling_action_for_agent(
            participant_id
        )
        is_agent_scheduled = EnvironmentActionEqualToConstraint(
            scheduling_action_for_agent
        )
        return is_agent_scheduled

    def get_is_agent_scheduled_condition_for_env(
        self, participant_id: str
    ) -> BooleanCondition:
        scheduling_action_for_agent = self.get_scheduling_action_for_agent(
            participant_id
        )
        is_agent_scheduled = ActionEqualToConstraint(scheduling_action_for_agent)
        return is_agent_scheduled

    def get_agent_done_varname(self, participant_id: str) -> str:
        return TermNaming.agent_done_varname(participant_id)

    def get_agent_done_is_false_with_env(self, participant_id: str) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(self.get_agent_done_varname(participant_id)), FalseBoolValue()
        )

    def get_agent_done_is_false(self, participant_id: str) -> BooleanCondition:
        return EqualTo(
            IdAtom(self.get_agent_done_varname(participant_id)), FalseBoolValue()
        )

    def get_agent_done_is_true(self, participant_id: str) -> BooleanCondition:
        return EqualTo(
            IdAtom(self.get_agent_done_varname(participant_id)), TrueBoolValue()
        )

    @property
    def all_agent_done_are_false(self) -> BooleanCondition:
        clauses = []
        for participant_id in self.wrapper.participant_ids:
            clauses.append(self.get_agent_done_is_false_with_env(participant_id))
        return reduce(operator.and_, clauses)

    @property
    def all_agent_done_are_true(self) -> BooleanCondition:
        clauses = []
        for participant_id in self.wrapper.participant_ids:
            clauses.append(self.get_agent_done_is_true(participant_id))
        return reduce(operator.and_, clauses)

    @property
    def contract_initialized_to_false_for_env(self) -> BooleanCondition:
        return EqualTo(IdAtom(CONTRACT_INITIALIZED), FalseBoolValue())

    @property
    def contract_initialized_to_false(self):
        return EqualTo(EnvironmentIdAtom(CONTRACT_INITIALIZED), FalseBoolValue())

    @property
    def contract_initialized_to_true_for_env(self) -> BooleanCondition:
        return EqualTo(IdAtom(CONTRACT_INITIALIZED), TrueBoolValue())

    @property
    def contract_initialized_to_true(self) -> BooleanCondition:
        return EqualTo(EnvironmentIdAtom(CONTRACT_INITIALIZED), TrueBoolValue())

    def get_is_public_secret_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(
                TermNaming.secret_name_with_prefix_public(secret.secret_id)
            ),
            IdAtom(PublicSecretValues.COMMITTED.value),
        )

    def get_is_public_secret_revealed(self, secret: BitMLSecretPrecondition):
        return EqualTo(
            EnvironmentIdAtom(
                TermNaming.secret_name_with_prefix_public(secret.secret_id)
            ),
            IdAtom(PublicSecretValues.VALID.value),
        )

    def get_is_public_secret_committed_for_env(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.COMMITTED.value),
        )

    def get_is_public_secret_not_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.NOT_COMMITTED.value),
        )

    @property
    def secret_all_committed_or_revealed_condition(self) -> BooleanCondition:
        if len(self.wrapper.secrets) == 0:
            raise ValueError("the contract does not have secrets")

        conditions = [
            OrBooleanCondition(self.get_is_public_secret_committed(secret), self.get_is_public_secret_revealed(secret))
            for secret in self.wrapper.secrets
        ]
        return cast(BooleanCondition, reduce(operator.and_, conditions))

    @property
    def secret_all_committed_or_revealed_condition_for_env(self) -> BooleanCondition:
        if len(self.wrapper.secrets) == 0:
            raise ValueError("the contract does not have secrets")

        conditions = [
            OrBooleanCondition(self.get_is_public_secret_committed_for_env(secret), self.get_is_public_secret_revealed_for_env(secret))
            for secret in self.wrapper.secrets
        ]
        return cast(BooleanCondition, reduce(operator.and_, conditions))

    def get_is_private_secret_valid(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_private(secret.secret_id)),
            IdAtom(PrivateSecretValues.VALID.value),
        )

    def get_is_private_secret_invalid(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_private(secret.secret_id)),
            IdAtom(PrivateSecretValues.INVALID.value),
        )

    def get_is_private_secret_committed(
        self, secret: BitMLSecretPrecondition
    ) -> BooleanCondition:
        return self.get_is_private_secret_valid(
            secret
        ) & self.get_is_private_secret_invalid(secret)

    @property
    def last_action_equal_to_delay(self) -> BooleanCondition:
        return EqualTo(
            EnvironmentIdAtom(LAST_ACTION),
            IdAtom(TermNaming.action_with_prefix(DELAY)),
        )

    def get_some_scheduled_agent_calls_action_condition(
        self, action: str
    ) -> BooleanCondition:
        clauses = []
        for participant_id in self.wrapper.participant_ids:
            agent_name = TermNaming.agent_name_from_participant_name(participant_id)
            is_scheduled = self.get_is_agent_scheduled_condition_for_env(participant_id)
            is_action_taken = AgentActionEqualToConstraint(agent_name, action)
            clauses.append(is_scheduled & is_action_taken)
        return reduce(operator.or_, clauses)

    @property
    def initialized_now_or_already_initialized(self) -> BooleanCondition:
        initialized_now = self.get_some_scheduled_agent_calls_action_condition(
            INITIALIZE_CONTRACT
        )
        already_initialized = EqualTo(IdAtom(CONTRACT_INITIALIZED), TrueBoolValue())
        return initialized_now | already_initialized

    def get_is_public_secret_revealed_for_env(self, secret):
        return EqualTo(
            IdAtom(TermNaming.secret_name_with_prefix_public(secret.secret_id)),
            IdAtom(PublicSecretValues.VALID.value),
        )
