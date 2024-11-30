"""Graph representation of a BitML smart contract."""

from collections.abc import Collection, Mapping, Sequence
from decimal import Decimal
from functools import cached_property, singledispatchmethod
from typing import AbstractSet, Union, cast

from bitml2mcmas.bitml.ast import (
    BitMLAfterExpression,
    BitMLAuthorizationExpression,
    BitMLChoiceExpression,
    BitMLDepositPrecondition,
    BitMLExpression,
    BitMLPutExpression,
    BitMLPutRevealExpression,
    BitMLRevealExpression,
    BitMLSplitExpression,
    BitMLVolatileDepositPrecondition,
    BitMLWithdrawExpression,
)
from bitml2mcmas.bitml.core import BitMLContract
from bitml2mcmas.bitml.custom_types import KEYWORDS, NAME_PATTERN
from bitml2mcmas.helpers.misc import assert_
from bitml2mcmas.helpers.validation import NotInSet, StringConstraint, ValidationError

NodeExpr = Union[
    BitMLWithdrawExpression,
    BitMLChoiceExpression,
    BitMLPutExpression,
    BitMLRevealExpression,
    BitMLPutRevealExpression,
    BitMLSplitExpression,
]


Guards = Union[BitMLAuthorizationExpression, BitMLAfterExpression]


def _get_expr_name(expr: NodeExpr):
    match expr:
        case BitMLWithdrawExpression():
            return "withdraw"
        case BitMLChoiceExpression():
            return "choice"
        case BitMLPutExpression():
            return "put"
        case BitMLRevealExpression():
            return "reveal"
        case BitMLPutRevealExpression():
            return "putreveal"
        case BitMLSplitExpression():
            return "split"
        case _:
            raise ValueError("")


class BitMLNode:
    def __init__(
        self,
        node_id: str,
        expression: NodeExpr,
        auths: Collection[str],
        afters: Collection[int],
        funds: Decimal,
        children: Sequence["BitMLNode"] | None = None,
        parent: Sequence["BitMLNode"] | None = None,
    ) -> None:
        assert_(
            isinstance(expression, NodeExpr),
            f"{expression!r} not a valid node expression",
        )
        self.__node_id = node_id
        self.__expression = expression
        self.__auths: AbstractSet[str] = self.__process_auths(auths)
        self.__afters: AbstractSet[int] = self.__process_afters(afters)
        self.__funds = funds
        self.__children: Sequence[BitMLNode] | None = self.__process_children(children)
        self.__parent: BitMLNode | None = parent

        self.__expr_name = _get_expr_name(self.__expression)

    @property
    def node_id(self) -> str:
        return self.__node_id

    @property
    def expr_name(self) -> str:
        return self.__expr_name

    @property
    def full_node_id(self) -> str:
        return f"{self.node_id}_{self.expr_name}"

    @property
    def expression(self) -> BitMLExpression:
        return self.__expression

    @property
    def auths(self) -> AbstractSet[str]:
        return self.__auths

    @property
    def afters(self) -> AbstractSet[int]:
        return self.__afters

    @property
    def children(self) -> Sequence["BitMLNode"]:
        if self.is_leaf_node:
            raise ValueError("node is a leaf node, it does not have children")
        return self.__children

    @property
    def is_leaf_node(self) -> bool:
        return self.__children is None

    @property
    def parent(self) -> "BitMLNode":
        return self.__parent

    @parent.setter
    def parent(self, parent: "BitMLNode") -> None:
        if self.__parent is not None:
            raise ValueError("parent node already set")
        self.__parent = parent

    @property
    def funds(self) -> Decimal:
        return self.__funds

    def __process_auths(self, auths: Collection[str]) -> frozenset[str]:
        for participant_id in auths:
            try:
                (
                    StringConstraint(pattern=NAME_PATTERN),
                    NotInSet(KEYWORDS).process(participant_id),
                )
            except ValidationError:
                raise ValueError(f"participant id {participant_id!r} is not valid")

        return frozenset(auths)

    def __process_afters(self, afters: Collection[int]) -> frozenset[int]:
        if any(i < 0 for i in afters):
            raise ValueError("all timeouts must be non-negative")
        return frozenset(afters)

    def __process_children(
        self, children: Sequence["BitMLNode"] | None
    ) -> Sequence["BitMLNode"] | None:
        if children is not None and len(children) == 0:
            raise ValueError("got empty list of children")
        return children


class BitMLGraph:
    def __init__(self, bitml_contract: BitMLContract) -> None:
        self.__contract = bitml_contract

        self.__nodes: list[BitMLNode] = []
        self.__timeouts: set[int] = set()

        self.__root_node = self.build_contract_graph(
            bitml_contract.contract_root,
            tuple(),
            tuple(),
            self.total_persistent_deposits,
        )

    @property
    def contract(self) -> BitMLContract:
        return self.__contract

    @property
    def nodes(self) -> tuple[BitMLNode, ...]:
        return tuple(self.__nodes)

    @property
    def timeouts(self) -> AbstractSet[int]:
        return frozenset(self.__timeouts)

    @property
    def max_timeout(self) -> int:
        return max(self.__timeouts)

    @property
    def root_node(self) -> BitMLNode:
        return self.__root_node

    @cached_property
    def persistent_deposits(self) -> tuple[BitMLDepositPrecondition, ...]:
        return tuple(
            [
                prec
                for prec in self.contract.preconditions
                if isinstance(prec, BitMLDepositPrecondition)
            ]
        )

    @cached_property
    def volatile_deposits(self) -> tuple[BitMLDepositPrecondition, ...]:
        return tuple(
            [
                prec
                for prec in self.contract.preconditions
                if isinstance(prec, BitMLDepositPrecondition)
            ]
        )

    @property
    def total_persistent_deposits(self) -> Decimal:
        return cast(Decimal, sum([dep.amount for dep in self.persistent_deposits]))

    @cached_property
    def volatile_deposits_by_id(self) -> Mapping[str, Decimal]:
        return {
            vd.deposit_id: vd.amount
            for vd in self.contract.preconditions
            if isinstance(vd, BitMLVolatileDepositPrecondition)
        }

    def _create_node(
        self,
        expression: NodeExpr,
        auths: Collection[str],
        afters: Collection[int],
        funds: Decimal,
        children: Sequence["BitMLNode"] | None = None,
        parent: BitMLNode | None = None,
    ) -> BitMLNode:
        new_id = len(self.__nodes)
        node_id = f"node_{new_id}"
        node = BitMLNode(node_id, expression, auths, afters, funds, children, parent)
        self.__nodes.append(node)
        self.__timeouts.update(afters)
        return node

    @singledispatchmethod
    def build_contract_graph(
        self,
        obj: object,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        raise CaseNotHandledError(boolcond_to_string.__name__, obj)  # type: ignore[attr-defined]

    @build_contract_graph.register
    def build_contract_graph_withdraw(
        self,
        expr: BitMLWithdrawExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        node = self._create_node(expr, current_auths, current_afters, available_funds)
        return node

    @build_contract_graph.register
    def build_contract_graph_auth(
        self,
        expr: BitMLAuthorizationExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        new_auths = current_auths + tuple([expr.participant_id])
        node = self.build_contract_graph(
            expr.branch, new_auths, current_afters, available_funds
        )
        return node

    @build_contract_graph.register
    def build_contract_graph_after(
        self,
        expr: BitMLAfterExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        new_afters = current_afters + tuple([expr.timeout])
        node = self.build_contract_graph(
            expr.branch, current_auths, new_afters, available_funds
        )
        return node

    @build_contract_graph.register
    def build_contract_graph_choice(
        self,
        expr: BitMLChoiceExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        assert_(
            len(current_auths) == 0,
            f"'authentication' guards were not expected for a choice expression, got {current_auths!r}",
        )
        assert_(
            len(current_afters) == 0,
            f"'after' guards were not expected for a choice expression, got {current_auths!r}",
        )

        children = [
            self.build_contract_graph(choice, tuple(), tuple(), available_funds)
            for choice in expr.choices
        ]
        node = self._create_node(
            expr, current_auths, current_afters, available_funds, children=children
        )

        for child in children:
            child.parent = node

        return node

    @build_contract_graph.register
    def build_contract_graph_split(
        self,
        expr: BitMLSplitExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        children = [
            self.build_contract_graph(
                split_branch.branch, tuple(), tuple(), split_branch.amount
            )
            for split_branch in expr.branches
        ]
        node = self._create_node(
            expr, current_auths, current_afters, available_funds, children=children
        )

        for child in children:
            child.parent = node
        return node

    @build_contract_graph.register
    def build_contract_graph_put(
        self,
        expr: BitMLPutExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        return self._build_contract_graph_put_like_expr(
            expr, current_auths, current_afters, available_funds
        )

    @build_contract_graph.register
    def build_contract_graph_reveal(
        self,
        expr: BitMLRevealExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        child_node = self.build_contract_graph(
            expr.branch, tuple(), tuple(), available_funds
        )
        node = self._create_node(
            expr, current_auths, current_afters, available_funds, children=[child_node]
        )
        child_node.parent = node
        return node

    @build_contract_graph.register
    def build_contract_graph_put_reveal(
        self,
        expr: BitMLPutRevealExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        return self._build_contract_graph_put_like_expr(
            expr, current_auths, current_afters, available_funds
        )

    def _build_contract_graph_put_like_expr(
        self,
        expr: BitMLPutRevealExpression | BitMLPutExpression,
        current_auths: tuple[str],
        current_afters: tuple[int],
        available_funds: Decimal,
    ) -> BitMLNode:
        new_funds = available_funds
        for deposit_id in expr.deposit_ids:
            new_funds += self.volatile_deposits_by_id[deposit_id]

        child_node = self.build_contract_graph(expr.branch, tuple(), tuple(), new_funds)
        node = self._create_node(
            expr, current_auths, current_afters, available_funds, children=[child_node]
        )
        child_node.parent = node
        return node
