"""Test BitML parser."""

from pathlib import Path

import pytest
from _pytest.fixtures import SubRequest

from bitml2mcmas.bitml.parser.parser import BitMLParser
from tests.conftest import file_contract_pairs


@pytest.mark.parametrize("contract_fixture_str, contract_file", file_contract_pairs)
def test_parser_parametrized(
    contract_fixture_str: str,
    contract_file: Path,
    bitml_parser: BitMLParser,
    request: SubRequest,
) -> None:
    expected_contract_obj = request.getfixturevalue(contract_fixture_str)
    actual_contract_obj = bitml_parser(contract_file.read_text())
    assert expected_contract_obj.participants == actual_contract_obj.participants
    assert expected_contract_obj.preconditions == actual_contract_obj.preconditions
    assert expected_contract_obj.contract_root == actual_contract_obj.contract_root
