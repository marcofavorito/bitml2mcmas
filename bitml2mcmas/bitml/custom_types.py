"""Custom types."""

from typing import Annotated

from bitml2mcmas.helpers.validation import NotInSet, StringConstraint

DEFINE_ID_PATTERN = r"^[A-Za-z][_A-Za-z]*$"
NAME_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"
TERM_PATTERN = r"^[A-Za-z_][A-Za-z0-9_]*$"
HEXSTRING_PATTERN = r"^[0-9a-f]*$"


KEYWORDS = frozenset(
    {
        "after",
        "and",
        "auth",
        "between",
        "check",
        "check-liquid",
        "check-query",
        "choice",
        "contract",
        "debug-mode",
        "define",
        "deposit",
        "fee",
        "or",
        "not",
        "participant",
        "pre",
        "pred",
        "put",
        "putrevealif",
        "reveal",
        "revealif",
        "secret",
        "split",
        "vol-deposit",
        "withdraw",
    }
)


Name = Annotated[str, StringConstraint(pattern=NAME_PATTERN), NotInSet(KEYWORDS)]
HexString = Annotated[str, StringConstraint(pattern=HEXSTRING_PATTERN)]
TermString = Annotated[str, StringConstraint(pattern=TERM_PATTERN), NotInSet(KEYWORDS)]
