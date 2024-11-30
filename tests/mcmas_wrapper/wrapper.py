import dataclasses
import logging
import re
import subprocess
from pathlib import Path


@dataclasses.dataclass(frozen=True)
class McmasCliOptions:
    """CLI Options for the MCMAS tool.

    For explanation, please read the MCMAS manual: https://sail.doc.ic.ac.uk/software/mcmas/manual.pdf
    """

    # -v Number: this option is used to modify the verbosity level. It is particularly useful to detect the
    # bottlenecks in large examples and to investigate unexpected behaviours of MCMAS or bugs.
    verbosity: int | None = None

    # -u: this option is used to print statistics on OBDDs at the end of the execution. Using this option, it is
    # possible to estimate memory consumption and the compression level. This options works even if MCMAS
    # is terminated by ctrl+c
    print_bdd_statistics: bool = False

    # -e Number: this option is used to switch between different strategies for the computation of the transition
    # relation and reachable states. Option 1, 2 and 3 differ on how reachable states are computed internally.
    reachable_state_space_strategy: int | None = None

    # -o Number: this option is used to switch between different strategies for BDD ordering. (1 -- 4, default 2)
    bdd_var_ordering_strategy: int | None = None

    # -g Number: this option groups BDD variables to speed up dynamic BDD reordering: option 1 group two
    # adjacent BDD variables; option 2 groups BDD variables for each ISPL variable; option 3 groups BDD
    # variables based on ISPL variables and each agent’s actions, which is the default choice.
    bdd_var_grouping_strategy: int | None = None

    # -d Number: this option disables dynamic reordering on BDD variable during the verification process when
    # Number > 0: option 1 disable the reordering in the whole process; option 2 disables the reordering after
    # transition relation is built; option 3 switches off the reordering after reachable states are computed, which
    # is the default choice.
    dynamic_bdd_reordering_disabling_point: int | None = None

    # -nobddcache: this option disables the internal BDD cache. In general, the internal BDD cache reduces
    # the running time. But in some rare cases, it can slow down the verification.
    nobddcache: bool = False

    # -k: this option searches for a deadlock state in the model, where no agents can make progress. If combined
    # with option -c, a witness execution is generated from an initial state to the deadlock state.
    check_deadlock: bool = False

    # -a: this option searches for a state in which an arithmetic overflow can occur, i.e., the value assigned to
    # an bounded integer variable is beyond the upper or lower bound of the variable. A witness execution is
    # generated if combined with -c
    check_arithmetic_overflow: bool = False

    # -c Number: this option is used to compute counterexamples (for false universal formulae) and witnesses
    # (for true existential formulae). For each formula for which such computation is possible, option 1 prints a
    # textual representation on screen; option 2 emits two files: “formulaN .dot” encoding the graphical repre-
    # sentation of the counterexample/witness path, and “formulaN .info” file containing a detailed description
    # of the states in the path, where N is the number of the formula; option 3 produces both the textual and
    # graphical representations
    compute_counterexamples_or_witness_executions: int | None = None

    # -p String: this option allows users to choose a specific directory to store the graphical representations for
    # counterexamples/witness executions. The default location is the current directory.
    executions_output: Path | None = None

    # -exportmodel : this option instructs MCMAS to export the generated LTS model from the ISPL file to
    # the file “model.dot” in Graphviz dot format and the file “model.info”. The LTS model can be displayed
    # in the graphical interface in the same way as for counterexamples
    export_model: bool = False

    # -f Number: this option chooses the level of generating ATL strategies: option 1 generates all strategies
    # for the outermost ATL operator; option 2 recursively generates all strategies for all ATL operators; option
    # 3 generates only one strategy for the outermost ATL operator; option 4 recursively generates one strategy
    # for all ATL operators.
    strategy_generation_level: int | None = None

    # -l: this option forces MCMAS to generate a counterexample for an ATL formula, which is not built by
    # -c options because the counterexample is an execution tree. (1 -- 2)
    counterexample_generation_level: int | None = None

    # -w: this option force MCMAS to choose a new state that is not visited before when possible at each step
    # of the generation of ATL strategies.
    force_choose_new_state: bool = False

    # -atlk: this option chooses what ATL semantics is used for verification. Semantics 0 is used when no
    # fariness constraint is present and full observability is assumed. Under fairness constraints, semantics 1
    # assumes full observability and semantics 2 assumes partial observability (hence uniform strategy). The
    # details about observability can be found in [2].
    atlk: int | None = None

    # -uc: this option specifies when MCMAS prints the number of uniform strategies that have been processed
    # during verification. When the number of uniform strategies can be divided by the value specified in this
    # option without a reminder, MCMAS prints the number to inform users about the progress of verification.
    # The default value is 10.
    uc: int | None = None

    # -uniform: this option chooses the uniform strategy semantics defined in [6]. This option will subsume
    # the option -atlk.
    uniform: bool = False

    # -ufgroup Name: this option specifies the name of the group when generating uniform strategies. Only
    # the agents in the group have uniform strategies; others do not have any. If this option is not used, then
    # all agents have uniform strategies by default.
    ufgroup: str | None = None

    # -n: this option disallows MCMAS to compare two enumeration types one of which is a strict subset of
    # the other
    disable_enum_comparison: bool = False

    def __post_init__(self):
        self._validate_verbosity()
        self._validate_reachable_state_space_strategy()
        self._validate_bdd_var_ordering_strategy()
        self._validate_bdd_var_grouping_strategy()
        self._validate_dynamic_bdd_reordering_disabling_point()
        self._validate_compute_counterexamples_or_witness_executions()
        self._validate_strategy_generation_level()
        self._validate_counterexample_generation_level()
        self._validate_atlk()
        self._validate_uc()

    def _check_in_range(self, option_name: str, value: int | None, r: range):
        if value is not None and value not in r:
            raise ValueError(f"{option_name} must be between {r.start} and {r.stop}")

    def _validate_verbosity(self) -> None:
        self._check_in_range("verbosity", self.verbosity, range(1, 6))

    def _validate_reachable_state_space_strategy(self) -> None:
        self._check_in_range(
            "reachable_state_space_strategy",
            self.reachable_state_space_strategy,
            range(1, 4),
        )

    def _validate_bdd_var_ordering_strategy(self):
        self._check_in_range(
            "bdd_var_ordering_strategy", self.bdd_var_ordering_strategy, range(1, 5)
        )

    def _validate_bdd_var_grouping_strategy(self):
        self._check_in_range(
            "bdd_var_grouping_strategy", self.bdd_var_grouping_strategy, range(1, 4)
        )

    def _validate_dynamic_bdd_reordering_disabling_point(self):
        self._check_in_range(
            "dynamic_bdd_reordering_disabling_point",
            self.dynamic_bdd_reordering_disabling_point,
            range(1, 4),
        )

    def _validate_compute_counterexamples_or_witness_executions(self):
        self._check_in_range(
            "compute_counterexamples_or_witness_executions",
            self.compute_counterexamples_or_witness_executions,
            range(1, 4),
        )

    def _validate_strategy_generation_level(self):
        self._check_in_range(
            "strategy_generation_level", self.strategy_generation_level, range(1, 5)
        )

    def _validate_counterexample_generation_level(self):
        self._check_in_range(
            "counterexample_generation_level",
            self.counterexample_generation_level,
            range(1, 3),
        )

    def _validate_atlk(self):
        self._check_in_range("atlk", self.counterexample_generation_level, range(3))

    def _validate_uc(self):
        if self.uc is not None and self.uc < 1:
            raise ValueError("uc must be strictly positive")

    def get_cli_args(self) -> list[str]:
        result = []
        if self.verbosity is not None:
            result += ["-v", str(self.verbosity)]

        if self.print_bdd_statistics:
            result += ["-u"]

        if self.reachable_state_space_strategy is not None:
            result += ["-e", str(self.reachable_state_space_strategy)]

        if self.bdd_var_ordering_strategy is not None:
            result += ["-o", str(self.bdd_var_ordering_strategy)]

        if self.bdd_var_grouping_strategy is not None:
            result += ["-g", str(self.bdd_var_grouping_strategy)]

        if self.dynamic_bdd_reordering_disabling_point is not None:
            result += ["-d", str(self.dynamic_bdd_reordering_disabling_point)]

        if self.nobddcache:
            result += ["-nobddcache"]

        if self.check_deadlock:
            result += ["-k"]

        if self.check_arithmetic_overflow:
            result += ["-a"]

        if self.compute_counterexamples_or_witness_executions is not None:
            result += ["-c", str(self.compute_counterexamples_or_witness_executions)]

        if self.executions_output is not None:
            result += ["-p", str(self.executions_output)]

        if self.export_model:
            result += ["-exportmodel"]

        if self.strategy_generation_level is not None:
            result += ["-f", str(self.strategy_generation_level)]

        if self.counterexample_generation_level is not None:
            result += ["-l", str(self.counterexample_generation_level)]

        if self.force_choose_new_state:
            result += ["-w"]

        if self.atlk is not None:
            result += ["-atlk", str(self.atlk)]

        if self.uc is not None:
            result += ["-uc", str(self.uc)]

        if self.uniform:
            result += ["-uniform"]

        if self.ufgroup is not None:
            result += ["-ufgroup", str(self.ufgroup)]

        if self.disable_enum_comparison:
            result += ["-n"]

        return result


@dataclasses.dataclass(frozen=True)
class McmasResult:
    cli_output: str
    verification_results: list[tuple[str, bool]]

    @classmethod
    def parse(cls, cli_output: str) -> "McmasResult":
        verification_results = []
        matches = re.findall(
            r"Formula number \d+: (.*), is (TRUE|FALSE) in the model",
            cli_output,
            flags=re.MULTILINE,
        )
        for formula_str, verification_result_str in matches:
            verification_result = True if verification_result_str == "TRUE" else False
            verification_results.append((formula_str, verification_result))
        return McmasResult(cli_output, verification_results)


class McmasSubprocessWrapper:
    def __init__(self, mcmas_bin_path: Path) -> None:
        self.__mcmas_bin_path = mcmas_bin_path.resolve(strict=True)

    @property
    def mcmas_bin_path(self) -> Path:
        return self.__mcmas_bin_path

    def call(
        self,
        input_file: Path,
        options: McmasCliOptions | None = None,
        timeout: int = 10,
    ) -> McmasResult:
        args = options.get_cli_args() if options is not None else []
        proc = subprocess.Popen(
            [str(self.mcmas_bin_path), *args, input_file],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        cli_output, _ = proc.communicate(timeout=timeout)
        cli_output_str = cli_output.decode("utf-8")
        logging.info(cli_output_str)
        return McmasResult.parse(cli_output_str)
