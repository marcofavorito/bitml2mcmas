import logging
import subprocess
import tempfile
import time
from collections.abc import Mapping, Sequence
from copy import copy
from pathlib import Path
from typing import Any

from bitml2mcmas.mcmas.custom_types import ENVIRONMENT

# this timeout is required to avoid reading too early after submitting a command to the MCMAS process
_TINY_TIMEOUT = 0.00001
_TIMEOUT = 5
_END_PREAMBLE_SECTION = "Encoding BDD parameters..."
_START_INITIAL_STATE_SECTION = "--------- Initial state ---------"
_START_CURRENT_STATE_SECTION = "--------- Current state ---------"
_END_SECTION = "----------------------------"

_START_ENABLED_ACTIONS_SECTION = "Enabled actions:"
_END_ENABLED_ACTIONS_SECTION = (
    "Please choose one, or type 0 to backtrack or -1 to quit:"
)


class _InteractiveSubprocess:
    def __init__(self, cmd: Sequence[str]) -> None:
        self.__cmd = tuple(cmd)

        self.__is_initialized: bool = False
        self.__subprocess = None
        self.__tmp_stdout_file_write = None
        self.__tmp_stdout_file_read = None

    @property
    def subprocess(self):
        return self.__subprocess

    @property
    def cmd(self) -> Sequence[str]:
        return list(self.__cmd)

    @property
    def is_initialized(self) -> bool:
        return self.__is_initialized

    def init(self) -> None:
        # delete=False due to bug on Windows: https://github.com/bravoserver/bravo/issues/111
        self.__tmp_stdout_file_write = tempfile.NamedTemporaryFile(
            mode="wb", delete=False
        )
        self.__tmp_stdout_file_read = open(self.__tmp_stdout_file_write.name)
        self.__subprocess = subprocess.Popen(
            self.cmd,
            stdin=subprocess.PIPE,
            stdout=self.__tmp_stdout_file_write,
            stderr=self.__tmp_stdout_file_write,
        )
        self.__is_initialized = True

    def writeline(self, input_str: str):
        assert self.is_initialized
        self.__subprocess.stdin.write(input_str.encode("ascii") + b"\n")
        self.__subprocess.stdin.flush()

    def readline(self) -> str:
        assert self.is_initialized
        return self.__tmp_stdout_file_read.readline()

    def close(self) -> None:
        self.writeline("-1")

        self.__subprocess.wait(timeout=_TIMEOUT)
        self.__tmp_stdout_file_read.close()
        self.__tmp_stdout_file_write.close()

        returncode = self.__subprocess.returncode
        Path(self.__tmp_stdout_file_write.name).unlink(missing_ok=True)

        self.__subprocess = None
        self.__tmp_stdout_file_write = None
        self.__tmp_stdout_file_read = None

        self.__is_initialized = False

        if returncode != 0:
            raise ValueError("Command failed")


class SimulationState:
    def __init__(
        self,
        env_state: dict[str, Any],
        agent_states_by_agent: dict[str, dict[str, str]],
    ) -> None:
        self._env_state = env_state
        self._agent_states_by_agent = agent_states_by_agent

        assert len(agent_states_by_agent) > 0

    @property
    def env_state(self) -> Mapping[str, str]:
        return self._env_state

    @property
    def agent_states_by_agent(self) -> Mapping[str, Mapping[str, str]]:
        return self._agent_states_by_agent

    def _copy_agent_states_by_agent(self) -> dict[str, dict[str, str]]:
        return {k: copy(v) for k, v in self._agent_states_by_agent.items()}

    def update_env_state(self, attr: str, value: str) -> "SimulationState":
        new_env_state = copy(self._env_state)
        assert attr in new_env_state, f"attribute {attr} not known for {ENVIRONMENT}"
        new_env_state[attr] = value
        return SimulationState(new_env_state, self._copy_agent_states_by_agent())

    def update_agent_state(
        self, agent_id: str, attr: str, value: str
    ) -> "SimulationState":
        new_agent_states = self._copy_agent_states_by_agent()
        assert agent_id in new_agent_states, f"agent {agent_id} not known"
        assert (
            attr in new_agent_states[agent_id]
        ), f"attribute {attr} not known for agent {agent_id}"
        new_agent_states[agent_id][attr] = value
        return SimulationState(copy(self._env_state), new_agent_states)

    def to_string(self) -> str:
        result = ""
        result += "Env state:"
        for k, v in sorted(self._env_state.items()):
            result += f"\n    {k}: {v}"

        result += "\n"

        for agent in sorted(self._agent_states_by_agent.keys()):
            state_dict = self._agent_states_by_agent[agent]
            result += f"Agent {agent} states:\n"
            for k, v in sorted(state_dict.items()):
                result += f"    {k}: {v}\n"

        return result

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, SimulationState)
            and self._env_state == other._env_state
            and self._agent_states_by_agent == other._agent_states_by_agent
        )

    def __str__(self) -> str:
        return self.to_string()

    def __repr__(self):
        return str(self)


class EnabledActions:
    def __init__(self, actions: list[dict[str, str]]) -> None:
        self._actions = actions

        self.__canonical_actions = self._validate_actions(actions)

    @property
    def action_seq(self) -> tuple[dict[str, str], ...]:
        return tuple(self._actions)

    @property
    def action_set(self) -> set[tuple[tuple[str, str], ...]]:
        return set(self.__canonical_actions)

    def _validate_actions(
        self, actions: list[dict[str, str]]
    ) -> tuple[tuple[tuple[str, str], ...], ...]:
        if len(actions) == 0:
            return tuple()

        unique = set()

        agents = set(actions[0].keys())
        for action in self._actions:
            assert set(action.keys()) == agents
            canonic = self._canonicalize_action(action)
            assert canonic not in unique
            unique.add(canonic)

        return tuple(sorted(unique))

    def _canonicalize_action(
        self, action: dict[str, str]
    ) -> tuple[tuple[str, str], ...]:
        return tuple(sorted(action.items()))

    def __len__(self):
        return len(self._actions)

    def __iter__(self):
        return iter(self._actions)

    def __getitem__(self, item):
        return self._actions[item]

    def __contains__(self, item):
        return item in self._actions

    def __eq__(self, other):
        return isinstance(other, EnabledActions) and self._actions == other._actions

    def index(self, obj: dict[str, str]) -> int:
        return self._actions.index(obj) + 1

    def select_where(self, **constraints: str) -> "EnabledActions":
        actions = []
        for action in self._actions:
            if all(action[k] == constraints[k] for k in constraints.keys()):
                actions.append(action)

        return EnabledActions(actions)


class McmasSimulator:
    def __init__(self, mcmas_bin_path: Path, mcmas_input_file: Path) -> None:
        self.__mcmas_bin_path = mcmas_bin_path.resolve(strict=True)
        self.__mcmas_input_file = mcmas_input_file.resolve(strict=True)
        self.__simulation_state = None
        self.__enabled_actions = None

        self.__initialized: bool = False
        self.__subprocess: _InteractiveSubprocess = _InteractiveSubprocess(
            self._get_cmdline()
        )
        self._history_length = 0
        self._action_history = []

    @property
    def mcmas_bin_path(self) -> Path:
        return self.__mcmas_bin_path

    @property
    def mcmas_input_file(self) -> Path:
        return self.__mcmas_input_file

    @property
    def initialized(self) -> bool:
        return self.__subprocess.is_initialized

    @property
    def simulation_state(self) -> SimulationState:
        if not self.initialized:
            raise ValueError("simulator is not initialized")
        return self.__simulation_state

    @property
    def enabled_actions(self) -> EnabledActions:
        if not self.initialized:
            raise ValueError("simulator is not initialized")
        return self.__enabled_actions

    @property
    def history_length(self) -> int:
        return len(self._action_history) + 1

    @property
    def subprocess(self) -> _InteractiveSubprocess:
        return self.__subprocess

    def _get_cmdline(self) -> list[str]:
        return [str(self.mcmas_bin_path), "-s", str(self.mcmas_input_file)]

    def _instantiate_subprocess(self):
        self.__subprocess.init()

    def start(self) -> None:
        if self.initialized:
            raise ValueError("Simulator already initialized")

        self.__subprocess.init()
        self.__initialized = True
        self._action_history = []
        self._wait_until_started()
        self._skip_preamble()
        time.sleep(_TINY_TIMEOUT)
        self.__simulation_state = self._read_initial_state_section()
        self.__enabled_actions = self._read_enabled_actions_section()

    def stop(self) -> None:
        self.__subprocess.close()
        self.__initialized = False
        self._action_history = []

    def take_action(self, i: int) -> None:
        assert 1 <= i <= len(self.enabled_actions)
        action = self.enabled_actions.action_seq[i - 1]
        self.subprocess.writeline(f"{i}")
        time.sleep(_TINY_TIMEOUT)

        self.__simulation_state = self._read_current_state_section()
        self.__enabled_actions = self._read_enabled_actions_section()
        self._action_history.append(action)

    def backtrack(self) -> None:
        """Go back to one state.

        Since we do not record the full history of states, we need to parse the state again.
        However, when backtracking, the MCMAS CLI tool does not reprint the previous state.
        To force the reprinting of the state, we backtrack twice, and repeat the second-to-last
        action wrt the current. However, we must recompute the index of the action since the generation of the
        available actions is not deterministic. In case we are only at the second step of the execution,
        the problem does not occur since the initial state is always reprinted by the tool.
        """

        if self.history_length == 2:
            # backtrack once, in this case it is enough
            self.subprocess.writeline("0")
            self.__simulation_state = self._read_initial_state_section()
            self.__enabled_actions = self._read_enabled_actions_section()
            self._action_history = []
        else:  # history length > 2
            # backtrack twice
            self.subprocess.writeline("0")
            self._read_enabled_actions_section()
            self.subprocess.writeline("0")
            self.__enabled_actions = self._read_enabled_actions_section()
            second_to_last_action = self._action_history[-2]
            second_to_last_action_index = self.enabled_actions.index(
                second_to_last_action
            )
            self.take_action(second_to_last_action_index)
            self._action_history.pop()

    def _read_until(self, line: str) -> list[str]:
        output = []
        line_read = False
        while not line_read:
            newline = self.subprocess.readline()
            line_read = newline.startswith(line)

            if newline != "":
                output.append(newline)

            if newline == "" and self.subprocess.subprocess.poll() is not None:
                break

            time.sleep(_TINY_TIMEOUT)

        return output

    def _wait_until_started(self) -> None:
        while self.subprocess.readline() == "":
            time.sleep(_TINY_TIMEOUT)

    def _skip_preamble(self) -> None:
        self._read_until(_END_PREAMBLE_SECTION)

    def _read_initial_state_section(self) -> SimulationState:
        # consume output buffer until the section start is read
        _ = self._read_until(_START_INITIAL_STATE_SECTION)
        section_content_lines = self._read_until(_END_SECTION)
        # remove end line
        section_content_lines = section_content_lines[:-1]

        simulation_state = self._parse_simulation_states(section_content_lines)
        return simulation_state

    def _read_current_state_section(self) -> SimulationState:
        # consume output buffer until the section start is read
        _ = self._read_until(_START_CURRENT_STATE_SECTION)
        section_content_lines = self._read_until(_END_SECTION)
        # remove end line
        section_content_lines = section_content_lines[:-1]

        simulation_state = self._parse_simulation_states(section_content_lines)
        return simulation_state

    def _read_enabled_actions_section(self) -> EnabledActions:
        # consume output buffer until the section start is read
        _ = self._read_until(_START_ENABLED_ACTIONS_SECTION)
        section_content_lines = self._read_until(_END_ENABLED_ACTIONS_SECTION)
        # remove end line
        section_content_lines = section_content_lines[:-1]

        enabled_actions = self._parse_enabled_actions(section_content_lines)
        return enabled_actions

    def _parse_simulation_states(
        self, section_content_lines: list[str]
    ) -> SimulationState:
        agent_names = []
        agent_states = []
        for line in section_content_lines:
            line = line.strip()
            if line.startswith("Agent "):
                current_agent_name = line.split()[1]
                agent_names.append(current_agent_name)
                agent_states.append({})
            else:
                varname, value = line.split(" = ")
                agent_states[-1][varname] = value

        assert len(agent_names) == len(agent_states)
        assert agent_names[0] == ENVIRONMENT

        env_state = agent_states[0]
        agent_states_by_agent = dict(
            zip(agent_names[1:], agent_states[1:], strict=False)
        )
        return SimulationState(env_state, agent_states_by_agent)

    def _parse_enabled_actions(
        self, section_content_lines: list[str]
    ) -> EnabledActions:
        all_actions = []
        for line in section_content_lines:
            agent_actions = {}

            actions_raw = line.split(";")
            # handle first split separately, since it also contains the action index
            tokens = actions_raw[0].split(":")
            _action_id = int(tokens[0])
            agent_name, action = tokens[1].strip(), tokens[2].strip()

            assert agent_name not in agent_actions
            agent_actions[agent_name] = action

            # handle other actions
            for action_raw in actions_raw[1:]:
                tokens = action_raw.split(":")
                agent_name, action = tokens[0].strip(), tokens[1].strip()
                assert agent_name not in agent_actions
                agent_actions[agent_name] = action

            all_actions.append(agent_actions)

        return EnabledActions(all_actions)


def str_to_bool(value: str) -> bool:
    if value.lower() == "false":
        return False
    if value.lower() == "true":
        return True
    raise ValueError(f"input {value!r} not valid")
