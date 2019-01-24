from macros.actions import OutputActionList
from macros.binding import InputBinding, Packet
from macros.bounded_expression import Bool
from macros.exceptions import UnsatisfiableActionException
from macros.inputs import input_sequence
from macros.instances import invariants, reactions, precedences, inv


class ActivatedPrecedences(object):

    def __init__(self, precedences):
        self.records = dict()
        self.precedences = precedences

    def record(self, pkt: Packet, port_id: int):
        for prec in self.precedences:
            conf = prec.get_configuration(pkt, port_id)
            if prec.happen(conf, pkt, port_id):
                if prec not in self.records:
                    self.records[prec] = set()
                self.records[prec].add(conf)

    def get_assignments(self, input_binding: InputBinding, pkt, port_id):
        ret = []
        for prec in self.precedences:
            conf = prec.get_configuration(pkt, port_id)
            if conf not in self.records[prec]:
                ret.append(prec.after.negate().apply_conf(conf).apply(input_binding))
        return ret


class ActivatedReactions(object):

    def __init__(self, reactions):
        self.record = dict()
        self.reactions = reactions

    def clear(self, input_binding: InputBinding):
        for react, confs in self.record.items():
            new_confs = []
            for conf in confs:
                if react.end.apply_conf(conf).apply(input_binding):
                    continue
                new_confs.append(conf)
            self.record[react] = new_confs

    def activate(self, input_binding: InputBinding, pkt: Packet, port_id: int):
        for react in self.reactions:
            conf = react.get_configuration(pkt, port_id)
            if react.start.apply_conf(conf).apply(input_binding):
                if react not in self.record:
                    self.record[react] = list()
                    self.record[react].append(conf)

    def get_assignments(self, input_binding: InputBinding):
        ret = []
        for react, confs in self.record.items():
            for conf in confs:
                rhs = react.policy.apply_conf(conf).apply(input_binding)
                if type(rhs) == Bool:
                    assert rhs.value
                    continue
                else:
                    ret.append(rhs)
        return ret


ActiveReactions = ActivatedReactions(reactions)
ActivePrecedences = ActivatedPrecedences(precedences)

for (pkt, port_id) in input_sequence:
    input_binding = InputBinding(pkt, port_id)

    ActivePrecedences.record(pkt, port_id)
    ActiveReactions.clear(input_binding)

    # Enforce policies for Invariant, Reaction and Precedence
    OA = OutputActionList([])
    for invariant in invariants:
        conf = inv.get_configuration(pkt, port_id)
        rhs = invariant.expr.apply_conf(conf).apply(input_binding)
        if type(rhs) == Bool:
            if rhs.value:
                print("GOOD!")
            else:
                raise Exception("Violation!")  # TODO : Test
        else:
            print("before update oa = ", OA)
            OA = OA * rhs
            print("after update oa = ", OA)

    try:
        oas = ActiveReactions.get_assignments(input_binding)
        for oa in oas:
            OA = OA * oa
    except UnsatisfiableActionException:
        raise Exception("QQ")

    try:
        oas = ActivePrecedences.get_assignments(input_binding, pkt, port_id)
        for oa in oas:
            OA = OA * oa
    except UnsatisfiableActionException:
        raise Exception("QQ")

    # Update Activated Reactions and Precedences
    ActiveReactions.activate(input_binding, pkt, port_id)
    print("final oa = ", OA)
