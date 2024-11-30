"""Custom types."""

from typing import Annotated, Literal

from bitml2mcmas.helpers.validation import InSet, NotInSet, StringConstraint

ENVIRONMENT = "Environment"
MCMAS_ID_PATTERN = r"^[A-Za-z][_A-Za-z0-9]*$"

MCMAS_KEYWORDS = {
    "A",
    "AF",
    "AG",
    "AX",
    "Action",
    "Actions",
    "DK",
    "E",
    "EF",
    "EG",
    "EX",
    ENVIRONMENT,
    "Evaluation",
    "Evolution",
    "F",
    "Fairness",
    "Formulae",
    "G",
    "GCK",
    "GK",
    "GreenStates",
    "Groups",
    "InitStates",
    "K",
    "Lobsvars",
    "MA",
    "MultiAssignment",
    "O",
    "Obsvars",
    "Other",
    "Protocol",
    "RedStates",
    "SAAgent",
    "Semantics",
    "SingleAssignment",
    "U",
    "Vars",
    "X",
    "and",
    "boolean",
    "end",
    "false",
    "if",
    "or",
    "true",
}

MCMAS_KEYWORDS_WITHOUT_ENV = MCMAS_KEYWORDS - {"Environment"}


McmasId = Annotated[
    str, StringConstraint(pattern=MCMAS_ID_PATTERN), NotInSet(MCMAS_KEYWORDS)
]

IdOrEnv = Annotated[
    str,
    StringConstraint(pattern=MCMAS_ID_PATTERN),
    NotInSet(MCMAS_KEYWORDS_WITHOUT_ENV),
]

EnvLiteral = Annotated[Literal["Environment"], InSet({ENVIRONMENT})]
