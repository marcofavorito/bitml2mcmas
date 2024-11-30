import pytest

from bitml2mcmas.bitml.custom_types import TermString
from bitml2mcmas.compiler._private.terms import PARTICIPANTS_GROUP, PARTICIPANTS_AND_ENV_GROUP, CONTRACT_FUNDS, \
    CONTRACT_IS_INITIALIZED, TermNaming, PublicSecretValues, PrivateSecretValues
from bitml2mcmas.mcmas.ast import EvaluationRule
from bitml2mcmas.mcmas.boolcond import EqualTo, IntAtom, IdAtom, EnvironmentIdAtom, TrueBoolValue, GreaterThanOrEqual, \
    LessThan
from bitml2mcmas.mcmas.formula import AFFormula, DiamondEventuallyFormula, EFFormula, EGFormula, NotFormula, AGFormula, \
    OrFormula, AndFormula, AtomicFormula, FormulaType, ImpliesFormula
from tests.helpers import TESTS_BITML_CONTRACTS_DIR, EXAMPLES_BITML_CONTRACTS_DIR
from tests.mcmas_wrapper.base_verification_test import BaseVerificationTest
from tests.mcmas_wrapper.shared import (
    A_GETS_2,
    A_GETS_2_FORMULA,
    AGENT_A_GROUP,
    AGENT_B_GROUP,
    PARTICIPANT_A, CONTRACT_FUNDS_ARE_ZERO_ER, CONTRACT_IS_LIQUID_FORMULA_FOR_A, CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE,
    CONTRACT_IS_LIQUID_FORMULA_FOR_B, B_GETS_2_FORMULA, B_GETS_2, PARTICIPANT_B, B_GETS_2_ER, A_GETS_2_ER,
    A_GETS_1_FORMULA, A_GETS_1_ER, EF_FUNDS_IS_ZERO, AF_FUNDS_IS_ZERO, TIME_REACHES_MAXIMUM_FORMULA,
    AF_A_GETS_2_FORMULA, AF_NOT_A_GETS_2_FORMULA, EF_A_GETS_2_FORMULA, EF_NOT_A_GETS_2_FORMULA, AG_A_GETS_2_FORMULA,
    AG_NOT_A_GETS_2_FORMULA, EG_A_GETS_2_FORMULA, EG_NOT_A_GETS_2_FORMULA, AGENT_A_GROUP_A_GETS_2_FORMULA,
    AGENT_B_GROUP_A_GETS_2_FORMULA, PARTICIPANTS_GROUP_A_GETS_2_FORMULA, AGENT_A_GROUP_B_GETS_2_FORMULA,
    AGENT_B_GROUP_B_GETS_2_FORMULA, PARTICIPANTS_GROUP_B_GETS_2_FORMULA, AF_B_GETS_2_FORMULA, AF_NOT_B_GETS_2_FORMULA,
    EF_B_GETS_2_FORMULA, EF_NOT_B_GETS_2_FORMULA, AG_B_GETS_2_FORMULA, AG_NOT_B_GETS_2_FORMULA, EG_B_GETS_2_FORMULA,
    EG_NOT_B_GETS_2_FORMULA, AF_A_GETS_1_FORMULA, AF_NOT_A_GETS_1_FORMULA, EF_A_GETS_1_FORMULA, EF_NOT_A_GETS_1_FORMULA,
    AG_A_GETS_1_FORMULA, AG_NOT_A_GETS_1_FORMULA, EG_A_GETS_1_FORMULA, EG_NOT_A_GETS_1_FORMULA, AF_B_GETS_1_FORMULA,
    AF_NOT_B_GETS_1_FORMULA, EF_B_GETS_1_FORMULA, EF_NOT_B_GETS_1_FORMULA, AG_B_GETS_1_FORMULA, AG_NOT_B_GETS_1_FORMULA,
    EG_B_GETS_1_FORMULA, EG_NOT_B_GETS_1_FORMULA, AGENT_A_GROUP_A_GETS_1_FORMULA, AGENT_B_GROUP_A_GETS_1_FORMULA,
    PARTICIPANTS_GROUP_A_GETS_1_FORMULA, AGENT_A_GROUP_B_GETS_1_FORMULA, AGENT_B_GROUP_B_GETS_1_FORMULA,
    PARTICIPANTS_GROUP_B_GETS_1_FORMULA, B_GETS_1_ER, CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE,
    CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B,
    A_GETS_4_ER, AF_A_GETS_4_FORMULA, AF_NOT_A_GETS_4_FORMULA, EF_A_GETS_4_FORMULA, EF_NOT_A_GETS_4_FORMULA,
    AG_A_GETS_4_FORMULA, AG_NOT_A_GETS_4_FORMULA, EG_A_GETS_4_FORMULA, EG_NOT_A_GETS_4_FORMULA,
    AGENT_A_GROUP_A_GETS_4_FORMULA, AGENT_B_GROUP_A_GETS_4_FORMULA, PARTICIPANTS_GROUP_A_GETS_4_FORMULA,
    participant_gets_x, _get_contract_is_liquid_formula_for_group,
    _get_contract_is_liquid_formula_after_initialization_for_group, B_GETS_1_FORMULA,
    AGENT_A_GROUP_A_GETS_AT_LEAST_1_FORMULA, AGENT_B_GROUP_A_GETS_AT_LEAST_1_FORMULA, A_GETS_AT_LEAST_1_FORMULA,
    AGENT_A_GROUP_B_GETS_AT_LEAST_1_FORMULA, AGENT_B_GROUP_B_GETS_AT_LEAST_1_FORMULA, A_GETS_AT_LEAST_1_ER,
    B_GETS_AT_LEAST_1_ER, B_GETS_AT_LEAST_1_FORMULA, SECRET_A1, A_GETS_AT_LEAST_1, SECRET_B1, A_GETS_1,
    participant_gets_at_least_x, AGENT_B, AGENT_A
)


class TestVerificationWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, False),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, True),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, True),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, False),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationAuthWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "auth-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, False),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, True),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationDoubleAuthWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "double-auth-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, False),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, True),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationAfterWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "after-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (TIME_REACHES_MAXIMUM_FORMULA, True),
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, False),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, True),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, True),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationAfterAuthWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "after-auth-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (TIME_REACHES_MAXIMUM_FORMULA, True),
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, False),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, True),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationRevealOneWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "reveal-one-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, False),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, True),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, False),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER
    )


class TestVerificationRevealWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "reveal-withdraw.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, False),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, True),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, False),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER,
    )


class TestVerificationAuthRevealAfterWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "auth-reveal-after-withdraw.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (TIME_REACHES_MAXIMUM_FORMULA, True),
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, False),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, True),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, False),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER,
    )


class TestVerificationPutWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "put-withdraw.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_4_FORMULA, False),
        (AF_NOT_A_GETS_4_FORMULA, True),
        (EF_A_GETS_4_FORMULA, True),
        (EF_NOT_A_GETS_4_FORMULA, True),
        (AG_A_GETS_4_FORMULA, False),
        (AG_NOT_A_GETS_4_FORMULA, False),
        (EG_A_GETS_4_FORMULA, False),
        (EG_NOT_A_GETS_4_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_4_FORMULA, True),
        (AGENT_B_GROUP_A_GETS_4_FORMULA, True),
        (PARTICIPANTS_GROUP_A_GETS_4_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_4_ER,
    )


class TestVerificationPutRevealWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "put-reveal-withdraw.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_4_FORMULA, False),
        (AF_NOT_A_GETS_4_FORMULA, True),
        (EF_A_GETS_4_FORMULA, True),
        (EF_NOT_A_GETS_4_FORMULA, True),
        (AG_A_GETS_4_FORMULA, False),
        (AG_NOT_A_GETS_4_FORMULA, False),
        (EG_A_GETS_4_FORMULA, False),
        (EG_NOT_A_GETS_4_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_4_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_4_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_4_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_4_ER,
    )



class TestVerificationSplitWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "split-withdraw.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_1_FORMULA, False),
        (AF_NOT_A_GETS_1_FORMULA, True),
        (EF_A_GETS_1_FORMULA, True),
        (EF_NOT_A_GETS_1_FORMULA, True),
        (AG_A_GETS_1_FORMULA, False),
        (AG_NOT_A_GETS_1_FORMULA, False),
        (EG_A_GETS_1_FORMULA, False),
        (EG_NOT_A_GETS_1_FORMULA, True),
        (AF_B_GETS_1_FORMULA, False),
        (AF_NOT_B_GETS_1_FORMULA, True),
        (EF_B_GETS_1_FORMULA, True),
        (EF_NOT_B_GETS_1_FORMULA, True),
        (AG_B_GETS_1_FORMULA, False),
        (AG_NOT_B_GETS_1_FORMULA, False),
        (EG_B_GETS_1_FORMULA, False),
        (EG_NOT_B_GETS_1_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_1_FORMULA, True),
        (AGENT_B_GROUP_A_GETS_1_FORMULA, True),
        (PARTICIPANTS_GROUP_A_GETS_1_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_1_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_1_FORMULA, True),
        (PARTICIPANTS_GROUP_B_GETS_1_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_1_ER,
        B_GETS_1_ER,
    )



class TestVerificationChoiceWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "choice-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER,
    )


class TestVerificationRevealChoiceWithdraw(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = TESTS_BITML_CONTRACTS_DIR / "reveal-choice-withdraw.rkt"
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_2_FORMULA, False),
        (AF_NOT_A_GETS_2_FORMULA, True),
        (EF_A_GETS_2_FORMULA, True),
        (EF_NOT_A_GETS_2_FORMULA, True),
        (AG_A_GETS_2_FORMULA, False),
        (AG_NOT_A_GETS_2_FORMULA, False),
        (EG_A_GETS_2_FORMULA, False),
        (EG_NOT_A_GETS_2_FORMULA, True),
        (AF_B_GETS_2_FORMULA, False),
        (AF_NOT_B_GETS_2_FORMULA, True),
        (EF_B_GETS_2_FORMULA, True),
        (EF_NOT_B_GETS_2_FORMULA, True),
        (AG_B_GETS_2_FORMULA, False),
        (AG_NOT_B_GETS_2_FORMULA, False),
        (EG_B_GETS_2_FORMULA, False),
        (EG_NOT_B_GETS_2_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (AGENT_A_GROUP_A_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_2_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_2_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_2_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_2_FORMULA, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_2_ER,
        B_GETS_2_ER,
    )


class TestVerificationTimeCommitment(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "timed-commitment.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )

    @staticmethod
    def invariant_a_cannot_recover_funds_if_a1_invalid_formula() -> FormulaType:
        secret_a1_invalid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.INVALID))
        return AGFormula(
            ImpliesFormula(
                secret_a1_invalid,
                NotFormula(DiamondEventuallyFormula(
                    AGENT_A_GROUP,
                    A_GETS_1_FORMULA
                ))
            )
        )

    @staticmethod
    def invariant_b_gets_A_penalty_if_a1_invalid_formula() -> FormulaType:
        secret_a1_invalid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.INVALID))
        return AGFormula(
            ImpliesFormula(
                secret_a1_invalid,
                DiamondEventuallyFormula(
                    AGENT_B_GROUP,
                    B_GETS_1_FORMULA
                )
            )
        )

    @staticmethod
    def invariant_a_recovers_penalty_if_a1_valid_wrong_formula() -> FormulaType:
        secret_a1_valid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.VALID))
        return AGFormula(
            ImpliesFormula(
                secret_a1_valid,
                DiamondEventuallyFormula(
                    AGENT_A_GROUP,
                    A_GETS_1_FORMULA
                )
            )
        )

    @staticmethod
    def invariant_a_recovers_penalty_if_a1_valid_formula() -> FormulaType:
        secret_a1_valid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.VALID))
        time_less_than_one = NotFormula(AtomicFormula(TermNaming.timeout_has_expired(1)))
        agent_not_done = NotFormula(AtomicFormula(TermNaming.agent_done_prop(PARTICIPANT_A)))
        return AGFormula(
            ImpliesFormula(
                AndFormula(secret_a1_valid, AndFormula(time_less_than_one, agent_not_done)),
                DiamondEventuallyFormula(
                    AGENT_A_GROUP,
                    A_GETS_1_FORMULA
                )
            )
        )

    FORMULAE_AND_EXPECTED_OUTCOME = (
        (TIME_REACHES_MAXIMUM_FORMULA, True),
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_1_FORMULA, False),
        (AF_NOT_A_GETS_1_FORMULA, True),
        (EF_A_GETS_1_FORMULA, True),
        (EF_NOT_A_GETS_1_FORMULA, True),
        (AG_A_GETS_1_FORMULA, False),
        (AG_NOT_A_GETS_1_FORMULA, False),
        (EG_A_GETS_1_FORMULA, False),
        (EG_NOT_A_GETS_1_FORMULA, True),
        (AF_B_GETS_1_FORMULA, False),
        (AF_NOT_B_GETS_1_FORMULA, True),
        (EF_B_GETS_1_FORMULA, True),
        (EF_NOT_B_GETS_1_FORMULA, True),
        (AG_B_GETS_1_FORMULA, False),
        (AG_NOT_B_GETS_1_FORMULA, False),
        (EG_B_GETS_1_FORMULA, False),
        (EG_NOT_B_GETS_1_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_1_FORMULA, True),
        (AGENT_B_GROUP_A_GETS_1_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_1_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_1_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_1_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_1_FORMULA, True),
        (invariant_a_cannot_recover_funds_if_a1_invalid_formula(), True),
        (invariant_b_gets_A_penalty_if_a1_invalid_formula(), True),
        (invariant_a_recovers_penalty_if_a1_valid_wrong_formula(), False),
        (invariant_a_recovers_penalty_if_a1_valid_formula(), True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_1_ER,
        B_GETS_1_ER
    )


class TestVerificationMutualTimeCommitment(BaseVerificationTest):
    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "mutual-tc.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )

    @staticmethod
    def invariant_a_cannot_recover_funds_if_a1_invalid_formula() -> FormulaType:
        secret_a1_invalid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.INVALID))
        return AGFormula(
            ImpliesFormula(
                secret_a1_invalid,
                NotFormula(DiamondEventuallyFormula(
                    AGENT_A_GROUP,
                    A_GETS_AT_LEAST_1_FORMULA
                ))
            )
        )

    @staticmethod
    def invariant_a_cannot_recover_funds_if_a1_not_revealed_formula() -> FormulaType:
        secret_a1_revealed = AtomicFormula(TermNaming.public_secret_is_x_prop(SECRET_A1, PublicSecretValues.VALID))
        return AGFormula(
            ImpliesFormula(
                NotFormula(secret_a1_revealed),
                NotFormula(A_GETS_AT_LEAST_1_FORMULA)
            )
        )

    @staticmethod
    def invariant_b_can_recover_funds_if_a_not_reveals_formula() -> FormulaType:
        secret_a1_not_valid = AtomicFormula(TermNaming.private_secret_is_x_prop(SECRET_A1, PrivateSecretValues.INVALID))
        secret_b1_not_revealed = NotFormula(AtomicFormula(TermNaming.public_secret_is_x_prop(SECRET_B1, PublicSecretValues.VALID)))
        t1_expired = AtomicFormula(TermNaming.timeout_has_expired(1))
        return AGFormula(
            ImpliesFormula(
                AndFormula(
                    secret_a1_not_valid,
                    AndFormula(
                        secret_b1_not_revealed,
                        t1_expired
                    )
                ),
                DiamondEventuallyFormula(
                    AGENT_B_GROUP,
                    AndFormula(
                        secret_b1_not_revealed,
                        B_GETS_2_FORMULA
                    )
                )
            )
        )

    FORMULAE_AND_EXPECTED_OUTCOME = (
        (TIME_REACHES_MAXIMUM_FORMULA, True),
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AF_A_GETS_1_FORMULA, False),
        (AF_NOT_A_GETS_1_FORMULA, True),
        (EF_A_GETS_1_FORMULA, True),
        (EF_NOT_A_GETS_1_FORMULA, True),
        (AG_A_GETS_1_FORMULA, False),
        (AG_NOT_A_GETS_1_FORMULA, False),
        (EG_A_GETS_1_FORMULA, False),
        (EG_NOT_A_GETS_1_FORMULA, True),
        (AF_B_GETS_1_FORMULA, False),
        (AF_NOT_B_GETS_1_FORMULA, True),
        (EF_B_GETS_1_FORMULA, True),
        (EF_NOT_B_GETS_1_FORMULA, True),
        (AG_B_GETS_1_FORMULA, False),
        (AG_NOT_B_GETS_1_FORMULA, False),
        (EG_B_GETS_1_FORMULA, False),
        (EG_NOT_B_GETS_1_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, True),
        (AGENT_A_GROUP_A_GETS_1_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_1_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_1_FORMULA, True),
        (AGENT_A_GROUP_B_GETS_1_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_1_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_1_FORMULA, True),
        (invariant_a_cannot_recover_funds_if_a1_invalid_formula(), True),
        (invariant_a_cannot_recover_funds_if_a1_not_revealed_formula(), True),
        (invariant_b_can_recover_funds_if_a_not_reveals_formula(), True)
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_1_ER,
        A_GETS_2_ER,
        A_GETS_AT_LEAST_1_ER,
        B_GETS_1_ER,
        B_GETS_2_ER,
        B_GETS_AT_LEAST_1_ER,
    )


class TestVerificationEscrow(BaseVerificationTest):
    # test-case specific definitions
    PARTICIPANT_M = "M"
    AGENT_M = "Agent_M"
    PARTICIPANT_M_TOTAL_DEPOSITS = "part_M_total_deposits"

    # groups
    AGENT_M_GROUP = "Agent_M"
    AGENT_A_AND_B_GROUP = "Agent_A__Agent_B"
    AGENT_A_AND_M_GROUP = "Agent_A__Agent_M"
    AGENT_B_AND_M_GROUP = "Agent_B__Agent_M"

    # propositions
    M_GETS_1 = "M_gets_1"
    M_GETS_1_FORMULA = AtomicFormula(M_GETS_1)
    M_GETS_1_ER = EvaluationRule(M_GETS_1, participant_gets_x(PARTICIPANT_M, 1))
    A_GETS_10 = "A_gets_10"
    A_GETS_10_FORMULA = AtomicFormula(A_GETS_10)
    A_GETS_10_ER = EvaluationRule(A_GETS_10, participant_gets_x(PARTICIPANT_A, 10))
    A_GETS_9 = "A_gets_9"
    A_GETS_9_FORMULA = AtomicFormula(A_GETS_9)
    A_GETS_9_ER = EvaluationRule(A_GETS_9, participant_gets_x(PARTICIPANT_A, 9))
    A_GETS_AT_LEAST_9 = "A_gets_at_least_9"
    A_GETS_AT_LEAST_9_FORMULA = AtomicFormula(A_GETS_AT_LEAST_9)
    A_GETS_AT_LEAST_9_ER = EvaluationRule(A_GETS_AT_LEAST_9, participant_gets_at_least_x(PARTICIPANT_A, 9))
    B_GETS_10 = "B_gets_10"
    B_GETS_10_FORMULA = AtomicFormula(B_GETS_10)
    B_GETS_10_ER = EvaluationRule(B_GETS_10, participant_gets_x(PARTICIPANT_B, 10))
    B_GETS_9 = "B_gets_9"
    B_GETS_9_FORMULA = AtomicFormula(B_GETS_9)
    B_GETS_9_ER = EvaluationRule(B_GETS_9, participant_gets_x(PARTICIPANT_B, 9))
    B_GETS_AT_LEAST_9 = "B_gets_at_least_9"
    B_GETS_AT_LEAST_9_FORMULA = AtomicFormula(B_GETS_AT_LEAST_9)
    B_GETS_AT_LEAST_9_ER = EvaluationRule(B_GETS_AT_LEAST_9, participant_gets_at_least_x(PARTICIPANT_B, 9))

    # formulae
    AF_M_GETS_1_FORMULA = AFFormula(M_GETS_1_FORMULA)
    AF_NOT_M_GETS_1_FORMULA = AFFormula(NotFormula(M_GETS_1_FORMULA))
    EF_M_GETS_1_FORMULA = EFFormula(M_GETS_1_FORMULA)
    EF_NOT_M_GETS_1_FORMULA = EFFormula(NotFormula(M_GETS_1_FORMULA))
    AG_M_GETS_1_FORMULA = AGFormula(M_GETS_1_FORMULA)
    AG_NOT_M_GETS_1_FORMULA = AGFormula(NotFormula(M_GETS_1_FORMULA))
    EG_M_GETS_1_FORMULA = EGFormula(M_GETS_1_FORMULA)
    EG_NOT_M_GETS_1_FORMULA = EGFormula(NotFormula(M_GETS_1_FORMULA))
    CONTRACT_IS_LIQUID_FORMULA_FOR_M = _get_contract_is_liquid_formula_for_group(AGENT_M_GROUP)
    CONTRACT_IS_LIQUID_FORMULA_FOR_A_AND_M = _get_contract_is_liquid_formula_for_group(AGENT_A_AND_M_GROUP)
    CONTRACT_IS_LIQUID_FORMULA_FOR_B_AND_M = _get_contract_is_liquid_formula_for_group(AGENT_B_AND_M_GROUP)
    CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_M = _get_contract_is_liquid_formula_after_initialization_for_group(AGENT_M_GROUP)
    CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A_AND_M = _get_contract_is_liquid_formula_after_initialization_for_group(AGENT_A_AND_M_GROUP)
    CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B_AND_M = _get_contract_is_liquid_formula_after_initialization_for_group(AGENT_B_AND_M_GROUP)

    # A gets 9
    AGENT_A_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_9_FORMULA)
    AGENT_B_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_9_FORMULA)
    AGENT_M_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, A_GETS_9_FORMULA)
    AGENT_A_AND_B_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, A_GETS_9_FORMULA)
    AGENT_A_AND_M_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, A_GETS_9_FORMULA)
    AGENT_B_AND_M_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, A_GETS_9_FORMULA)
    PARTICIPANTS_GROUP_A_GETS_9_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_9_FORMULA)

    # B gets 9
    AGENT_A_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_9_FORMULA)
    AGENT_B_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_9_FORMULA)
    AGENT_M_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, B_GETS_9_FORMULA)
    AGENT_A_AND_B_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, B_GETS_9_FORMULA)
    AGENT_A_AND_M_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, B_GETS_9_FORMULA)
    AGENT_B_AND_M_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, B_GETS_9_FORMULA)
    PARTICIPANTS_GROUP_B_GETS_9_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_9_FORMULA)

    # A gets at least 9
    AGENT_A_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    AGENT_B_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    AGENT_M_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    AGENT_A_AND_B_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    AGENT_A_AND_M_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    AGENT_B_AND_M_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, A_GETS_AT_LEAST_9_FORMULA)
    PARTICIPANTS_GROUP_A_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_AT_LEAST_9_FORMULA)

    # B gets at least 9
    AGENT_A_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    AGENT_B_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    AGENT_M_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    AGENT_A_AND_B_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    AGENT_A_AND_M_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    AGENT_B_AND_M_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, B_GETS_AT_LEAST_9_FORMULA)
    PARTICIPANTS_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_9_FORMULA)

    # A gets 10
    AGENT_A_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_10_FORMULA)
    AGENT_B_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_10_FORMULA)
    AGENT_M_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, A_GETS_10_FORMULA)
    AGENT_A_AND_B_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, A_GETS_10_FORMULA)
    AGENT_A_AND_M_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, A_GETS_10_FORMULA)
    AGENT_B_AND_M_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, A_GETS_10_FORMULA)
    PARTICIPANTS_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_10_FORMULA)

    # B gets 10
    AGENT_A_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_10_FORMULA)
    AGENT_B_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_10_FORMULA)
    AGENT_M_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_M_GROUP, B_GETS_10_FORMULA)
    AGENT_A_AND_B_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_B_GROUP, B_GETS_10_FORMULA)
    AGENT_A_AND_M_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_M_GROUP, B_GETS_10_FORMULA)
    AGENT_B_AND_M_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_B_AND_M_GROUP, B_GETS_10_FORMULA)
    PARTICIPANTS_GROUP_B_GETS_10_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_10_FORMULA)

    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "escrow.rkt"
    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )

    # AG((status_node_6_split_is_executed | status_node_11_split_is_executed)
    #     -> <M>F(part_M_total_deposits_is_at_least_1))
    PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1_PROP = "part_M_total_deposits_is_at_least_1"
    PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1 = AtomicFormula(PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1_PROP)
    PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1_ER = EvaluationRule(
        PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1_PROP,
        GreaterThanOrEqual(EnvironmentIdAtom(PARTICIPANT_M_TOTAL_DEPOSITS), IntAtom(1))
    )
    IF_RESOLVE_BRANCH_TAKEN_THEN_MEDIATOR_CAN_GET_COMMISSION = AGFormula(
        ImpliesFormula(
            AtomicFormula("node_6_split_is_executed") | AtomicFormula("node_11_split_is_executed"),
            DiamondEventuallyFormula(AGENT_M, PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1),
        )
    )

    # AG( ( (status_node_6_split_is_executed | status_node_11_split_is_executed)
    #       & !node_3_withdraw_is_authorized_by_M
    #       & !node_4_withdraw_is_authorized_by_M
    #       & !node_8_withdraw_is_authorized_by_M
    #       & !node_9_withdraw_is_authorized_by_M)
    #       -> (<M>F(part_A_total_deposits_is_at_least_9)
    #           <M>F(part_B_total_deposits_is_at_least_9))
    # )
    IF_RESOLVE_BRANCH_TAKEN_THEN_MEDIATOR_CAN_GIVE_FUNDS_TO_A_OR_B = AGFormula(
        ImpliesFormula(
            (AtomicFormula("node_6_split_is_executed") | AtomicFormula("node_11_split_is_executed"))
            & ~AtomicFormula("node_3_withdraw_is_authorized_by_M")
            & ~AtomicFormula("node_4_withdraw_is_authorized_by_M")
            & ~AtomicFormula("node_8_withdraw_is_authorized_by_M")
            & ~AtomicFormula("node_9_withdraw_is_authorized_by_M"),
            AndFormula(
                DiamondEventuallyFormula(AGENT_M, A_GETS_AT_LEAST_9_FORMULA),
                DiamondEventuallyFormula(AGENT_M, B_GETS_AT_LEAST_9_FORMULA),
            )
        )
    )

    FORMULAE_AND_EXPECTED_OUTCOME = (
        (EF_FUNDS_IS_ZERO, True),
        (AF_FUNDS_IS_ZERO, False),
        (AFFormula(A_GETS_9_FORMULA), False),
        (AFFormula(~A_GETS_9_FORMULA), True),
        (EFFormula(A_GETS_9_FORMULA), True),
        (EFFormula(~A_GETS_9_FORMULA), True),
        (AGFormula(A_GETS_9_FORMULA), False),
        (AGFormula(~A_GETS_9_FORMULA), False),
        (EGFormula(A_GETS_9_FORMULA), False),
        (EGFormula(~A_GETS_9_FORMULA), True),
        (AFFormula(A_GETS_10_FORMULA), False),
        (AFFormula(~A_GETS_10_FORMULA), True),
        (EFFormula(A_GETS_10_FORMULA), True),
        (EFFormula(~A_GETS_10_FORMULA), True),
        (AGFormula(A_GETS_10_FORMULA), False),
        (AGFormula(~A_GETS_10_FORMULA), False),
        (EGFormula(A_GETS_10_FORMULA), False),
        (EGFormula(~A_GETS_10_FORMULA), True),
        (AFFormula(B_GETS_9_FORMULA), False),
        (AFFormula(~B_GETS_9_FORMULA), True),
        (EFFormula(B_GETS_9_FORMULA), True),
        (EFFormula(~B_GETS_9_FORMULA), True),
        (AGFormula(B_GETS_9_FORMULA), False),
        (AGFormula(~B_GETS_9_FORMULA), False),
        (EGFormula(B_GETS_9_FORMULA), False),
        (EGFormula(~B_GETS_9_FORMULA), True),
        (AFFormula(B_GETS_10_FORMULA), False),
        (AFFormula(~B_GETS_10_FORMULA), True),
        (EFFormula(B_GETS_10_FORMULA), True),
        (EFFormula(~B_GETS_10_FORMULA), True),
        (AGFormula(B_GETS_10_FORMULA), False),
        (AGFormula(~B_GETS_10_FORMULA), False),
        (EGFormula(B_GETS_10_FORMULA), False),
        (EGFormula(~B_GETS_10_FORMULA), True),
        (AF_M_GETS_1_FORMULA, False),
        (AF_NOT_M_GETS_1_FORMULA, True),
        (EF_M_GETS_1_FORMULA, True),
        (EF_NOT_M_GETS_1_FORMULA, True),
        (AG_M_GETS_1_FORMULA, False),
        (AG_NOT_M_GETS_1_FORMULA, False),
        (EG_M_GETS_1_FORMULA, False),
        (EG_NOT_M_GETS_1_FORMULA, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_M, False),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A_AND_M, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B_AND_M, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_M, False),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A_AND_M, True),
        (CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B_AND_M, True),

        # check A gets 9
        (AGENT_A_GROUP_A_GETS_9_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_9_FORMULA, False),
        (AGENT_M_GROUP_A_GETS_9_FORMULA, False),
        (AGENT_A_AND_B_GROUP_A_GETS_9_FORMULA, False),
        (AGENT_A_AND_M_GROUP_A_GETS_9_FORMULA, False),
        (AGENT_B_AND_M_GROUP_A_GETS_9_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_9_FORMULA, True),

        # B gets 9
        (AGENT_A_GROUP_B_GETS_9_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_9_FORMULA, False),
        (AGENT_M_GROUP_B_GETS_9_FORMULA, False),
        (AGENT_A_AND_B_GROUP_B_GETS_9_FORMULA, False),
        (AGENT_A_AND_M_GROUP_B_GETS_9_FORMULA, False),
        (AGENT_B_AND_M_GROUP_B_GETS_9_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_9_FORMULA, True),

        # A gets at least 9
        (AGENT_A_GROUP_A_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_M_GROUP_A_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_A_AND_B_GROUP_A_GETS_AT_LEAST_9_FORMULA, True),
        (AGENT_A_AND_M_GROUP_A_GETS_AT_LEAST_9_FORMULA, True),
        (AGENT_B_AND_M_GROUP_A_GETS_AT_LEAST_9_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_AT_LEAST_9_FORMULA, True),

        # B gets at least 9
        (AGENT_A_GROUP_B_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_M_GROUP_B_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_A_AND_B_GROUP_B_GETS_AT_LEAST_9_FORMULA, True),
        (AGENT_A_AND_M_GROUP_B_GETS_AT_LEAST_9_FORMULA, False),
        (AGENT_B_AND_M_GROUP_B_GETS_AT_LEAST_9_FORMULA, True),
        (PARTICIPANTS_GROUP_B_GETS_AT_LEAST_9_FORMULA, True),

        # A gets 10
        (AGENT_A_GROUP_A_GETS_10_FORMULA, False),
        (AGENT_B_GROUP_A_GETS_10_FORMULA, False),
        (AGENT_M_GROUP_A_GETS_10_FORMULA, False),
        (AGENT_A_AND_B_GROUP_A_GETS_10_FORMULA, True),
        (AGENT_A_AND_M_GROUP_A_GETS_10_FORMULA, False),
        (AGENT_B_AND_M_GROUP_A_GETS_10_FORMULA, False),
        (PARTICIPANTS_GROUP_A_GETS_10_FORMULA, True),

        # B gets 10
        (AGENT_A_GROUP_B_GETS_10_FORMULA, False),
        (AGENT_B_GROUP_B_GETS_10_FORMULA, False),
        (AGENT_M_GROUP_B_GETS_10_FORMULA, False),
        (AGENT_A_AND_B_GROUP_B_GETS_10_FORMULA, True),
        (AGENT_A_AND_M_GROUP_B_GETS_10_FORMULA, False),
        (AGENT_B_AND_M_GROUP_B_GETS_10_FORMULA, False),
        (PARTICIPANTS_GROUP_B_GETS_10_FORMULA, True),

        (IF_RESOLVE_BRANCH_TAKEN_THEN_MEDIATOR_CAN_GET_COMMISSION, True),
        (IF_RESOLVE_BRANCH_TAKEN_THEN_MEDIATOR_CAN_GIVE_FUNDS_TO_A_OR_B, True),
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_1_ER,
        A_GETS_2_ER,
        B_GETS_1_ER,
        B_GETS_2_ER,
        A_GETS_9_ER,
        B_GETS_9_ER,
        A_GETS_AT_LEAST_9_ER,
        B_GETS_AT_LEAST_9_ER,
        A_GETS_10_ER,
        B_GETS_10_ER,
        M_GETS_1_ER,
        PART_M_TOTAL_DEPOSITS_IS_AT_LEAST_1_ER
    )


class TestVerificationZeroCouponBond(BaseVerificationTest):
    AGENT_G = "Agent_G"
    AGENT_A_AND_AGENT_G_GROUP = "Agent_A__Agent_G"
    PATH_TO_CONTRACT_FILE = EXAMPLES_BITML_CONTRACTS_DIR / "zero-coupon-bond.rkt"

    A_GETS_10 = "A_gets_10"
    A_GETS_10_FORMULA = AtomicFormula(A_GETS_10)
    A_GETS_10_ER = EvaluationRule(A_GETS_10, participant_gets_x(PARTICIPANT_A, 10))
    B_GETS_AT_LEAST_9 = "B_gets_at_least_9"
    B_GETS_AT_LEAST_9_FORMULA = AtomicFormula(B_GETS_AT_LEAST_9)
    B_GETS_AT_LEAST_9_ER = EvaluationRule(B_GETS_AT_LEAST_9, participant_gets_at_least_x(PARTICIPANT_B, 9))

    CONTRACT_IS_LIQUID_FORMULA_FOR_G = _get_contract_is_liquid_formula_for_group(AGENT_G)
    AGENT_A_AND_G_GROUP_A_GETS_10_FORMULA = DiamondEventuallyFormula(AGENT_A_AND_AGENT_G_GROUP, A_GETS_10_FORMULA)
    AGENT_B_GROUP_B_GETS_AT_LEAST_9_FORMULA = DiamondEventuallyFormula(AGENT_B, B_GETS_AT_LEAST_9_FORMULA)
    CANNOT_PREVENT_A_FROM_WITHDRAWING_FUNDS = AndFormula(
        ~DiamondEventuallyFormula(AGENT_B, ~DiamondEventuallyFormula(AGENT_A, A_GETS_10_FORMULA)),
        ~DiamondEventuallyFormula(AGENT_B, ~DiamondEventuallyFormula(AGENT_A, A_GETS_10_FORMULA)),
    )

    override_mcmas_options_kwargs: dict = dict(
        atlk=1
    )
    FORMULAE_AND_EXPECTED_OUTCOME = (
        (CONTRACT_IS_LIQUID_FORMULA_FOR_A, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_B, True),
        (CONTRACT_IS_LIQUID_FORMULA_FOR_G, True),
        (CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE, True),
        (AGENT_A_AND_G_GROUP_A_GETS_10_FORMULA, True),
        (AGENT_B_GROUP_B_GETS_AT_LEAST_9_FORMULA, True),
        (CANNOT_PREVENT_A_FROM_WITHDRAWING_FUNDS, True)
    )
    EVALUATION_RULES = (
        CONTRACT_FUNDS_ARE_ZERO_ER,
        A_GETS_10_ER,
        B_GETS_AT_LEAST_9_ER
    )
