from collections.abc import Collection, Generator, Mapping, Sequence
from typing import AbstractSet, Generic, TypeVar, cast

from bitml2mcmas.bitml.ast import (
    BitMLDepositPrecondition,
    BitMLSecretPrecondition,
    BitMLVolatileDepositPrecondition,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.custom_types import Name
from bitml2mcmas.compiler._private.contract_graph import BitMLGraph
from bitml2mcmas.compiler._private.terms import TermNaming
from bitml2mcmas.helpers.misc import assert_
from bitml2mcmas.mcmas.ast import Protocol
from bitml2mcmas.mcmas.custom_types import McmasId


class _HasParticipantId(Protocol):
    participant_id: Name


_HasParticipantIdType = TypeVar("_HasParticipantIdType", bound=_HasParticipantId)


class ContractWrapper:
    def __init__(self, contract: BitMLContract) -> None:
        self.__contract = contract

        self.__participant_ids = self._get_participant_ids()
        self.__participant_ids_with_prefix = self._get_participant_ids_with_prefix()

        self.__persistent_deposits, self.__volatile_deposits, self.__secrets = (
            self._split_preconditions()
        )
        self.__volatile_deposits_by_id = self._index_by_deposit_id(
            self.__volatile_deposits
        )
        self.__persistent_deposits_by_participant_id = self._index_by_participant_id(
            self.__persistent_deposits
        )
        self.__volatile_deposits_by_participant_id = self._index_by_participant_id(
            self.__volatile_deposits
        )
        self.__secrets_by_id = self._index_by_secret_id(self.__secrets)
        self.__secrets_by_participant_id = self._index_by_participant_id(self.__secrets)

        self.__total_persistent_deposits = self._get_total_persistent_deposits(
            self.__persistent_deposits
        )
        self.__total_volatile_deposits = self._get_total_volatile_deposits(
            self.__volatile_deposits
        )
        self.__total_deposits = (
            self.__total_persistent_deposits + self.__total_volatile_deposits
        )

        self.__graph = BitMLGraph(self.contract)

    @property
    def contract(self) -> BitMLContract:
        return self.__contract

    @property
    def graph(self) -> BitMLGraph:
        return self.__graph

    @property
    def participant_ids(self) -> AbstractSet[str]:
        return self.__participant_ids

    @property
    def participant_ids_with_prefix(self) -> AbstractSet[str]:
        return self.__participant_ids_with_prefix

    @property
    def persistent_deposits(self) -> AbstractSet[BitMLDepositPrecondition]:
        return self.__persistent_deposits

    @property
    def volatile_deposits(self) -> AbstractSet[BitMLVolatileDepositPrecondition]:
        return self.__volatile_deposits

    @property
    def secrets(self) -> AbstractSet[BitMLSecretPrecondition]:
        return self.__secrets

    @property
    def persistent_deposits_by_participant_id(
        self,
    ) -> Mapping[str, Sequence[BitMLDepositPrecondition]]:
        return cast(
            Mapping[str, Sequence[BitMLDepositPrecondition]],
            self.__persistent_deposits_by_participant_id,
        )

    @property
    def volatile_deposits_by_participant_id(
        self,
    ) -> Mapping[str, Sequence[BitMLVolatileDepositPrecondition]]:
        return cast(
            Mapping[str, Sequence[BitMLVolatileDepositPrecondition]],
            self.__volatile_deposits_by_participant_id,
        )

    @property
    def volatile_deposits_by_id(self) -> Mapping[str, BitMLVolatileDepositPrecondition]:
        return self.__volatile_deposits_by_id

    @property
    def secrets_by_id(
        self,
    ) -> Mapping[str, BitMLSecretPrecondition]:
        return cast(
            Mapping[str, BitMLSecretPrecondition],
            self.__secrets_by_id,
        )

    @property
    def secrets_by_participant_id(
        self,
    ) -> Mapping[str, Sequence[BitMLSecretPrecondition]]:
        return cast(
            Mapping[str, Sequence[BitMLSecretPrecondition]],
            self.__secrets_by_participant_id,
        )

    @property
    def volatile_deposit_names(self) -> Generator[str, None, None]:
        for deposit in self.__volatile_deposits:
            yield TermNaming.deposit_with_prefix(deposit.deposit_id)

    @property
    def total_deposit_amount(self) -> int:
        return self.__total_deposits

    @property
    def total_persistent_deposit_amount(self) -> int:
        return self.__total_persistent_deposits

    @property
    def total_volatile_deposit_amount(self) -> int:
        return self.__total_volatile_deposits

    @property
    def has_timeouts(self) -> bool:
        return len(self.graph.timeouts) > 0

    @property
    def has_secrets(self) -> bool:
        return len(self.secrets) > 0

    def get_secrets_of_participant(
        self, participant_id: str
    ) -> Sequence[BitMLSecretPrecondition]:
        return self.__secrets_by_participant_id.get(participant_id, [])

    def _get_participant_ids(self) -> set[McmasId]:
        return set(part.identifier for part in self.contract.participants)

    def _get_participant_ids_with_prefix(self) -> set[McmasId]:
        return set(
            TermNaming.participant_name_with_prefix(part.identifier)
            for part in self.contract.participants
        )

    def _split_preconditions(
        self,
    ) -> tuple[
        set[BitMLDepositPrecondition],
        set[BitMLVolatileDepositPrecondition],
        set[BitMLSecretPrecondition],
    ]:
        persistent_deposits, volatile_deposits, secrets = set(), set(), set()
        for precondition in self.contract.preconditions:
            if isinstance(precondition, BitMLDepositPrecondition):
                # TODO handle fractions of integers or use satoshi as amount unit
                assert_(int(precondition.amount) == precondition.amount)
                persistent_deposits.add(precondition)
            elif isinstance(precondition, BitMLVolatileDepositPrecondition):
                # TODO handle fractions of integers or use satoshi as amount unit
                assert_(int(precondition.amount) == precondition.amount)
                volatile_deposits.add(precondition)
            elif isinstance(precondition, BitMLSecretPrecondition):
                secrets.add(precondition)
        return persistent_deposits, volatile_deposits, secrets

    def _get_total_persistent_deposits(
        self, deposits: Collection[BitMLDepositPrecondition]
    ) -> int:
        return sum([int(dep.amount) for dep in deposits])

    def _get_total_volatile_deposits(
        self, deposits: Collection[BitMLVolatileDepositPrecondition]
    ) -> int:
        return sum([int(dep.amount) for dep in deposits])

    def _index_by_participant_id(
        self, collection: Collection[Generic[_HasParticipantIdType]]
    ) -> Mapping[str, Sequence[_HasParticipantIdType]]:
        result = {}
        for item in collection:
            result.setdefault(item.participant_id, []).append(item)
        return result

    def _index_by_deposit_id(
        self, volatile_deposits: Collection[BitMLVolatileDepositPrecondition]
    ):
        return {item.deposit_id: item for item in volatile_deposits}

    def _index_by_secret_id(self, secrets: Collection[BitMLSecretPrecondition]):
        return {secret.secret_id: secret for secret in secrets}
