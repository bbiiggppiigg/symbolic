from macros.actions import OutputActionList
from macros.binding import InputBinding
from macros.bounded_expression import Bool
from macros.exceptions import UnsatisfiableActionException
from macros.instances import invariants, reactions, precedences

import frenetic
from frenetic.syntax import *
from frenetic.packet import *




class ActivatedPrecedences(object):

    def __init__(self, precedes):
        self.records = dict()
        self.precedences = precedes

    def record(self, pkt, port_id):
        for prec in self.precedences:
            conf = prec.get_configuration(pkt, port_id)
            if prec.happen(conf, pkt, port_id):
                if prec not in self.records:
                    self.records[prec] = set()
                self.records[prec].add(conf)

    def get_assignments(self, input_binding, pkt, port_id):
        ret = []
        for prec in self.precedences:
            conf = prec.get_configuration(pkt, port_id)
            if conf not in self.records[prec]:
                ret.append(prec.after.negate().apply_conf(conf).apply(input_binding))
        return ret


class ActivatedReactions(object):

    def __init__(self, reacts):
        self.record = dict()
        self.reactions = reacts

    def clear(self, input_binding):
        for react, confs in self.record.items():
            new_confs = []
            for conf in confs:
                if react.end.apply_conf(conf).apply(input_binding):
                    continue
                new_confs.append(conf)
            self.record[react] = new_confs

    def activate(self, input_binding, pkt, port_id):
        for react in self.reactions:
            conf = react.get_configuration(pkt, port_id)
            if react.start.apply_conf(conf).apply(input_binding):
                if react not in self.record:
                    self.record[react] = list()
                self.record[react].append(conf)

    def get_assignments(self, input_binding):
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

class RepeaterApp(frenetic.App):

    def __init__(self):
        frenetic.App.__init__(self)

    def connected(self):
        def handle_current_switches(swithces):
            dpid = swithces.keys()[0]

            self.update(id >> SendToController("repeater_app"))
        self.current_switches(callback=handle_current_switches)

    def packet_in(self,dpid,port_id,payload):
        actions = SetPort([1,2,3,4,5])
        pkt = Packet.from_payload(dpid,port_id,payload)
        input_binding = InputBinding(pkt,port_id)
        #print input_binding
        ActivePrecedences.record(pkt, port_id)
        ActiveReactions.clear(input_binding)
        
        
        OA = OutputActionList([])
        
        for invariant in invariants:
            conf = invariant.get_configuration(pkt, port_id)
            #print (invariant.expr.apply_conf(conf))
            rhs = invariant.expr.apply_conf(conf).apply(input_binding)
            if type(rhs) == Bool:
                if rhs.value:
                    print("GOOD!")
                else:
                    raise Exception("Violation!")  # TODO : Test
            else:
                #print("before update oa = ", OA)
                OA = OA * rhs
                #print("after update oa = ", OA)

        try:
            oas = ActiveReactions.get_assignments(input_binding)
            for oa in oas:
                OA = OA * oa
        except UnsatisfiableActionException:
            raise Exception("QQ")

        """
        try:
            oas = ActivePrecedences.get_assignments(input_binding, pkt, port_id)
            for oa in oas:
                OA = OA * oa
        except UnsatisfiableActionException:
            raise Exception("QQ")
        """
        # Update Activated Reactions and Precedences
        ActiveReactions.activate(input_binding, pkt, port_id)
        print("final oa = ", OA)

        self.pkt_out(dpid,payload,actions)
app = RepeaterApp()
app.start_event_loop()


