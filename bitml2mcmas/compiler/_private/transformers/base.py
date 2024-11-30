from abc import ABC, abstractmethod
from collections.abc import Generator

from bitml2mcmas.compiler._private.contract_wrapper import ContractWrapper
from bitml2mcmas.compiler._private.mcmas_builder import (
    AgentBuilder,
    EnvBuilder,
    MCMASBuilder,
)
from bitml2mcmas.compiler._private.mcmas_objects import McmasObjects
from bitml2mcmas.compiler._private.terms import TermNaming


class Transformer(ABC):
    def __init__(self, wrapper: ContractWrapper, builder: MCMASBuilder) -> None:
        self.__wrapper = wrapper
        self.__builder = builder

        self.__obj = McmasObjects(self.wrapper)

    @property
    def wrapper(self) -> ContractWrapper:
        return self.__wrapper

    @property
    def builder(self) -> MCMASBuilder:
        return self.__builder

    @property
    def objects(self) -> McmasObjects:
        return self.__obj

    @property
    def env(self) -> EnvBuilder:
        return self.builder.env

    def get_agent_builders(self) -> Generator[tuple[str, AgentBuilder], None, None]:
        for participant_id in self.wrapper.participant_ids:
            agent_name = TermNaming.agent_name_from_participant_name(participant_id)
            yield participant_id, self.builder.get_agent_builder(agent_name)

    def agent_builder_by_participant_id(self, participant_id: str) -> AgentBuilder:
        agent_name = TermNaming.agent_name_from_participant_name(participant_id)
        return self.builder.get_agent_builder(agent_name)

    def agent_actions_participant_id(self, participant_id: str):
        agent_builder = self.agent_builder_by_participant_id(participant_id)
        return agent_builder.agent_actions

    @abstractmethod
    def apply(self) -> None:
        raise NotImplementedError
