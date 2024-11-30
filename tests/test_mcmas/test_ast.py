# This file is part of bitml2mcmas.
# Copyright 2024 Marco Favorito
#
# bitml2mcmas is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# bitml2mcmas is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with bitml2mcmas.  If not, see <https://www.gnu.org/licenses/>.
#

"""Tests for the mcmas.ast module."""

from bitml2mcmas.mcmas.ast import (
    Agent,
    BooleanVarType,
    Effect,
    EnumVarType,
    Environment,
    EvaluationRule,
    EvolutionRule,
    Group,
    InterpretedSystem,
    Protocol,
    ProtocolRule,
    Semantics,
    VarDefinition,
)
from bitml2mcmas.mcmas.boolcond import (
    ActionEqualToConstraint,
    AgentActionEqualToConstraint,
    AttributeIdAtom,
    EnvironmentActionEqualToConstraint,
    EnvironmentIdAtom,
    EqualTo,
    FalseBoolValue,
    IdAtom,
    TrueBoolValue,
)
from bitml2mcmas.mcmas.formula import AFFormula, AtomicFormula
from bitml2mcmas.mcmas.to_string import interpreted_system_to_string


def test_bit_transmission_problem() -> None:
    bit = "bit"
    ack = "ack"
    S, R, SR, none = "S", "R", "SR", "none"
    b0, b1, nothing, sb0, sb1 = "b0", "b1", "nothing", "sb0", "sb1"
    empty, r0, r1 = "empty", "r0", "r1"
    sendack = "sendack"
    Receiver, Sender = "Receiver", "Sender"

    # environment definition
    state = "state"
    env_state_vardef = VarDefinition(state, EnumVarType({S, R, SR, none}))
    env_actions = {S, R, SR, none}

    state_equal_to_s = EqualTo(IdAtom(state), IdAtom(S))
    state_equal_to_r = EqualTo(IdAtom(state), IdAtom(R))
    state_equal_to_sr = EqualTo(IdAtom(state), IdAtom(SR))
    state_equal_to_none = EqualTo(IdAtom(state), IdAtom(none))

    env_protocol_rule_s = ProtocolRule(state_equal_to_s, env_actions)
    env_protocol_rule_r = ProtocolRule(state_equal_to_r, env_actions)
    env_protocol_rule_sr = ProtocolRule(state_equal_to_sr, env_actions)
    env_protocol_rule_none = ProtocolRule(state_equal_to_none, env_actions)
    env_protocol = Protocol(
        [
            env_protocol_rule_s,
            env_protocol_rule_r,
            env_protocol_rule_sr,
            env_protocol_rule_none,
        ],
        other_rule=None,
    )

    env_evolution_rule_s = EvolutionRule(
        [Effect(state, IdAtom(S))], ActionEqualToConstraint(S)
    )
    env_evolution_rule_r = EvolutionRule(
        [Effect(state, IdAtom(R))], ActionEqualToConstraint(R)
    )
    env_evolution_rule_sr = EvolutionRule(
        [Effect(state, IdAtom(SR))], ActionEqualToConstraint(SR)
    )
    env_evolution_rule_none = EvolutionRule(
        [Effect(state, IdAtom(none))], ActionEqualToConstraint(none)
    )
    env_evolutions = [
        env_evolution_rule_s,
        env_evolution_rule_r,
        env_evolution_rule_sr,
        env_evolution_rule_none,
    ]

    env_agent = Environment(
        obs_var_definitions=None,
        env_var_definitions=[env_state_vardef],
        env_red_definitions=None,
        env_action_definitions=env_actions,
        env_protocol_definition=env_protocol,
        env_evolution_definition=env_evolutions,
    )

    # sender definition
    sender_bit_vardef = VarDefinition(bit, EnumVarType({b0, b1}))
    sender_ack_vardef = VarDefinition(ack, BooleanVarType())
    sender_vars = [sender_bit_vardef, sender_ack_vardef]
    sender_actions = {sb0, sb1, nothing}

    bit_equal_to_b0 = EqualTo(IdAtom(bit), IdAtom(b0))
    bit_equal_to_b1 = EqualTo(IdAtom(bit), IdAtom(b1))
    ack_is_false = EqualTo(IdAtom(ack), FalseBoolValue())
    ack_is_true = EqualTo(IdAtom(ack), TrueBoolValue())
    sender_protocol_rule_1 = ProtocolRule(bit_equal_to_b0 & ack_is_false, {sb0})
    sender_protocol_rule_2 = ProtocolRule(bit_equal_to_b1 & ack_is_false, {sb1})
    sender_protocol_rule_3 = ProtocolRule(ack_is_true, {nothing})
    sender_protocol = Protocol(
        [
            sender_protocol_rule_1,
            sender_protocol_rule_2,
            sender_protocol_rule_3,
        ],
        other_rule=None,
    )

    effect_ack_to_true = Effect(ack, TrueBoolValue())
    ack_to_true_condition = ack_is_false & (
        (
            AgentActionEqualToConstraint(Receiver, sendack)
            & EnvironmentActionEqualToConstraint(SR)
        )
        | (
            AgentActionEqualToConstraint(Receiver, sendack)
            & EnvironmentActionEqualToConstraint(R)
        )
    )
    sender_evolution_rules = [
        EvolutionRule([effect_ack_to_true], ack_to_true_condition)
    ]

    sender_agent = Agent(
        name=Sender,
        lobs_var_definitions=None,
        agent_var_definitions=sender_vars,
        agent_red_definitions=None,
        agent_action_definitions=sender_actions,
        agent_protocol_definition=sender_protocol,
        agent_evolution_definition=sender_evolution_rules,
    )

    # receiver definition
    receiver_state_vardef = VarDefinition(state, EnumVarType({empty, r0, r1}))
    receiver_vars = [receiver_state_vardef]
    receiver_actions = {nothing, sendack}

    state_equal_to_empty = EqualTo(IdAtom(state), IdAtom(empty))
    state_equal_to_r0 = EqualTo(IdAtom(state), IdAtom(r0))
    state_equal_to_r1 = EqualTo(IdAtom(state), IdAtom(r1))

    receiver_protocol_rule_1 = ProtocolRule(state_equal_to_empty, {nothing})
    receiver_protocol_rule_2 = ProtocolRule(
        state_equal_to_r0 | state_equal_to_r1, {sendack}
    )
    receiver_protocol = Protocol(
        rules=[receiver_protocol_rule_1, receiver_protocol_rule_2], other_rule=None
    )

    effect_state_to_r0 = Effect(state, IdAtom(r0))
    state_to_r0_condition = (
        AgentActionEqualToConstraint(Sender, sb0)
        & state_equal_to_empty
        & EnvironmentActionEqualToConstraint(SR)
    ) | (
        AgentActionEqualToConstraint(Sender, sb0)
        & state_equal_to_empty
        & EnvironmentActionEqualToConstraint(S)
    )
    effect_state_to_r1 = Effect(state, IdAtom(r1))
    state_to_r1_condition = (
        AgentActionEqualToConstraint(Sender, sb1)
        & state_equal_to_empty
        & EnvironmentActionEqualToConstraint(SR)
    ) | (
        AgentActionEqualToConstraint(Sender, sb1)
        & state_equal_to_empty
        & EnvironmentActionEqualToConstraint(S)
    )
    receiver_evolution_rules = [
        EvolutionRule([effect_state_to_r0], state_to_r0_condition),
        EvolutionRule([effect_state_to_r1], state_to_r1_condition),
    ]

    receiver_agent = Agent(
        name=Receiver,
        lobs_var_definitions=None,
        agent_var_definitions=receiver_vars,
        agent_red_definitions=None,
        agent_action_definitions=receiver_actions,
        agent_protocol_definition=receiver_protocol,
        agent_evolution_definition=receiver_evolution_rules,
    )

    # evaluation rules
    recbit, recack = "recbit", "recack"
    bit0, bit1 = "bit0", "bit1"
    envworks = "envworks"

    sender_bit_equal_to_b0 = EqualTo(AttributeIdAtom(Sender, bit), IdAtom(b0))
    sender_bit_equal_to_b1 = EqualTo(AttributeIdAtom(Sender, bit), IdAtom(b1))
    sender_ack_equal_to_true = EqualTo(AttributeIdAtom(Sender, ack), TrueBoolValue())
    sender_ack_equal_to_false = EqualTo(AttributeIdAtom(Sender, ack), FalseBoolValue())

    receiver_state_equal_to_r0 = EqualTo(AttributeIdAtom(Receiver, state), IdAtom(r0))
    receiver_state_equal_to_r1 = EqualTo(AttributeIdAtom(Receiver, state), IdAtom(r1))
    receiver_state_equal_to_empty = EqualTo(
        AttributeIdAtom(Receiver, state), IdAtom(empty)
    )

    recbit_def = EvaluationRule(
        recbit, (receiver_state_equal_to_r0 | receiver_state_equal_to_r1)
    )
    recack_def = EvaluationRule(recack, sender_ack_equal_to_true)
    bit0_def = EvaluationRule(bit0, sender_bit_equal_to_b0)
    bit1_def = EvaluationRule(bit1, sender_bit_equal_to_b1)
    envworks_def = EvaluationRule(
        envworks, EqualTo(EnvironmentIdAtom(state), IdAtom(SR))
    )
    evaluation_rules = [
        recbit_def,
        recack_def,
        bit0_def,
        bit1_def,
        envworks_def,
    ]

    initial_states_boolcond = (
        (sender_bit_equal_to_b0 | sender_bit_equal_to_b1)
        & (receiver_state_equal_to_empty)
        & (sender_ack_equal_to_false)
        & EqualTo(EnvironmentIdAtom(state), IdAtom(none))
    )

    groups = [Group("g1", {Sender, Receiver})]

    fairness_formulae = [AtomicFormula(envworks)]
    formulae = [AFFormula(AtomicFormula(recbit))]

    system = InterpretedSystem(
        semantics=Semantics.MULTI_ASSIGNMENT,
        environment=env_agent,
        agents=[sender_agent, receiver_agent],
        evaluation_rules=evaluation_rules,
        initial_states_boolean_condition=initial_states_boolcond,
        groups=groups,
        fair_formulae=fairness_formulae,
        formulae=formulae,
    )

    print(interpreted_system_to_string(system))
