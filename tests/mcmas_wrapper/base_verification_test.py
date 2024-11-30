import shutil
import tempfile
from copy import copy
from pathlib import Path
from typing import Sequence

import pytest

from bitml2mcmas.bitml.parser.parser import BitMLParser
from bitml2mcmas.compiler._private.terms import TermNaming
from bitml2mcmas.compiler.core import Compiler
from bitml2mcmas.mcmas.ast import EvaluationRule
from bitml2mcmas.mcmas.boolcond import (
    BooleanCondition,
    EnvironmentIdAtom,
    EqualTo,
    GreaterThanOrEqual,
    IntAtom,
)
from bitml2mcmas.mcmas.formula import FormulaType
from bitml2mcmas.mcmas.to_string import interpreted_system_to_string
from tests.helpers import TEST_DIRECTORY, ROOT_DIRECTORY
from tests.mcmas_wrapper.wrapper import (
    McmasCliOptions,
    McmasResult,
    McmasSubprocessWrapper,
)

_MAX_TIMEOUT = 300


class BaseVerificationTest:
    PATH_TO_MCMAS_BIN: Path = TEST_DIRECTORY / "bin" / "mcmas"
    mcmas_options_kwargs: dict = dict(
        compute_counterexamples_or_witness_executions=3,
        strategy_generation_level=4,
        counterexample_generation_level=2,
        verbosity=5,
    )
    override_mcmas_options_kwargs: dict = dict(
        atlk=2,
    )
    BASE_VERIFICATION_OUTPUT_DIR: Path = (
        TEST_DIRECTORY / "test_compiler" / "verification_outputs"
    )

    tmp_file_path: Path
    mcmas_result: McmasResult
    mcmas_options: McmasCliOptions

    # test parameters
    PATH_TO_CONTRACT_FILE: Path
    FORMULAE_AND_EXPECTED_OUTCOME: Sequence[tuple[FormulaType, bool]]
    EVALUATION_RULES: tuple[EvaluationRule]
    GROUPS: set[str] = set()

    @classmethod
    def setup_class(cls) -> None:
        cls._prepare_verification_output_dir()

        contract = BitMLParser()(cls.PATH_TO_CONTRACT_FILE.read_text())
        compiler = Compiler(
            contract, cls._get_formulae(), evaluation_rules=cls.EVALUATION_RULES
        )
        system = compiler.compile()
        system_str = interpreted_system_to_string(system)

        cls.tmp_file_path = Path(tempfile.mktemp(suffix=".ispl"))
        cls.tmp_file_path.write_text(system_str)

        mcmas_wrapper = McmasSubprocessWrapper(cls.PATH_TO_MCMAS_BIN)
        cls.mcmas_options = cls._get_mcmas_cli_options()
        # save ispl file
        cls._save_ispl_file()
        cls.mcmas_result = mcmas_wrapper.call(
            cls.tmp_file_path, cls.mcmas_options, timeout=_MAX_TIMEOUT
        )
        cls._save_output_data()

    @classmethod
    def teardown_class(cls) -> None:
        cls.tmp_file_path.unlink(missing_ok=True)

    @classmethod
    def _prepare_verification_output_dir(cls):
        output_dir = cls._get_verification_output_dir()
        if output_dir.exists():
            for f in output_dir.iterdir():
                f.unlink(missing_ok=True)

        output_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def _get_verification_output_dir(cls) -> Path:
        return cls.BASE_VERIFICATION_OUTPUT_DIR / str(cls.__name__)

    @classmethod
    def _get_mcmas_cli_options(cls):
        options = copy(cls.mcmas_options_kwargs)
        options.update(cls.override_mcmas_options_kwargs)
        options["executions_output"] = str(cls._get_verification_output_dir())
        return McmasCliOptions(**options)

    @classmethod
    def _get_formulae(cls) -> list[FormulaType]:
        return [t[0] for t in cls.FORMULAE_AND_EXPECTED_OUTCOME]

    @classmethod
    def _save_ispl_file(cls):
        output_dir = cls._get_verification_output_dir()
        shutil.copy(cls.tmp_file_path, output_dir / "main.ispl")

    @classmethod
    def _save_output_data(cls):
        output_dir = cls._get_verification_output_dir()

        # save cli output
        (output_dir / "stdout.txt").write_text(cls.mcmas_result.cli_output)

        # save kwargs
        cli_command = cls.mcmas_options.get_cli_args()
        (output_dir / "command.txt").write_text("\n".join(cli_command))

    def test_verification(self, index, arg):
        if type(self) == BaseVerificationTest:
            pytest.skip("base test class")
        formula, expected_result = arg
        formula_str, actual_result = self.mcmas_result.verification_results[index]
        assert expected_result is actual_result, f"expected result for formula '{formula_str}' to be {expected_result}, got {actual_result}"
