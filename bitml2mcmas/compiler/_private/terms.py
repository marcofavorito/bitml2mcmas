"""Constants of the BitML2MCMAS compilation."""

import re

from bitml2mcmas.helpers.misc import ExtendedEnum, assert_

# nop action for agents and env
NOP = "nop"

LAST_ACTION = "last_action"
UNSET_ACTION = "unset"

# none value for previous_scheduled_agent
NONE = "none"

EXEC_PREFIX = "exec_"

PARTICIPANTS_GROUP = "Participants"
PARTICIPANTS_AND_ENV_GROUP = "ParticipantsAndEnv"
ENV_GROUP = "Env"


# secret values
class PublicSecretValues(ExtendedEnum):
    COMMITTED = "committed"
    NOT_COMMITTED = "not_committed"
    VALID = "valid"


class PrivateSecretValues(ExtendedEnum):
    VALID = "valid"
    INVALID = "invalid"
    NOT_COMMITTED = "not_committed"


class BitMLExprStatus(ExtendedEnum):
    DISABLED = "disabled"
    ENABLED = "enabled"
    EXECUTED = "executed"


# env vars
PREVIOUS_SCHEDULED_AGENT = "previous_scheduled_agent"
CONTRACT_FUNDS = "contract_funds"
CONTRACT_INITIALIZED = "contract_initialized"
TIME = "time"

# env actions
INITIALIZE_CONTRACT = "initialize_contract"
DELAY = "delay"

# evaluations
CONTRACT_IS_INITIALIZED = "contract_is_initialized"

# misc
TIME_PROGRESSES_FOREVER = "time_progresses_forever"
TIME_REACHES_MAXIMUM = "time_reaches_maximum"

PARTICIPANT_PREFIX = "part_"

class TermNaming:
    @staticmethod
    def secret_name_with_prefix(secret_name: str) -> str:
        return f"secret_{secret_name}"

    @staticmethod
    def participant_name_with_prefix(participant_name: str) -> str:
        return f"{PARTICIPANT_PREFIX}{participant_name}"

    @staticmethod
    def deposit_with_prefix(deposit_name: str) -> str:
        return f"deposit_{deposit_name}"

    @staticmethod
    def secret_name_with_prefix_public(secret_name: str) -> str:
        return f"public_{TermNaming.secret_name_with_prefix(secret_name)}"

    @staticmethod
    def secret_name_with_prefix_private(secret_name: str) -> str:
        return f"private_{TermNaming.secret_name_with_prefix(secret_name)}"

    @staticmethod
    def deposit_spent_var(deposit_name: str) -> str:
        return f"spent_{deposit_name}"

    @staticmethod
    def deposit_spent_var_from_id(deposit_id: str) -> str:
        return f"spent_{TermNaming.deposit_with_prefix(deposit_id)}"

    @staticmethod
    def agent_name_from_participant_name(participant_name: str) -> str:
        return f"Agent_{participant_name}"

    @staticmethod
    def participant_id_from_agent_name(agent_name: str) -> str:
        assert_(agent_name.startswith("Agent_"))
        return re.sub("^Agent_", "", agent_name)

    @staticmethod
    def scheduling_action_from_participant_id(participant_id: str) -> str:
        return f"schedule_{TermNaming.participant_name_with_prefix(participant_id)}"

    @staticmethod
    def scheduling_prop_from_participant_id(participant_id: str) -> str:
        return f"{TermNaming.participant_name_with_prefix(participant_id)}_is_scheduled"

    @staticmethod
    def secret_is_committed_prop(secret_id: str) -> str:
        return f"{TermNaming.secret_name_with_prefix(secret_id)}_is_committed"

    @staticmethod
    def private_secret_is_x_prop(secret_id: str, value: PrivateSecretValues) -> str:
        return f"{TermNaming.secret_name_with_prefix_private(secret_id)}_is_{value.value}"

    @staticmethod
    def public_secret_is_x_prop(secret_id: str, value: PublicSecretValues) -> str:
        return f"{TermNaming.secret_name_with_prefix_public(secret_id)}_is_{value.value}"

    @staticmethod
    def action_with_prefix(action_id: str) -> str:
        return f"action_{action_id}"

    @staticmethod
    def valid_commitment_action(secret_id: str) -> str:
        return f"commit_valid_{TermNaming.secret_name_with_prefix(secret_id)}"

    @staticmethod
    def invalid_commitment_action(secret_id: str) -> str:
        return f"commit_invalid_{TermNaming.secret_name_with_prefix(secret_id)}"

    @staticmethod
    def reveal_action(secret_id: str) -> str:
        return f"reveal_{TermNaming.secret_name_with_prefix(secret_id)}"

    @staticmethod
    def participant_total_deposits(participant_id: str) -> str:
        return (
            f"{TermNaming.participant_name_with_prefix(participant_id)}_total_deposits"
        )

    @staticmethod
    def exec_expression_node_id(full_node_id: str) -> str:
        return f"{EXEC_PREFIX}{full_node_id}"

    @staticmethod
    def expression_node_id_status(full_node_id: str) -> str:
        return f"status_{full_node_id}"

    @staticmethod
    def authorized_by_variable(full_node_id: str, participant_id: str) -> str:
        part_name = TermNaming.participant_name_with_prefix(participant_id)
        return f"{full_node_id}_authorized_by_{part_name}"

    @staticmethod
    def authorize_action(full_node_id: str) -> str:
        return f"authorize_{full_node_id}"

    @staticmethod
    def agent_done_varname(participant_id: str) -> str:
        part_name = TermNaming.participant_name_with_prefix(participant_id)
        return f"{part_name}_is_done"

    @staticmethod
    def agent_done_prop(participant_id: str) -> str:
        part_name = TermNaming.participant_name_with_prefix(participant_id)
        return f"{part_name}_is_done"

    @staticmethod
    def funds_of_node(full_node_id: str) -> str:
        return f"{full_node_id}_funds"

    @staticmethod
    def timeout_has_expired(timeout: int):
        return f"timeout_{timeout}_has_expired"
