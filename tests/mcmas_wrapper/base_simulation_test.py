import logging
import tempfile
from collections.abc import Collection, Sequence
from pathlib import Path

import pytest

from bitml2mcmas.bitml.ast import BitMLParticipant
from bitml2mcmas.bitml.parser.parser import BitMLParser
from bitml2mcmas.compiler._private.terms import (
    DELAY,
    INITIALIZE_CONTRACT,
    LAST_ACTION,
    BitMLExprStatus,
    TermNaming, NOP, PARTICIPANT_PREFIX,
)
from bitml2mcmas.compiler.core import Compiler
from bitml2mcmas.mcmas.custom_types import ENVIRONMENT
from bitml2mcmas.mcmas.formula import AFFormula, AtomicFormula
from bitml2mcmas.mcmas.to_string import interpreted_system_to_string
from tests.helpers import TEST_DIRECTORY
from tests.mcmas_wrapper.shared import (
    ACTION_DELAY,
    FALSE_STR,
    TIME,
    TRUE_STR,
    _add_action_prefix,
)
from tests.mcmas_wrapper.simulator import (
    EnabledActions,
    McmasSimulator,
    SimulationState,
)

_TEST_TIMEOUT = 5


@pytest.mark.timeout(_TEST_TIMEOUT)
class BaseSimulationTest:
    PATH_TO_MCMAS_BIN: Path = TEST_DIRECTORY / "bin" / "mcmas"
    PATH_TO_CONTRACT_FILE: Path

    tmp_file_path: Path
    simulator: McmasSimulator

    def setup_method(self) -> None:
        contract = BitMLParser()(self.PATH_TO_CONTRACT_FILE.read_text())
        formulae = self._add_default_formulae(contract.participants)
        compiler = Compiler(contract, formulae)
        system = compiler.compile()
        system_str = interpreted_system_to_string(system)

        self.tmp_file_path = Path(tempfile.mktemp(suffix=".ispl"))
        self.tmp_file_path.write_text(system_str)
        logging.info(system_str)

        self.simulator = McmasSimulator(self.PATH_TO_MCMAS_BIN, self.tmp_file_path)
        self.simulator.start()

    def teardown_method(self) -> None:
        self.simulator.stop()
        self.tmp_file_path.unlink(missing_ok=True)

    @property
    def actual_current_state(self) -> SimulationState:
        return self.simulator.simulation_state

    @property
    def enabled_actions(self) -> EnabledActions:
        return self.simulator.enabled_actions

    @property
    def agents(self) -> set[str]:
        return set(self.actual_current_state.agent_states_by_agent.keys())

    @property
    def participant_ids(self) -> set[str]:
        result = set()
        for agent_name in self.actual_current_state.agent_states_by_agent.keys():
            participant_id = TermNaming.participant_id_from_agent_name(agent_name)
            result.add(participant_id)
        return result

    @property
    def participant_agent_pairs(self) -> list[tuple[str, str]]:
        result = []
        for agent_name in self.actual_current_state.agent_states_by_agent.keys():
            participant_id = TermNaming.participant_id_from_agent_name(agent_name)
            result.append((participant_id, agent_name))
        return result

    def assert_action_enabled(self, action) -> None:
        assert action in self.enabled_actions

    def assert_some_action_enabled(self, **constraints: str) -> None:
        assert len(self.enabled_actions.select_where(**constraints)) > 0

    def assert_no_action_enabled(self, **constraints: str) -> None:
        assert len(self.enabled_actions.select_where(**constraints)) == 0

    def assert_action_enabled_for_participants(
        self, action: str, agents: set[str] | None = None
    ) -> None:
        if agents is None:
            participants_to_be_checked = self.agents
        else:
            participants_to_be_checked = set(agents)

        for enabled_action_dict in self.enabled_actions.action_seq:
            env_action = enabled_action_dict[ENVIRONMENT]
            scheduled_agent = self.get_scheduled_agent_from_env_action(env_action)
            if scheduled_agent is not None and scheduled_agent in enabled_action_dict:
                agent_action = enabled_action_dict[scheduled_agent]
                if agent_action == action:
                    participants_to_be_checked.discard(scheduled_agent)
                    if len(participants_to_be_checked) == 0:
                        break

        assert (
            len(participants_to_be_checked) == 0
        ), f"action {action} is not enabled for the following participants: {participants_to_be_checked}"

    def assert_any_action_not_enabled_for_participants(
        self, actions: Collection[str]
    ) -> None:
        actions_set = set(actions)
        for enabled_action_dict in self.enabled_actions.action_seq:
            agent_actions = {
                action
                for agent, action in enabled_action_dict.items()
                if agent != ENVIRONMENT
            }
            assert len(agent_actions.intersection(actions_set)) == 0

    def get_action_index(self, action) -> int:
        return self.enabled_actions.index(action)

    def add_action_prefix(self, a: str):
        return TermNaming.action_with_prefix(a)

    def assert_actions_are_equivalent(
        self,
        actions: Sequence[dict[str, str]],
        ignore_fields: Collection[str] = (),
    ) -> None:
        action_index = self.get_action_index(actions[0])
        self.simulator.take_action(action_index)
        expected_next_state = self.actual_current_state
        expected_next_enabled_actions = self.simulator.enabled_actions

        self.simulator.backtrack()
        for action in actions[1:]:
            action_index = self.get_action_index(action)
            self.simulator.take_action(action_index)
            actual_next_state = self.actual_current_state
            actual_next_enabled_action = self.simulator.enabled_actions
            self.simulator.backtrack()

            self.assert_states_are_equal(
                expected_next_state, actual_next_state, ignore_fields=ignore_fields
            )
            assert (
                actual_next_enabled_action.action_set
                == expected_next_enabled_actions.action_set
            )

    def assert_states_are_equal(
        self,
        state_1: SimulationState,
        state_2: SimulationState,
        ignore_fields: Collection[str] = (),
    ) -> None:
        message = f"expected:\n{state_1.to_string()}\nactual:\n{state_2.to_string()}"
        if len(ignore_fields) == 0:
            logging.info(message)
            assert state_1 == state_2, message
            return

        for field in state_1.env_state.keys():
            if field in ignore_fields:
                continue
            assert state_1.env_state[field] == state_2.env_state[field], message

        for agent_id in state_1.agent_states_by_agent:
            agent_state_1 = state_1.agent_states_by_agent[agent_id]
            agent_state_2 = state_2.agent_states_by_agent[agent_id]
            for field in agent_state_1.keys():
                if field in ignore_fields:
                    continue
                assert agent_state_1[field] == agent_state_2[field], message

    def assert_env_attr_equal_to(self, attr_name: str, expected_value: str) -> None:
        actual_value = self.actual_current_state.env_state[attr_name]
        assert (
            actual_value == expected_value
        ), f"assert failed on env attribute {attr_name}:\nexpected: {expected_value}\nactual: {actual_value}"

    def assert_agent_attr_equal_to(
        self, agent_name: str, attr_name: str, expected_value: str
    ) -> None:
        actual_value = self.actual_current_state.agent_states_by_agent[agent_name][
            attr_name
        ]
        assert (
            actual_value == expected_value
        ), f"assert failed on agent {agent_name}'s attribute:\nexpected: {expected_value}\nactual: {actual_value}"

    def assert_node_status_equal_to(
        self, node_id: str, expected_value: BitMLExprStatus
    ):
        status_varname = TermNaming.expression_node_id_status(node_id)
        self.assert_env_attr_equal_to(status_varname, expected_value.value)

    def select_actions_when_scheduled(self, agent_name: str) -> EnabledActions:
        participant_id = TermNaming.participant_id_from_agent_name(agent_name)
        scheduling_action = TermNaming.scheduling_action_from_participant_id(
            participant_id
        )
        return self.enabled_actions.select_where(**{ENVIRONMENT: scheduling_action})

    def take_any_action(self, **constraints: str) -> None:
        actions = self.enabled_actions.select_where(**constraints)
        action_1 = actions[0]
        action_1_index = self.get_action_index(action_1)
        self.simulator.take_action(action_1_index)

    def take_any_participant_action(self, agent_name: str, **constraints: str) -> None:
        actions = self.select_actions_when_scheduled(agent_name).select_where(
            **constraints
        )
        action_1 = actions[0]
        action_1_index = self.get_action_index(action_1)
        self.simulator.take_action(action_1_index)

    def take_participant_action(self, agent_name: str, action: str) -> None:
        other_agents = self.agents - {agent_name}
        actions = self.select_actions_when_scheduled(agent_name).select_where(
            **{agent_name: action},
            **{other_agent: NOP for other_agent in other_agents}
        )
        action_1 = actions[0]
        action_1_index = self.get_action_index(action_1)
        self.simulator.take_action(action_1_index)

    def get_last_scheduled_agent_or_none(self) -> str | None:
        last_action = self.simulator.simulation_state.env_state[LAST_ACTION]
        if last_action.startswith(f"action_schedule_{PARTICIPANT_PREFIX}"):
            participant_id = last_action.replace(f"action_schedule_{PARTICIPANT_PREFIX}", "")
            return TermNaming.agent_name_from_participant_name(participant_id)
        return None

    def get_scheduled_agent_from_env_action(self, env_action: str) -> str | None:
        if env_action.startswith(f"schedule_{PARTICIPANT_PREFIX}"):
            participant_id = env_action.replace(f"schedule_{PARTICIPANT_PREFIX}", "")
            return TermNaming.agent_name_from_participant_name(participant_id)
        return None

    def _check_all_agents_are_not_done(self) -> None:
        for participant_id, agent_name in self.participant_agent_pairs:
            participant_is_done = TermNaming.agent_done_varname(participant_id)
            assert self.actual_current_state.env_state[participant_is_done] == FALSE_STR

    def progress_time(self):
        self._check_all_agents_are_not_done()
        for agent_name in self.agents:
            self.take_participant_action(agent_name, NOP)
        self.take_any_action(**{ENVIRONMENT: DELAY})

    def progress_time_and_check(
        self,
        ignore_fields: Collection[str] = (),
    ) -> None:
        self._check_all_agents_are_not_done()
        current_state = self.actual_current_state
        current_time = self.actual_current_state.env_state[TIME]

        # increase time for each agent
        for participant_id, agent_name in self.participant_agent_pairs:
            participant_is_done = TermNaming.agent_done_varname(participant_id)
            scheduling_action = TermNaming.scheduling_action_from_participant_id(
                participant_id
            )
            self.take_participant_action(agent_name, NOP)
            current_state = (
                current_state.update_env_state(
                    LAST_ACTION, _add_action_prefix(scheduling_action)
                )
                .update_env_state(participant_is_done, TRUE_STR)
            )

            self.assert_states_are_equal(
                current_state, self.actual_current_state, ignore_fields=ignore_fields
            )

        # env takes action delay
        self.take_any_action(**{ENVIRONMENT: DELAY})
        current_state = current_state.update_env_state(
            LAST_ACTION, ACTION_DELAY
        ).update_env_state(TIME, str(int(current_time) + 1))
        for participant_id, agent_name in self.participant_agent_pairs:
            participant_is_done = TermNaming.agent_done_varname(participant_id)
            current_state = (
                current_state.update_env_state(participant_is_done, FALSE_STR)
            )
        self.assert_states_are_equal(
            current_state, self.actual_current_state, ignore_fields=ignore_fields
        )

    def agent_commits_to_secret(
        self, agent_name: str, secret_id: str, is_valid: bool
    ) -> None:
        action = (
            TermNaming.valid_commitment_action(secret_id)
            if is_valid
            else TermNaming.invalid_commitment_action(secret_id)
        )
        self.take_participant_action(agent_name, action)

    def agent_initializes_contract(self, agent_name: str) -> None:
        self.take_participant_action(agent_name, INITIALIZE_CONTRACT)

    def agent_reveals_secret(self, agent_name: str, secret_id: str) -> None:
        action = TermNaming.reveal_action(secret_id)
        self.take_participant_action(agent_name, action)

    def agent_authorizes_contract_node(self, agent_name, node_id: str) -> None:
        action = TermNaming.authorize_action(node_id)
        self.take_participant_action(agent_name, action)

    def agent_executes_contract_node(self, agent_name: str, node_id: str) -> None:
        action = self.get_node_exec_action(node_id)
        self.take_participant_action(agent_name, action)

    def get_node_exec_action(self, node_id: str) -> str:
        return TermNaming.exec_expression_node_id(node_id)

    def _add_default_formulae(self, participants: Sequence[BitMLParticipant]):
        # these formulae are not really needed for the simulation, but a ISPL file requires at least one formula
        # to verify even if it is in interactive mode
        result = []
        for participant in participants:
            formula = AFFormula(
                AtomicFormula(
                    TermNaming.scheduling_prop_from_participant_id(
                        participant.identifier
                    )
                )
            )
            result.append(formula)
        return result
