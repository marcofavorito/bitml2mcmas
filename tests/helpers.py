"""Helper functions for tests."""

import inspect
from pathlib import Path

_current_filepath = inspect.getframeinfo(inspect.currentframe()).filename  # type: ignore[arg-type]
ROOT_DIRECTORY = Path(_current_filepath).absolute().parent.parent
TEST_DIRECTORY = Path(_current_filepath).absolute().parent
BITML_CONTRACTS_DIR = TEST_DIRECTORY / "bitml_contracts"
EXAMPLES_BITML_CONTRACTS_DIR = BITML_CONTRACTS_DIR / "examples"
INVALID_BITML_CONTRACTS_DIR = BITML_CONTRACTS_DIR / "invalid"
ORIGINAL_BITML_CONTRACTS_DIR = BITML_CONTRACTS_DIR / "original"
TESTS_BITML_CONTRACTS_DIR = BITML_CONTRACTS_DIR / "tests"


def read_original_bitml_contracts() -> list[Path]:
    return list(ORIGINAL_BITML_CONTRACTS_DIR.rglob("*.rkt"))


def read_examples_bitml_contracts() -> list[Path]:
    return list(EXAMPLES_BITML_CONTRACTS_DIR.rglob("*.rkt"))


def read_tests_bitml_contracts() -> list[Path]:
    return list(TESTS_BITML_CONTRACTS_DIR.rglob("*.rkt"))


def read_all_bitml_contracts() -> list[Path]:
    return (
        read_examples_bitml_contracts()
        + read_original_bitml_contracts()
        + read_tests_bitml_contracts()
    )


BITML_CONTRACT_FILES = read_all_bitml_contracts()


def get_contract_name_file_pairs() -> list[tuple[str, Path]]:
    result = []
    for filepath in BITML_CONTRACT_FILES:
        suffix_path = filepath.relative_to(TEST_DIRECTORY)
        contract_name = "_".join(suffix_path.with_suffix("").parts).lower()
        contract_name = contract_name.replace("-", "_")
        result.append((contract_name, filepath))
    return result
