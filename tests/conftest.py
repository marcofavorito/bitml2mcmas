"""Pytest tests configurations."""

from bitml2mcmas.bitml.parser.parser import BitMLParser
from tests.bitml_contracts.code_defined import *
from tests.helpers import get_contract_name_file_pairs
from tests.mcmas_wrapper.base_verification_test import BaseVerificationTest


def pytest_addoption(parser):
    parser.addoption(
        "--runslow", action="store_true", default=False,  dest="runslow", help="run slow tests"
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: mark test as slow to run")


def pytest_collection_modifyitems(config, items):
    if config.getoption("--runslow"):
        # --runslow given in cli: do not skip slow tests
        return
    skip_slow = pytest.mark.skip(reason="need --runslow option to run")
    for item in items:
        if "slow" in item.keywords:
            item.add_marker(skip_slow)


# Dynamically generate test cases using pytest.mark.parametrize
def pytest_generate_tests(metafunc):
    testcls = metafunc.cls
    if type(testcls) == type and issubclass(testcls, BaseVerificationTest) and metafunc.function.__name__ == "test_verification":
        formulae_and_expected_outcomes = getattr(testcls, "FORMULAE_AND_EXPECTED_OUTCOME")
        indexed_args = list(enumerate(formulae_and_expected_outcomes))
        metafunc.parametrize("index,arg", indexed_args)


@pytest.fixture(scope="session")
def bitml_parser() -> BitMLParser:
    return BitMLParser()


file_contract_pairs = get_contract_name_file_pairs()

contract_obj_fixtures, contract_files = list(zip(*file_contract_pairs, strict=False))
