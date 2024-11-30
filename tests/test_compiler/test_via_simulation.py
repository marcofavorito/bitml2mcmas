import pytest

from bitml2mcmas.compiler._private.terms import (
    CONTRACT_FUNDS,
    CONTRACT_INITIALIZED,
    INITIALIZE_CONTRACT,
    LAST_ACTION,
    NOP,
    BitMLExprStatus,
    PrivateSecretValues,
    PublicSecretValues,
    TermNaming, UNSET_ACTION,
)
from tests.helpers import EXAMPLES_BITML_CONTRACTS_DIR, TESTS_BITML_CONTRACTS_DIR
from tests.mcmas_wrapper.base_simulation_test import (
    BaseSimulationTest,
)
from tests.mcmas_wrapper.shared import (
    ACTION_COMMIT_VALID_SECRET_A1,
    ACTION_COMMIT_VALID_SECRET_B1,
    ACTION_DELAY,
    ACTION_INITIALIZE_CONTRACT,
    ACTION_NOP,
    ACTION_REVEAL_SECRET_A1,
    ACTION_REVEAL_SECRET_B1,
    ACTION_SCHEDULE_PARTICIPANT_A,
    ACTION_SCHEDULE_PARTICIPANT_B,
    AGENT_A,
    AGENT_B,
    FALSE_STR,
    PARTICIPANT_A_IS_DONE,
    PARTICIPANT_A_TOTAL_DEPOSITS,
    PARTICIPANT_B_IS_DONE,
    PARTICIPANT_B_TOTAL_DEPOSITS,
    PRIVATE_SECRET_A1,
    PRIVATE_SECRET_B1,
    PUBLIC_SECRET_A1,
    PUBLIC_SECRET_B1,
    REVEAL_SECRET_A1,
    REVEAL_SECRET_B1,
    SECRET_A1,
    SECRET_B1,
    SPENT_DEPOSIT_TXA1,
    SPENT_DEPOSIT_TXB1,
    TIME,
    TRUE_STR,
)


class TestWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "withdraw.rkt"

    WITHDRAW_NODE_NAME = "node_0_withdraw"

    STATUS_WITHDRAW_NODE = TermNaming.expression_node_id_status(WITHDRAW_NODE_NAME)
    EXEC_WITHDRAW_NODE = TermNaming.exec_expression_node_id(WITHDRAW_NODE_NAME)
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)

    def test_execution(self) -> None:
        initial_state = self.actual_current_state
        current_state = initial_state

        # check initial state
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # contract cannot be initialized anymore
        self.assert_any_action_not_enabled_for_participants({INITIALIZE_CONTRACT})
        self.assert_action_enabled_for_participants(self.EXEC_WITHDRAW_NODE)

        # test final state after withdraw
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_WITHDRAW_NODE})
        current_state = (
            current_state.update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "2")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # just 'nop' for agents, and environment scheduling either A or B
        assert len(self.simulator.enabled_actions) == 2

        self.assert_actions_are_equivalent(self.simulator.enabled_actions.action_seq, ignore_fields={LAST_ACTION})


class TestAuthWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "auth-withdraw.rkt"

    STATUS_WITHDRAW_NODE = "status_node_0_withdraw"
    WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT = (
        "node_0_withdraw_authorized_by_part_A"
    )
    AUTHORIZEWITHDRAW_NODE_NAME = "authorize_node_0_withdraw"
    EXEC_WITHDRAW_NODE = "exec_node_0_withdraw"
    ACTIONAUTHORIZEWITHDRAW_NODE_NAME = TermNaming.action_with_prefix(
        AUTHORIZEWITHDRAW_NODE_NAME
    )
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)

    def test_execution(self) -> None:
        # check initial state
        initial_state = self.actual_current_state
        current_state = initial_state
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT, FALSE_STR
        )
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # authorize withdraw
        self.take_any_participant_action(
            AGENT_A, **{AGENT_A: self.AUTHORIZEWITHDRAW_NODE_NAME}
        )
        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value
            )
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(
                self.WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT, TRUE_STR
            )
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # do withdraw
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_WITHDRAW_NODE})
        current_state = (
            current_state.update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value)
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)


class TestAfterWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "after-withdraw.rkt"

    STATUS_WITHDRAW_NODE = "status_node_0_withdraw"
    EXEC_WITHDRAW_NODE = "exec_node_0_withdraw"
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)

    def test_execution(self) -> None:
        # check initial state
        initial_state = self.actual_current_state
        current_state = initial_state
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(TIME, "0")
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_IS_DONE, "false")
        self.assert_env_attr_equal_to(PARTICIPANT_B_IS_DONE, "false")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # progress time
        self.progress_time_and_check(ignore_fields={self.STATUS_WITHDRAW_NODE})

        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value
        )

        # do withdraw
        current_state = self.actual_current_state
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_WITHDRAW_NODE})
        current_state = (
            current_state.update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value)
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)


class TestAfterAuthWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "after-auth-withdraw.rkt"

    STATUS_WITHDRAW_NODE = "status_node_0_withdraw"
    WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT = (
        "node_0_withdraw_authorized_by_part_A"
    )
    AUTHORIZE_WITHDRAW_NODE_NAME = "authorize_node_0_withdraw"
    EXEC_WITHDRAW_NODE = "exec_node_0_withdraw"
    ACTION_AUTHORIZE_WITHDRAW_NODE_NAME = TermNaming.action_with_prefix(
        AUTHORIZE_WITHDRAW_NODE_NAME
    )
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)

    def test_execution(self):
        # check initial state
        initial_state = self.actual_current_state
        current_state = initial_state
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT, FALSE_STR
        )
        self.assert_env_attr_equal_to(TIME, "0")
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_IS_DONE, "false")
        self.assert_env_attr_equal_to(PARTICIPANT_B_IS_DONE, "false")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # authorize withdraw
        self.take_any_participant_action(
            AGENT_A, **{AGENT_A: self.AUTHORIZE_WITHDRAW_NODE_NAME}
        )
        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(
                self.WITHDRAW_NODE_NAME_AUTHORIZED_BY_PARTICIPANT, TRUE_STR
            )
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # progress time
        self.progress_time_and_check(ignore_fields={self.STATUS_WITHDRAW_NODE})

        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value
        )

        # do withdraw
        current_state = self.actual_current_state
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_WITHDRAW_NODE})
        current_state = (
            current_state.update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value)
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)


class TestRevealWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "reveal-withdraw.rkt"

    WITHDRAW_NODE_NAME = "node_0_withdraw"
    REVEAL_NODE_NAME = "node_1_reveal"

    STATUS_WITHDRAW_NODE = TermNaming.expression_node_id_status(WITHDRAW_NODE_NAME)
    STATUS_REVEAL_NODE = TermNaming.expression_node_id_status(REVEAL_NODE_NAME)
    EXEC_WITHDRAW_NODE = TermNaming.exec_expression_node_id(WITHDRAW_NODE_NAME)
    EXEC_REVEAL_NODE = TermNaming.exec_expression_node_id(REVEAL_NODE_NAME)
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)
    ACTION_EXEC_NODE_1_REVEAL = TermNaming.action_with_prefix(EXEC_REVEAL_NODE)

    def test_execution(self):
        # check initial state
        initial_state = self.actual_current_state
        current_state = initial_state
        assert int(current_state.env_state[CONTRACT_FUNDS]) == 2
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)
        assert (
            current_state.env_state[self.STATUS_WITHDRAW_NODE]
            == BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(
            PUBLIC_SECRET_A1, PublicSecretValues.NOT_COMMITTED.value
        )
        self.assert_env_attr_equal_to(
            PUBLIC_SECRET_B1, PublicSecretValues.NOT_COMMITTED.value
        )
        self.assert_agent_attr_equal_to(
            AGENT_A, PRIVATE_SECRET_A1, PrivateSecretValues.NOT_COMMITTED.value
        )
        self.assert_agent_attr_equal_to(
            AGENT_B, PRIVATE_SECRET_B1, PrivateSecretValues.NOT_COMMITTED.value
        )

        self.assert_any_action_not_enabled_for_participants({INITIALIZE_CONTRACT})

        # agent A commits to valid secret
        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PUBLIC_SECRET_A1, PublicSecretValues.COMMITTED.value)
            .update_agent_state(
                AGENT_A, PRIVATE_SECRET_A1, PrivateSecretValues.VALID.value
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)
        # secret can be revealed even before contract initialization
        self.assert_action_enabled_for_participants(REVEAL_SECRET_A1, {AGENT_A})

        # agent B commits to valid secret
        self.agent_commits_to_secret(AGENT_B, SECRET_B1, True)
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_B)
            .update_env_state(PUBLIC_SECRET_B1, PublicSecretValues.COMMITTED.value)
            .update_agent_state(
                AGENT_B, PRIVATE_SECRET_B1, PrivateSecretValues.VALID.value
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)
        # secret can be revealed even before contract initialization
        self.assert_action_enabled_for_participants(REVEAL_SECRET_B1, {AGENT_B})

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # reveal secret a
        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PUBLIC_SECRET_A1, PublicSecretValues.VALID.value)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # reveal secret b
        self.agent_reveals_secret(AGENT_B, SECRET_B1)
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_B)
            .update_env_state(PUBLIC_SECRET_B1, PublicSecretValues.VALID.value)
            .update_env_state(self.STATUS_REVEAL_NODE, BitMLExprStatus.ENABLED.value)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # append transaction
        self.assert_action_enabled_for_participants(
            self.EXEC_REVEAL_NODE, {AGENT_A, AGENT_B}
        )
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_REVEAL_NODE})
        current_state = (
            current_state.update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(self.STATUS_REVEAL_NODE, BitMLExprStatus.EXECUTED.value)
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # do withdraw
        self.assert_action_enabled_for_participants(
            self.EXEC_WITHDRAW_NODE, {AGENT_A, AGENT_B}
        )
        self.take_any_participant_action(AGENT_A, **{AGENT_A: self.EXEC_WITHDRAW_NODE})
        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "2")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

    @pytest.mark.parametrize("a1,b1", [(False, False), (True, False), (False, True)])
    def test_commitment_to_invalid_secrets(self, a1, b1) -> None:
        self.agent_commits_to_secret(AGENT_A, SECRET_A1, a1)
        self.agent_commits_to_secret(AGENT_B, SECRET_B1, b1)
        self.agent_initializes_contract(AGENT_A)

        if a1:
            self.agent_reveals_secret(AGENT_A, SECRET_A1)
        else:
            self.assert_no_action_enabled(**{AGENT_A: REVEAL_SECRET_A1})

        if b1:
            self.agent_reveals_secret(AGENT_B, SECRET_B1)
        else:
            self.assert_no_action_enabled(**{AGENT_B: REVEAL_SECRET_B1})

        self.assert_any_action_not_enabled_for_participants({self.EXEC_WITHDRAW_NODE})


class TestAuthRevealAfterWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "auth-reveal-after-withdraw.rkt"

    WITHDRAW_NODE_NAME = "node_0_withdraw"
    REVEAL_NODE_NAME = "node_1_reveal"
    EXEC_WITHDRAW_NODE = TermNaming.exec_expression_node_id(WITHDRAW_NODE_NAME)
    EXEC_REVEAL_NODE = TermNaming.exec_expression_node_id(REVEAL_NODE_NAME)

    def test_execution(self) -> None:
        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        self.agent_initializes_contract(AGENT_A)
        self.progress_time()
        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_executes_contract_node(AGENT_A, self.REVEAL_NODE_NAME)
        self.agent_authorizes_contract_node(AGENT_B, self.WITHDRAW_NODE_NAME)
        self.progress_time()
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_NODE_NAME)


class TestPutWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "put-withdraw.rkt"

    WITHDRAW_NODE_NAME = "node_0_withdraw"
    PUT_NODE_NAME = "node_1_put"

    STATUS_WITHDRAW_NODE = TermNaming.expression_node_id_status(WITHDRAW_NODE_NAME)
    EXEC_WITHDRAW_NODE = TermNaming.exec_expression_node_id(WITHDRAW_NODE_NAME)
    ACTION_EXEC_WITHDRAW_NODE = TermNaming.action_with_prefix(EXEC_WITHDRAW_NODE)

    STATUS_PUT_NODE = TermNaming.expression_node_id_status(PUT_NODE_NAME)
    EXEC_PUT_NODE = TermNaming.exec_expression_node_id(PUT_NODE_NAME)
    ACTION_EXEC_PUT_NODE = TermNaming.action_with_prefix(EXEC_PUT_NODE)

    def test_execution(self) -> None:
        # check initial state
        initial_state = self.actual_current_state
        current_state = initial_state
        assert int(current_state.env_state[CONTRACT_FUNDS]) == 2
        self.assert_env_attr_equal_to(CONTRACT_INITIALIZED, FALSE_STR)

        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_PUT_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(LAST_ACTION, UNSET_ACTION)
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "1")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "1")
        self.assert_env_attr_equal_to(SPENT_DEPOSIT_TXA1, FALSE_STR)
        self.assert_env_attr_equal_to(SPENT_DEPOSIT_TXB1, FALSE_STR)

        # initialize contract
        self.agent_initializes_contract(AGENT_A)
        current_state = (
            current_state.update_env_state(
                self.STATUS_PUT_NODE, BitMLExprStatus.ENABLED.value
            )
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # execute put
        self.assert_action_enabled_for_participants(self.EXEC_PUT_NODE)
        self.agent_executes_contract_node(AGENT_A, self.PUT_NODE_NAME)
        current_state = (
            current_state.update_env_state(
                self.STATUS_PUT_NODE, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(self.STATUS_WITHDRAW_NODE, BitMLExprStatus.ENABLED.value)
            .update_env_state(CONTRACT_FUNDS, "4")
            .update_env_state(SPENT_DEPOSIT_TXA1, TRUE_STR)
            .update_env_state(SPENT_DEPOSIT_TXB1, TRUE_STR)
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        # execute withdraw
        self.assert_action_enabled_for_participants(self.EXEC_WITHDRAW_NODE)
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_NODE_NAME)
        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "4")
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)


class TestPutRevealWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "put-reveal-withdraw.rkt"

    WITHDRAW_NODE_NAME = "node_0_withdraw"
    PUTREVEAL_NODE_NAME = "node_1_putreveal"
    EXEC_WITHDRAW_NODE = TermNaming.exec_expression_node_id(WITHDRAW_NODE_NAME)
    EXEC_PUT_REVEAL_NODE = TermNaming.exec_expression_node_id(PUTREVEAL_NODE_NAME)
    STATUS_WITHDRAW_NODE = TermNaming.expression_node_id_status(WITHDRAW_NODE_NAME)
    STATUS_PUT_REVEAL_NODE = TermNaming.expression_node_id_status(PUTREVEAL_NODE_NAME)

    def test_execution(self) -> None:
        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        self.agent_commits_to_secret(AGENT_B, SECRET_B1, True)
        self.agent_initializes_contract(AGENT_A)
        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_reveals_secret(AGENT_B, SECRET_B1)
        self.agent_executes_contract_node(AGENT_A, self.PUTREVEAL_NODE_NAME)
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_NODE_NAME)

        self.assert_env_attr_equal_to(
            self.STATUS_PUT_REVEAL_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "4")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")


class TestSplitWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "split-withdraw.rkt"

    WITHDRAW_A_NODE_NAME = "node_0_withdraw"
    WITHDRAW_B_NODE_NAME = "node_1_withdraw"
    SPLIT_NODE_NAME = "node_2_split"
    EXEC_WITHDRAW_A_NODE = TermNaming.exec_expression_node_id(WITHDRAW_A_NODE_NAME)
    EXEC_WITHDRAW_B_NODE = TermNaming.exec_expression_node_id(WITHDRAW_B_NODE_NAME)
    EXEC_SPLIT_NODE = TermNaming.exec_expression_node_id(SPLIT_NODE_NAME)
    STATUS_WITHDRAW_A_NODE = TermNaming.expression_node_id_status(WITHDRAW_A_NODE_NAME)
    STATUS_WITHDRAW_B_NODE = TermNaming.expression_node_id_status(WITHDRAW_B_NODE_NAME)
    STATUS_SPLIT_NODE = TermNaming.expression_node_id_status(SPLIT_NODE_NAME)

    def test_execution(self) -> None:
        self.assert_env_attr_equal_to(
            self.STATUS_SPLIT_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

        # contract initialization
        self.agent_initializes_contract(AGENT_A)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(
            self.STATUS_SPLIT_NODE, BitMLExprStatus.ENABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

        # split executed
        self.agent_executes_contract_node(AGENT_A, self.SPLIT_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(
            self.STATUS_SPLIT_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.ENABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.ENABLED.value
        )

        # do withdraw A
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "1")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "1")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.ENABLED.value
        )

        # do withdraw B
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_B_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "1")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "1")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.EXECUTED.value
        )


class TestChoiceWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "choice-withdraw.rkt"

    WITHDRAW_A_NODE_NAME = "node_0_withdraw"
    WITHDRAW_B_NODE_NAME = "node_1_withdraw"
    EXEC_WITHDRAW_A_NODE = TermNaming.exec_expression_node_id(WITHDRAW_A_NODE_NAME)
    EXEC_WITHDRAW_B_NODE = TermNaming.exec_expression_node_id(WITHDRAW_B_NODE_NAME)
    STATUS_WITHDRAW_A_NODE = TermNaming.expression_node_id_status(WITHDRAW_A_NODE_NAME)
    STATUS_WITHDRAW_B_NODE = TermNaming.expression_node_id_status(WITHDRAW_B_NODE_NAME)

    def setup_method(self):
        """Initialize the test for both branches."""
        super().setup_method()
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

        # contract initialization
        self.agent_initializes_contract(AGENT_A)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "2")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.ENABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.ENABLED.value
        )

        self.assert_action_enabled_for_participants(
            self.EXEC_WITHDRAW_A_NODE, {AGENT_A, AGENT_B}
        )
        self.assert_action_enabled_for_participants(
            self.EXEC_WITHDRAW_B_NODE, {AGENT_A, AGENT_B}
        )

    def test_branch_withdraw_A(self):
        # do withdraw A
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "2")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

    def test_branch_withdraw_B(self):
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_B_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.EXECUTED.value
        )


class TestRevealChoiceWithdraw(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "reveal-choice-withdraw.rkt"

    WITHDRAW_A_NODE_NAME = "node_0_withdraw"
    WITHDRAW_B_NODE_NAME = "node_1_withdraw"
    REVEAL_NODE_NAME = "node_3_reveal"
    EXEC_WITHDRAW_A_NODE = TermNaming.exec_expression_node_id(WITHDRAW_A_NODE_NAME)
    EXEC_WITHDRAW_B_NODE = TermNaming.exec_expression_node_id(WITHDRAW_B_NODE_NAME)
    EXEC_REVEAL_NODE_NODE = TermNaming.exec_expression_node_id(REVEAL_NODE_NAME)
    STATUS_WITHDRAW_A_NODE = TermNaming.expression_node_id_status(WITHDRAW_A_NODE_NAME)
    STATUS_WITHDRAW_B_NODE = TermNaming.expression_node_id_status(WITHDRAW_B_NODE_NAME)
    STATUS_REVEAL_NODE = TermNaming.expression_node_id_status(REVEAL_NODE_NAME)

    def setup_method(self) -> None:
        super().setup_method()
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        self.agent_initializes_contract(AGENT_A)
        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_executes_contract_node(AGENT_A, self.REVEAL_NODE_NAME)

        self.assert_action_enabled_for_participants(
            self.EXEC_WITHDRAW_A_NODE, {AGENT_A, AGENT_B}
        )
        self.assert_action_enabled_for_participants(
            self.EXEC_WITHDRAW_B_NODE, {AGENT_A, AGENT_B}
        )

    def test_branch_withdraw_A(self):
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "2")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.EXECUTED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

    def test_branch_withdraw_B(self):
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_B_NODE_NAME)
        self.assert_env_attr_equal_to(CONTRACT_FUNDS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_A_TOTAL_DEPOSITS, "0")
        self.assert_env_attr_equal_to(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.EXECUTED.value
        )


class TestTimedCommitment(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "timed-commitment.rkt"

    WITHDRAW_A_NODE_NAME = "node_0_withdraw"
    WITHDRAW_B_NODE_NAME = "node_2_withdraw"
    REVEAL_NODE_NAME = "node_1_reveal"
    EXEC_WITHDRAW_A_NODE = TermNaming.exec_expression_node_id(WITHDRAW_A_NODE_NAME)
    EXEC_WITHDRAW_B_NODE = TermNaming.exec_expression_node_id(WITHDRAW_B_NODE_NAME)
    EXEC_REVEAL_NODE_NODE = TermNaming.exec_expression_node_id(REVEAL_NODE_NAME)
    STATUS_WITHDRAW_A_NODE = TermNaming.expression_node_id_status(WITHDRAW_A_NODE_NAME)
    STATUS_WITHDRAW_B_NODE = TermNaming.expression_node_id_status(WITHDRAW_B_NODE_NAME)
    STATUS_REVEAL_NODE = TermNaming.expression_node_id_status(REVEAL_NODE_NAME)

    def setup_method(self) -> None:
        super().setup_method()
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_A_NODE, BitMLExprStatus.DISABLED.value
        )
        self.assert_env_attr_equal_to(
            self.STATUS_WITHDRAW_B_NODE, BitMLExprStatus.DISABLED.value
        )

        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        self.agent_initializes_contract(AGENT_A)

        self.assert_action_enabled_for_participants(REVEAL_SECRET_A1, {AGENT_A})
        self.assert_action_enabled_for_participants(NOP, {AGENT_A, AGENT_B})

    def test_branch_withdraw_A(self) -> None:
        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_executes_contract_node(AGENT_A, self.REVEAL_NODE_NAME)
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_NODE_NAME)

        self.assert_action_enabled_for_participants(NOP, {AGENT_A, AGENT_B})

    def test_branch_withdraw_B(self) -> None:
        self.progress_time()
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_B_NODE_NAME)

        self.assert_action_enabled_for_participants(NOP, {AGENT_A, AGENT_B})


class TestMutualTimedCommitment(BaseSimulationTest):
    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "mutual-tc.rkt"

    # withdraw A, after revealing both secrets
    WITHDRAW_A_NODE_NAME = "node_0_withdraw"
    STATUS_WITHDRAW_A_NODE_NAME = TermNaming.expression_node_id_status(
        WITHDRAW_A_NODE_NAME
    )
    EXEC_WITHDRAW_A_NODE_NAME = TermNaming.exec_expression_node_id(WITHDRAW_A_NODE_NAME)
    ACTION_EXEC_WITHDRAW_A_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_WITHDRAW_A_NODE_NAME
    )

    # withdraw A, after revealing both secrets
    WITHDRAW_B_NODE_NAME = "node_1_withdraw"
    STATUS_WITHDRAW_B_NODE_NAME = TermNaming.expression_node_id_status(
        WITHDRAW_B_NODE_NAME
    )
    EXEC_WITHDRAW_B_NODE_NAME = TermNaming.exec_expression_node_id(WITHDRAW_B_NODE_NAME)
    ACTION_EXEC_WITHDRAW_B_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_WITHDRAW_B_NODE_NAME
    )

    # split node
    SPLIT_NODE_NAME = "node_2_split"
    STATUS_SPLIT_NODE_NAME = TermNaming.expression_node_id_status(SPLIT_NODE_NAME)
    EXEC_SPLIT_NODE_NAME = TermNaming.exec_expression_node_id(SPLIT_NODE_NAME)
    ACTION_EXEC_SPLIT_NODE_NAME = TermNaming.action_with_prefix(EXEC_SPLIT_NODE_NAME)

    # reveal b
    REVEAL_B_NODE_NAME = "node_3_reveal"
    STATUS_REVEAL_B_NODE_NAME = TermNaming.expression_node_id_status(REVEAL_B_NODE_NAME)
    EXEC_REVEAL_B_NODE_NAME = TermNaming.exec_expression_node_id(REVEAL_B_NODE_NAME)
    ACTION_EXEC_REVEAL_B_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_REVEAL_B_NODE_NAME
    )

    # withdraw A, after 4
    WITHDRAW_A_AFTER_4_NODE_NAME = "node_4_withdraw"
    STATUS_WITHDRAW_A_AFTER_4_NODE_NAME = TermNaming.expression_node_id_status(
        WITHDRAW_A_AFTER_4_NODE_NAME
    )
    EXEC_WITHDRAW_A_AFTER_4_NODE_NAME = TermNaming.exec_expression_node_id(
        WITHDRAW_A_AFTER_4_NODE_NAME
    )
    ACTION_EXEC_WITHDRAW_A_AFTER_4_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_WITHDRAW_A_AFTER_4_NODE_NAME
    )

    # reveal a
    REVEAL_A_NODE_NAME = "node_6_reveal"
    STATUS_REVEAL_A_NODE_NAME = TermNaming.expression_node_id_status(REVEAL_A_NODE_NAME)
    EXEC_REVEAL_A_NODE_NAME = TermNaming.exec_expression_node_id(REVEAL_A_NODE_NAME)
    ACTION_EXEC_REVEAL_A_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_REVEAL_A_NODE_NAME
    )

    # withdraw B, after 2
    WITHDRAW_B_AFTER_2_NODE_NAME = "node_7_withdraw"
    STATUS_WITHDRAW_B_AFTER_2_NODE_NAME = TermNaming.expression_node_id_status(
        WITHDRAW_B_AFTER_2_NODE_NAME
    )
    EXEC_WITHDRAW_B_AFTER_2_NODE_NAME = TermNaming.exec_expression_node_id(
        WITHDRAW_B_AFTER_2_NODE_NAME
    )
    ACTION_EXEC_WITHDRAW_B_AFTER_2_NODE_NAME = TermNaming.action_with_prefix(
        EXEC_WITHDRAW_B_AFTER_2_NODE_NAME
    )

    def setup_method(self) -> None:
        super().setup_method()

        current_state = self.actual_current_state

        self.agent_commits_to_secret(AGENT_A, SECRET_A1, True)
        self.agent_commits_to_secret(AGENT_B, SECRET_B1, True)
        self.agent_initializes_contract(AGENT_A)

        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(PUBLIC_SECRET_A1, PublicSecretValues.COMMITTED.value)
            .update_env_state(PUBLIC_SECRET_B1, PublicSecretValues.COMMITTED.value)
            .update_agent_state(
                AGENT_A, PRIVATE_SECRET_A1, PrivateSecretValues.VALID.value
            )
            .update_agent_state(
                AGENT_B, PRIVATE_SECRET_B1, PrivateSecretValues.VALID.value
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

    def test_branch_withdraw_b_after_2(self) -> None:
        current_state = self.actual_current_state

        self.progress_time()

        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(LAST_ACTION, ACTION_DELAY)
            .update_env_state(TIME, "1")
            .update_env_state(
                self.STATUS_WITHDRAW_B_AFTER_2_NODE_NAME,
                BitMLExprStatus.ENABLED.value,
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        exec_action = self.get_node_exec_action(self.WITHDRAW_B_AFTER_2_NODE_NAME)
        self.assert_action_enabled_for_participants(exec_action, {AGENT_A, AGENT_B})
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_B_AFTER_2_NODE_NAME)

        current_state = (
            current_state.update_env_state(CONTRACT_INITIALIZED, TRUE_STR)
            .update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "2")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
            .update_env_state(
                self.STATUS_WITHDRAW_A_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_SPLIT_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_REVEAL_B_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_WITHDRAW_A_AFTER_4_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_REVEAL_A_NODE_NAME,
                BitMLExprStatus.DISABLED.value,
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_AFTER_2_NODE_NAME,
                BitMLExprStatus.EXECUTED.value,
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

    def test_branch_reveal_a_withdraw_A_after_4(self) -> None:
        current_state = self.actual_current_state

        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_executes_contract_node(AGENT_A, self.REVEAL_A_NODE_NAME)

        current_state = (
            current_state.update_env_state(
                PUBLIC_SECRET_A1, PublicSecretValues.VALID.value
            )
            .update_env_state(
                self.STATUS_REVEAL_A_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_AFTER_2_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        self.progress_time()
        self.progress_time()

        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_A_AFTER_4_NODE_NAME, BitMLExprStatus.ENABLED.value
            )
            .update_env_state(TIME, "2")
            .update_env_state(LAST_ACTION, ACTION_DELAY)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_AFTER_4_NODE_NAME)

        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_A_AFTER_4_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_SPLIT_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(
                self.STATUS_REVEAL_B_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_A_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "2")
            .update_env_state(TIME, "2")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_A)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)

    def test_split_branch(self) -> None:
        current_state = self.actual_current_state

        self.agent_reveals_secret(AGENT_A, SECRET_A1)
        self.agent_executes_contract_node(AGENT_A, self.REVEAL_A_NODE_NAME)
        self.agent_reveals_secret(AGENT_B, SECRET_B1)
        self.agent_executes_contract_node(AGENT_B, self.REVEAL_B_NODE_NAME)
        self.agent_executes_contract_node(AGENT_A, self.SPLIT_NODE_NAME)
        self.agent_executes_contract_node(AGENT_A, self.WITHDRAW_A_NODE_NAME)
        self.agent_executes_contract_node(AGENT_B, self.WITHDRAW_B_NODE_NAME)

        current_state = (
            current_state.update_env_state(
                self.STATUS_WITHDRAW_A_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_SPLIT_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_REVEAL_A_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_REVEAL_B_NODE_NAME, BitMLExprStatus.EXECUTED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_B_AFTER_2_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(
                self.STATUS_WITHDRAW_A_AFTER_4_NODE_NAME, BitMLExprStatus.DISABLED.value
            )
            .update_env_state(PUBLIC_SECRET_A1, PublicSecretValues.VALID.value)
            .update_env_state(PUBLIC_SECRET_B1, PublicSecretValues.VALID.value)
            .update_env_state(CONTRACT_FUNDS, "0")
            .update_env_state(PARTICIPANT_A_TOTAL_DEPOSITS, "1")
            .update_env_state(PARTICIPANT_B_TOTAL_DEPOSITS, "1")
            .update_env_state(LAST_ACTION, ACTION_SCHEDULE_PARTICIPANT_B)
        )
        self.assert_states_are_equal(current_state, self.actual_current_state)