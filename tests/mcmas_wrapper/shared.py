from functools import reduce

from bitml2mcmas.bitml.custom_types import TermString
from bitml2mcmas.compiler._private.terms import (
    DELAY,
    INITIALIZE_CONTRACT,
    NOP,
    TermNaming, CONTRACT_FUNDS, PARTICIPANTS_GROUP, TIME_REACHES_MAXIMUM, CONTRACT_IS_INITIALIZED,
)
from bitml2mcmas.mcmas.ast import EvaluationRule
from bitml2mcmas.mcmas.boolcond import EqualTo, EnvironmentIdAtom, IntAtom, BooleanCondition, GreaterThanOrEqual, IdAtom
from bitml2mcmas.mcmas.formula import AtomicFormula, AFFormula, OrFormula, NotFormula, AGFormula, FormulaType, \
    DiamondEventuallyFormula, AndFormula, EFFormula, EGFormula, ImpliesFormula
from tests.test_bitml.test_validation import SECRET_B_ID


def _add_action_prefix(a: str):
    return TermNaming.action_with_prefix(a)


# some usual variable names and terms
TRUE_STR = "true"
FALSE_STR = "false"
PARTICIPANT_A = "A"
PARTICIPANT_B = "B"
AGENT_A = TermNaming.agent_name_from_participant_name(PARTICIPANT_A)
AGENT_B = TermNaming.agent_name_from_participant_name(PARTICIPANT_B)
PARTICIPANT_A_IS_DONE = TermNaming.agent_done_varname(PARTICIPANT_A)
PARTICIPANT_A_TOTAL_DEPOSITS = TermNaming.participant_total_deposits(PARTICIPANT_A)
PARTICIPANT_B_IS_DONE = TermNaming.agent_done_varname(PARTICIPANT_B)
PARTICIPANT_B_TOTAL_DEPOSITS = TermNaming.participant_total_deposits(PARTICIPANT_B)

# scheduling and time progression
SCHEDULE_PARTICIPANT_A = TermNaming.scheduling_action_from_participant_id(PARTICIPANT_A)
SCHEDULE_PARTICIPANT_B = TermNaming.scheduling_action_from_participant_id(PARTICIPANT_B)
TIME = "time"


# volatile deposits
TXA1 = "txa1"
TXB1 = "txb1"
SPENT_DEPOSIT_TXA1 = TermNaming.deposit_spent_var_from_id(TXA1)
SPENT_DEPOSIT_TXB1 = TermNaming.deposit_spent_var_from_id(TXB1)


# secret handling
SECRET_A1 = "a1"
SECRET_B1 = "b1"
PUBLIC_SECRET_A1 = TermNaming.secret_name_with_prefix_public(SECRET_A1)
PUBLIC_SECRET_B1 = TermNaming.secret_name_with_prefix_public(SECRET_B1)
PRIVATE_SECRET_A1 = TermNaming.secret_name_with_prefix_private(SECRET_A1)
PRIVATE_SECRET_B1 = TermNaming.secret_name_with_prefix_private(SECRET_B1)
COMMIT_VALID_SECRET_A1 = TermNaming.valid_commitment_action(SECRET_A1)
COMMIT_INVALID_SECRET_A1 = TermNaming.invalid_commitment_action(SECRET_A1)
COMMIT_VALID_SECRET_B1 = TermNaming.valid_commitment_action(SECRET_B1)
COMMIT_INVALID_SECRET_B1 = TermNaming.invalid_commitment_action(SECRET_B1)
REVEAL_SECRET_A1 = TermNaming.reveal_action(SECRET_A1)
REVEAL_SECRET_B1 = TermNaming.reveal_action(SECRET_B1)

ACTION_NOP = _add_action_prefix(NOP)
ACTION_DELAY = _add_action_prefix(DELAY)
ACTION_SCHEDULE_PARTICIPANT_A = _add_action_prefix(SCHEDULE_PARTICIPANT_A)
ACTION_SCHEDULE_PARTICIPANT_B = _add_action_prefix(SCHEDULE_PARTICIPANT_B)
ACTION_INITIALIZE_CONTRACT = _add_action_prefix(INITIALIZE_CONTRACT)
ACTION_COMMIT_VALID_SECRET_A1 = _add_action_prefix(COMMIT_VALID_SECRET_A1)
ACTION_COMMIT_INVALID_SECRET_A1 = _add_action_prefix(COMMIT_INVALID_SECRET_A1)
ACTION_COMMIT_VALID_SECRET_B1 = _add_action_prefix(COMMIT_VALID_SECRET_B1)
ACTION_COMMIT_INVALID_SECRET_B1 = _add_action_prefix(COMMIT_INVALID_SECRET_B1)
ACTION_REVEAL_SECRET_A1 = _add_action_prefix(REVEAL_SECRET_A1)
ACTION_REVEAL_SECRET_B1 = _add_action_prefix(REVEAL_SECRET_B1)


# verification terms
AGENT_A_GROUP = "Agent_A"
AGENT_B_GROUP = "Agent_B"

# evaluation rules
CONTRACT_FUNDS_ARE_ZERO = "contract_funds_are_zero"
CONTRACT_FUNDS_ARE_ZERO_COND = EqualTo(EnvironmentIdAtom(CONTRACT_FUNDS), IntAtom(0))
CONTRACT_FUNDS_ARE_ZERO_ER = EvaluationRule(CONTRACT_FUNDS_ARE_ZERO, CONTRACT_FUNDS_ARE_ZERO_COND)


# formulas
def _get_contract_is_liquid_formula_for_group(group_id: str) -> FormulaType:
    return DiamondEventuallyFormula(group_id, AtomicFormula(CONTRACT_FUNDS_ARE_ZERO))


# formulas
def _get_contract_is_liquid_formula_after_initialization_for_group(group_id: str) -> FormulaType:
    return AGFormula(
        ImpliesFormula(
            AtomicFormula(CONTRACT_IS_INITIALIZED),
            DiamondEventuallyFormula(group_id, AtomicFormula(CONTRACT_FUNDS_ARE_ZERO))
    ))


def participant_gets_x(participant_id: str, amount: int) -> BooleanCondition:
    total_deposit_varname = TermNaming.participant_total_deposits(participant_id)
    return EqualTo(EnvironmentIdAtom(total_deposit_varname), IntAtom(amount))


def participant_gets_at_least_x(
    participant_id: str, amount: int
) -> BooleanCondition:
    total_deposit_varname = TermNaming.participant_total_deposits(participant_id)
    return GreaterThanOrEqual(
        EnvironmentIdAtom(total_deposit_varname), IntAtom(amount)
    )


TIME_REACHES_MAXIMUM_FORMULA = AFFormula(AtomicFormula(TIME_REACHES_MAXIMUM))


EF_FUNDS_IS_ZERO = EFFormula(AtomicFormula(CONTRACT_FUNDS_ARE_ZERO))
AF_FUNDS_IS_ZERO = AFFormula(AtomicFormula(CONTRACT_FUNDS_ARE_ZERO))


CONTRACT_IS_LIQUID_FORMULA_FOR_A = _get_contract_is_liquid_formula_for_group(AGENT_A_GROUP)
CONTRACT_IS_LIQUID_FORMULA_FOR_B = _get_contract_is_liquid_formula_for_group(AGENT_B_GROUP)
CONTRACT_IS_LIQUID_FORMULA_COOPERATIVE = _get_contract_is_liquid_formula_for_group(PARTICIPANTS_GROUP)
CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_A = _get_contract_is_liquid_formula_after_initialization_for_group(AGENT_A_GROUP)
CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_FOR_B = _get_contract_is_liquid_formula_after_initialization_for_group(AGENT_B_GROUP)
CONTRACT_IS_LIQUID_AFTER_INITIALIZATION_FORMULA_COOPERATIVE = _get_contract_is_liquid_formula_after_initialization_for_group(PARTICIPANTS_GROUP)

A_GETS_1 = "A_gets_1"
A_GETS_1_FORMULA = AtomicFormula(A_GETS_1)
A_GETS_1_ER = EvaluationRule(A_GETS_1, participant_gets_x(PARTICIPANT_A, 1))
AF_A_GETS_1_FORMULA = AFFormula(A_GETS_1_FORMULA)
AF_NOT_A_GETS_1_FORMULA = AFFormula(NotFormula(A_GETS_1_FORMULA))
EF_A_GETS_1_FORMULA = EFFormula(A_GETS_1_FORMULA)
EF_NOT_A_GETS_1_FORMULA = EFFormula(NotFormula(A_GETS_1_FORMULA))
AG_A_GETS_1_FORMULA = AGFormula(A_GETS_1_FORMULA)
AG_NOT_A_GETS_1_FORMULA = AGFormula(NotFormula(A_GETS_1_FORMULA))
EG_A_GETS_1_FORMULA = EGFormula(A_GETS_1_FORMULA)
EG_NOT_A_GETS_1_FORMULA = EGFormula(NotFormula(A_GETS_1_FORMULA))
AGENT_A_GROUP_A_GETS_1_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_1_FORMULA)
AGENT_B_GROUP_A_GETS_1_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_1_FORMULA)
PARTICIPANTS_GROUP_A_GETS_1_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_1_FORMULA)

A_GETS_2 = "A_gets_2"
A_GETS_2_FORMULA = AtomicFormula(A_GETS_2)
A_GETS_2_ER = EvaluationRule(A_GETS_2, participant_gets_x(PARTICIPANT_A, 2))
AF_A_GETS_2_FORMULA = AFFormula(A_GETS_2_FORMULA)
AF_NOT_A_GETS_2_FORMULA = AFFormula(NotFormula(A_GETS_2_FORMULA))
EF_A_GETS_2_FORMULA = EFFormula(A_GETS_2_FORMULA)
EF_NOT_A_GETS_2_FORMULA = EFFormula(NotFormula(A_GETS_2_FORMULA))
AG_A_GETS_2_FORMULA = AGFormula(A_GETS_2_FORMULA)
AG_NOT_A_GETS_2_FORMULA = AGFormula(NotFormula(A_GETS_2_FORMULA))
EG_A_GETS_2_FORMULA = EGFormula(A_GETS_2_FORMULA)
EG_NOT_A_GETS_2_FORMULA = EGFormula(NotFormula(A_GETS_2_FORMULA))
AGENT_A_GROUP_A_GETS_2_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_2_FORMULA)
AGENT_B_GROUP_A_GETS_2_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_2_FORMULA)
PARTICIPANTS_GROUP_A_GETS_2_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_2_FORMULA)

A_GETS_4 = "A_gets_4"
A_GETS_4_FORMULA = AtomicFormula(A_GETS_4)
A_GETS_4_ER = EvaluationRule(A_GETS_4, participant_gets_x(PARTICIPANT_A, 4))
AF_A_GETS_4_FORMULA = AFFormula(A_GETS_4_FORMULA)
AF_NOT_A_GETS_4_FORMULA = AFFormula(NotFormula(A_GETS_4_FORMULA))
EF_A_GETS_4_FORMULA = EFFormula(A_GETS_4_FORMULA)
EF_NOT_A_GETS_4_FORMULA = EFFormula(NotFormula(A_GETS_4_FORMULA))
AG_A_GETS_4_FORMULA = AGFormula(A_GETS_4_FORMULA)
AG_NOT_A_GETS_4_FORMULA = AGFormula(NotFormula(A_GETS_4_FORMULA))
EG_A_GETS_4_FORMULA = EGFormula(A_GETS_4_FORMULA)
EG_NOT_A_GETS_4_FORMULA = EGFormula(NotFormula(A_GETS_4_FORMULA))
AGENT_A_GROUP_A_GETS_4_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_4_FORMULA)
AGENT_B_GROUP_A_GETS_4_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_4_FORMULA)
PARTICIPANTS_GROUP_A_GETS_4_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_4_FORMULA)

B_GETS_1 = "B_gets_1"
B_GETS_1_FORMULA = AtomicFormula(B_GETS_1)
B_GETS_1_ER = EvaluationRule(B_GETS_1, participant_gets_x(PARTICIPANT_B, 1))
AF_B_GETS_1_FORMULA = AFFormula(B_GETS_1_FORMULA)
AF_NOT_B_GETS_1_FORMULA = AFFormula(NotFormula(B_GETS_1_FORMULA))
EF_B_GETS_1_FORMULA = EFFormula(B_GETS_1_FORMULA)
EF_NOT_B_GETS_1_FORMULA = EFFormula(NotFormula(B_GETS_1_FORMULA))
AG_B_GETS_1_FORMULA = AGFormula(B_GETS_1_FORMULA)
AG_NOT_B_GETS_1_FORMULA = AGFormula(NotFormula(B_GETS_1_FORMULA))
EG_B_GETS_1_FORMULA = EGFormula(B_GETS_1_FORMULA)
EG_NOT_B_GETS_1_FORMULA = EGFormula(NotFormula(B_GETS_1_FORMULA))
AGENT_A_GROUP_B_GETS_1_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_1_FORMULA)
AGENT_B_GROUP_B_GETS_1_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_1_FORMULA)
PARTICIPANTS_GROUP_B_GETS_1_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_1_FORMULA)

B_GETS_2 = "B_gets_2"
B_GETS_2_FORMULA = AtomicFormula(B_GETS_2)
B_GETS_2_ER = EvaluationRule(B_GETS_2, participant_gets_x(PARTICIPANT_B, 2))
AF_B_GETS_2_FORMULA = AFFormula(B_GETS_2_FORMULA)
AF_NOT_B_GETS_2_FORMULA = AFFormula(NotFormula(B_GETS_2_FORMULA))
EF_B_GETS_2_FORMULA = EFFormula(B_GETS_2_FORMULA)
EF_NOT_B_GETS_2_FORMULA = EFFormula(NotFormula(B_GETS_2_FORMULA))
AG_B_GETS_2_FORMULA = AGFormula(B_GETS_2_FORMULA)
AG_NOT_B_GETS_2_FORMULA = AGFormula(NotFormula(B_GETS_2_FORMULA))
EG_B_GETS_2_FORMULA = EGFormula(B_GETS_2_FORMULA)
EG_NOT_B_GETS_2_FORMULA = EGFormula(NotFormula(B_GETS_2_FORMULA))
AGENT_A_GROUP_B_GETS_2_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_2_FORMULA)
AGENT_B_GROUP_B_GETS_2_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_2_FORMULA)
PARTICIPANTS_GROUP_B_GETS_2_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_2_FORMULA)


A_GETS_AT_LEAST_1 = "A_gets_at_least_1"
A_GETS_AT_LEAST_1_FORMULA = AtomicFormula(A_GETS_AT_LEAST_1)
A_GETS_AT_LEAST_1_ER = EvaluationRule(A_GETS_AT_LEAST_1, participant_gets_at_least_x(PARTICIPANT_A, 1))
AGENT_A_GROUP_A_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, A_GETS_AT_LEAST_1_FORMULA)
AGENT_B_GROUP_A_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, A_GETS_AT_LEAST_1_FORMULA)
PARTICIPANTS_GROUP_A_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, A_GETS_AT_LEAST_1_FORMULA)

B_GETS_AT_LEAST_1 = "B_gets_at_least_1"
B_GETS_AT_LEAST_1_FORMULA = AtomicFormula(B_GETS_AT_LEAST_1)
B_GETS_AT_LEAST_1_ER = EvaluationRule(B_GETS_AT_LEAST_1, participant_gets_at_least_x(PARTICIPANT_B, 1))
AGENT_A_GROUP_B_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(AGENT_A_GROUP, B_GETS_AT_LEAST_1_FORMULA)
AGENT_B_GROUP_B_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(AGENT_B_GROUP, B_GETS_AT_LEAST_1_FORMULA)
PARTICIPANTS_GROUP_B_GETS_AT_LEAST_1_FORMULA = DiamondEventuallyFormula(PARTICIPANTS_GROUP, B_GETS_AT_LEAST_1_FORMULA)
