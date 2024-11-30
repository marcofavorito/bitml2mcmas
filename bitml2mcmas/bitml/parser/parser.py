"""Parser for BitML contracts."""

import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any, TypeVar

from lark import Lark, Token, Transformer

from bitml2mcmas.bitml.ast import (
    And,
    Between,
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLDefinition,
    BitMLDepositPrecondition,
    BitMLExpression,
    BitMLExpressionInt,
    BitMLExpressionSecret,
    BitMLFeePrecondition,
    BitMLParticipant,
    BitMLPreconditionExpression,
    BitMLPredicate,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLPutRevealIfExpression,
    BitMLRevealExpression,
    BitMLRevealIfExpression,
    BitMLSecretPrecondition,
    BitMLSplitBranch,
    BitMLSplitExpression,
    BitMLTransactionOutput,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
    EqualTo,
    GreaterThan,
    GreaterThanOrEqual,
    LessThan,
    LessThanOrEqual,
    Minus,
    Not,
    NotEqualTo,
    Or,
    Plus,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.custom_types import HexString, Name, TermString
from bitml2mcmas.bitml.parser._cached_lark import CachedLark
from bitml2mcmas.bitml.validation import BitMLContractValidator
from bitml2mcmas.helpers.misc import ROOT_PATH, assert_
from bitml2mcmas.helpers.validation import NonNegativeDecimal, NonNegativeInt

_PARSER_DIR = ROOT_PATH / "bitml" / "parser"


class BitMLTransformer(Transformer[Any, BitMLContract]):
    """Domain Transformer."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize the domain transformer."""
        super().__init__(*args, **kwargs)

        self.__context = BitMLContractValidator()

    def start(self, args: Sequence) -> BitMLContract:
        """Entry point."""
        return args[0]

    def contract_spec(self, args: Sequence) -> BitMLContract:
        definitions, preconditions, contract_body = args[1]
        definitions = tuple(reversed(definitions))
        return BitMLContract(definitions, preconditions, contract_body)

    def definitions_or_contract(
        self, args: Sequence
    ) -> tuple[Sequence[BitMLDefinition], Sequence[BitMLDefinition], BitMLContract]:
        if len(args) == 1:
            preconditions, contract_body = args[0]
            return [], preconditions, contract_body

        assert_(len(args) == 2)
        definition_clause = args[0]
        definitions, preconditions, contract_body = args[1]
        if definition_clause is not None:
            definitions.append(definition_clause)

        return definitions, preconditions, contract_body

    def participant_clause(self, args: Sequence) -> BitMLParticipant:
        participant = BitMLParticipant(args[2], args[3])
        self.__context.add_participant(participant)
        return participant

    def debug_mode_clause(self, args: Sequence) -> None:
        return None

    def define_clause(self, args: Sequence) -> None:
        return None

    def contract(
        self, args: Sequence
    ) -> tuple[Sequence[BitMLPreconditionExpression], BitMLExpression]:
        preconditions = args[2]
        body = args[3]
        return preconditions, body

    def contract_preconditions(
        self, args: Sequence
    ) -> Sequence[BitMLPreconditionExpression]:
        precondition_clauses = args[2:-1]
        return precondition_clauses

    def deposit_clause(self, args: Sequence) -> BitMLDepositPrecondition:
        participant_id, tx_amount, tx_id = args[2:-1]
        precondition = BitMLDepositPrecondition(participant_id, tx_amount, tx_id)
        self.__context.add_deposit_precondition(precondition)
        return precondition

    def secret_clause(self, args: Sequence) -> BitMLSecretPrecondition:
        participant_id, secret_id, secret_hash = args[2:-1]
        precondition = BitMLSecretPrecondition(participant_id, secret_id, secret_hash)
        self.__context.add_secret_precondition(precondition)
        return precondition

    def fee_clause(self, args: Sequence) -> BitMLFeePrecondition:
        participant_id, tx_amount, tx_id = args[2:-1]
        precondition = BitMLFeePrecondition(participant_id, tx_amount, tx_id)
        self.__context.add_fee_deposit_precondition(precondition)
        return precondition

    def volatile_deposit_clause(
        self, args: Sequence
    ) -> BitMLVolatileDepositPrecondition:
        participant_id, deposit_id, tx_amount, tx_id = args[2:-1]
        precondition = BitMLVolatileDepositPrecondition(
            participant_id, deposit_id, tx_amount, tx_id
        )
        self.__context.add_volatile_deposit_precondition(precondition)
        return precondition

    def contract_body(self, args: Sequence) -> BitMLExpression:
        return args[0]

    def withdraw_expr(self, args: Sequence) -> BitMLWithdrawExpression:
        participant_id = args[2]
        expr = BitMLWithdrawExpression(participant_id)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def after_expr(self, args: Sequence) -> BitMLAfterExpression:
        timeout = args[2]
        arg = args[3]
        expr = BitMLAfterExpression(timeout, arg)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def choice_expr(self, args: Sequence) -> BitMLChoiceExpression:
        choices = args[2:-1]
        expr = BitMLChoiceExpression(choices)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def authorization_expr(self, args: Sequence) -> BitMLAuthorizationExpression:
        participant_ids = args[2:-2]
        contract_expr = args[-2]
        reversed_participant_ids = list(reversed(participant_ids))
        result = BitMLAuthorizationExpression(
            reversed_participant_ids[0], contract_expr
        )
        for participant_id in reversed_participant_ids[1:]:
            result = BitMLAuthorizationExpression(participant_id, result)
        self.__context.check_bitml_contract_validity(result, recursive=False)
        return result

    def split_expr(self, args: Sequence) -> BitMLSplitExpression:
        expr = BitMLSplitExpression(args[2:-1])
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def put_expr(self, args: Sequence) -> BitMLPutExpression:
        vol_deposits = args[2]
        contract_expr = args[3]
        expr = BitMLPutExpression(vol_deposits, contract_expr)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def put_reveal_expr(self, args: Sequence) -> BitMLPutRevealExpression:
        vol_deposits_or_empty = args[2]
        secret_ids = args[3]
        contract_expr = args[4]
        expr = BitMLPutRevealExpression(
            vol_deposits_or_empty, secret_ids, contract_expr
        )
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def put_reveal_if_expr(self, args: Sequence) -> BitMLPutRevealIfExpression:
        vol_deposits_or_empty = args[2]
        secret_ids = args[3]
        if len(args) == 7:
            predicate = args[4]
            contract_expr = args[5]
            expr = BitMLPutRevealIfExpression(
                vol_deposits_or_empty, secret_ids, predicate, contract_expr
            )
        else:
            contract_expr = args[4]
            expr = BitMLPutRevealExpression(
                vol_deposits_or_empty, secret_ids, contract_expr
            )
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def reveal_if_expr(self, args: Sequence) -> BitMLRevealIfExpression:
        secret_ids = args[2]
        predicate = args[3]
        contract_expr = args[4]
        expr = BitMLRevealIfExpression(secret_ids, predicate, contract_expr)
        self.__context.check_predicate(predicate)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def reveal_expr(self, args: Sequence) -> BitMLRevealExpression:
        secret_ids = args[2]
        contract_expr = args[3]
        expr = BitMLRevealExpression(secret_ids, contract_expr)
        self.__context.check_bitml_contract_validity(expr, recursive=False)
        return expr

    def compilation_directives(self, args: Sequence) -> None:
        pass

    def predicate_def(self, args: Sequence) -> BitMLPredicate:
        return args[2]

    def minus_predicate(self, args: Sequence) -> Minus:
        arg_left = args[2]
        arg_right = args[3]
        return Minus(arg_left, arg_right)

    def plus_predicate(self, args: Sequence) -> Plus:
        arg_left = args[2]
        arg_right = args[3]
        return Plus(arg_left, arg_right)

    def atom_secret_id(self, args: Sequence) -> BitMLExpressionSecret:
        return BitMLExpressionSecret(args[0])

    def atom_int(self, args: Sequence) -> BitMLExpressionInt:
        return BitMLExpressionInt(NonNegativeInt(args[0]))

    def and_predicate(self, args: Sequence) -> And:
        arg_left = args[2]
        arg_right = args[3]
        return And(arg_left, arg_right)

    def or_predicate(self, args: Sequence) -> Or:
        arg_left = args[2]
        arg_right = args[3]
        return Or(arg_left, arg_right)

    def not_predicate(self, args: Sequence) -> Not:
        return Not(args[2])

    def between_predicate(self, args: Sequence) -> Between:
        arg = args[2]
        arg_left = args[3]
        arg_right = args[4]
        return Between(arg, arg_left, arg_right)

    def greater_than_or_equal_predicate(self, args: Sequence) -> GreaterThanOrEqual:
        arg_left = args[2]
        arg_right = args[3]
        return GreaterThanOrEqual(arg_left, arg_right)

    def greater_than_predicate(self, args: Sequence) -> GreaterThan:
        arg_left = args[2]
        arg_right = args[3]
        return GreaterThan(arg_left, arg_right)

    def less_than_or_equal_predicate(self, args: Sequence) -> LessThanOrEqual:
        arg_left = args[2]
        arg_right = args[3]
        return LessThanOrEqual(arg_left, arg_right)

    def less_than_predicate(self, args: Sequence) -> LessThan:
        arg_left = args[2]
        arg_right = args[3]
        return LessThan(arg_left, arg_right)

    def not_equal_to_predicate(self, args: Sequence) -> NotEqualTo:
        arg_left = args[2]
        arg_right = args[3]
        return NotEqualTo(arg_left, arg_right)

    def equal_to_predicate(self, args: Sequence) -> EqualTo:
        arg_left = args[2]
        arg_right = args[3]
        return EqualTo(arg_left, arg_right)

    def split_branch(self, args: Sequence) -> BitMLSplitBranch:
        value = NonNegativeDecimal(args[1])
        expr = args[3]
        return BitMLSplitBranch(value, expr)

    def vol_deposits(self, args: Sequence) -> tuple[TermString, ...]:
        seq = tuple([TermString(arg) for arg in args[1:-1]])
        return seq

    def vol_deposits_or_empty(self, args: Sequence) -> tuple[TermString, ...]:
        seq = tuple([TermString(arg) for arg in args[1:-1]])
        return seq

    def secret_ids(self, args: Sequence) -> tuple[TermString, ...]:
        seq = tuple([TermString(arg) for arg in args[1:-1]])
        return seq

    def deposit_id(self, args: Sequence) -> TermString:
        return TermString(args[0])

    def participant_id(self, args: Sequence) -> Name:
        return Name(args[0])

    def participant_pubkey(self, args: Sequence) -> HexString:
        return HexString(args[0])

    def tx_id(self, args: Sequence) -> BitMLTransactionOutput:
        tx_id = Name(args[1])
        tx_output_index = NonNegativeInt(args[2])
        return BitMLTransactionOutput(tx_id, tx_output_index)

    def tx_amount(self, args: Sequence) -> NonNegativeDecimal:
        return NonNegativeDecimal(args[0])

    def secret_id(self, args: Sequence) -> TermString:
        return TermString(args[0])

    def secret_hash(self, args: Sequence) -> HexString:
        return HexString(args[0])

    def INT(self, arg: Token) -> int:
        return int(arg)

    def QUOTED_NAME(self, token: Token) -> str:
        return str(token)[1:-1]

    def QUOTED_HEX(self, token: Token) -> str:
        return str(token)[1:-1]


class BitMLParser:
    """BitML parser class."""

    def __init__(self) -> None:
        """Initialize."""
        self._cached_parser = CachedLark(
            self._read_main_grammar(),
            parser="lalr",
            import_paths=[self._get_grammars_dir()],
        )

    @classmethod
    def _get_grammars_dir(cls) -> Path:
        return _PARSER_DIR / "grammars"

    @classmethod
    def _read_main_grammar(cls) -> str:
        grammar_file = cls._get_grammars_dir() / "main.lark"
        return grammar_file.read_text()

    def __call__(self, text: str) -> BitMLContract:
        """Call."""
        return call_parser(text, self._cached_parser.parser, BitMLTransformer())


T = TypeVar("T")


def call_parser(text: str, parser: Lark, transformer: Transformer[Any, T]) -> T:
    """Parse a text with a Lark parser and transformer.

    To produce a better traceback in case of an error, the function will temporarily overwrite the sys.tracebacklimit
    value of the current interpreter.

    :param text: the text to parse
    :param parser: the Lark parser object
    :param transformer: the Lark transformer object
    :return: the object returned by the parser
    """
    old_tracebacklimit = getattr(sys, "tracebacklimit", None)
    try:
        sys.tracebacklimit = 0
        tree = parser.parse(text)
        sys.tracebacklimit = None  # type: ignore[assignment]
        result = transformer.transform(tree)
    finally:
        if old_tracebacklimit is not None:
            sys.tracebacklimit = old_tracebacklimit
    return result


class BitMLParsingError(Exception):
    pass
