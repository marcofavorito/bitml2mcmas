"""Tests for the bitml.to_string module."""

from pathlib import Path

import pytest

from bitml2mcmas.bitml.parser.parser import BitMLParser
from bitml2mcmas.bitml.to_string import to_string
from tests.conftest import (
    contract_files,
)


@pytest.mark.parametrize("contract_file", contract_files)
def test_parser_parametrized(contract_file: Path, bitml_parser: BitMLParser) -> None:
    expected_contract_str = contract_file.read_text()
    contract_obj = bitml_parser(expected_contract_str)
    actual_contract_str = to_string(contract_obj)

    # The original BitML DSL supported the operator 'putrevealif' without the predicate expression.
    # In our library, this expression is parsed as 'putreveal', and printed as 'putreveal'.
    # Therefore, to compare the to_string output, we must replace the original 'putrevealif' with the new expression.
    expected_contract_str = expected_contract_str.replace("putrevealif ", "putreveal ")

    assert (
        expected_contract_str == actual_contract_str
    ), f"expected:\n{expected_contract_str}\n\nactual:\n{actual_contract_str}"
