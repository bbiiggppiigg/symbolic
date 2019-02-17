import frenetic
from frenetic.packet import *
from frenetic.syntax import *
# from macros.frenetic import *

# from examples.static import invariants, reactions, precedences, state_var_list
from examples.ssymbolic import invariants, reactions, precedences, state_var_list , symbolic_state_var_list
from macros.actions import OutputActionList
from macros.binding import MapInputValue, Filter
from macros.bounded_expression import Bool
from macros.exceptions import UnsatisfiableActionException


# from examples.stateful import invariants, reactions, precedences
# from examples.combine import invariants, reactions, precedences
# from examples.conflict import invariants, reactions, precedences , state_var_list


class StateVariables(object):
    def __init__(self, state_var_list):
        self.records = dict()
        for sv in state_var_list:
            self.records[sv.name] = sv

    def update(self, new_dict):
        for name in self.records.keys():
            if name + "_out" in new_dict:
                self.records[name].update_value(new_dict[name + "_out"])
        pass


class SymbolicStateVariables(object):
    def __init__(self, symbolic_state_var_list):
        self.records = dict()
        for ssv in symbolic_state_var_list:
            self.records[ssv.name] = ssv
    
    def update(self, new_dict ,indices):
        for name in self.records.keys():
            if name + "_out" in indices:
                self.records[name].update_value(indices[name+"_out"],new_dict[name+"_out"])
        

class ActivatedInvariants(object):

    def __init__(self, invars):
        self.records = invars

    def get_assignments(self, input_binding):
        ret = []

        for inv in self.records:

            conf = inv.get_fv_value_mapping(input_binding)
            print "config is ",conf.mapping
            rhs = inv.expr.instantiate_fvs(conf).apply(input_binding)
            if type(rhs) == Bool:
                if rhs.value:
                    pass
                else:
                    raise Exception("Violation!")  # TODO : Test
            else:
                # print("before update oa = ", OA ,"rhs = ", rhs)
                ret.append(rhs)
        return ret


class ActivatedPrecedences(object):

    def __init__(self, precedes):
        self.records = dict()
        self.symbolics = filter(lambda prec: prec.symbolic, precedes)
        self.concretes = filter(lambda prec: prec.symbolic == False, precedes)

        print(len(self.symbolics))
        print(len(self.concretes))
        for prec in self.symbolics:
            self.records[prec] = Filter({})

    def record(self, input_binding):
        res = []
        for prec in self.concretes:
            if prec.happen(input_binding):
                print("removing concrete precedence")

            else:
                res.append(prec)
        self.concretes = res

        for prec in self.symbolics:
            if prec.happen(input_binding):
                print("recording")
                self.records[prec] += prec.get_filter(input_binding)
                print("filter for prec = ", prec, " is ", self.records[prec])

    def get_filter(self):
        ret = Filter({})
        for prec in self.concretes:
            print(prec)
            ret *= prec.get_filter()

        print("filter = ", ret.binding)
        for prec in self.symbolics:
            ret *= self.records[prec];

        print("filter = ", ret.binding)
        return ret


class ActivatedReactions(object):

    def __init__(self, reacts):
        self.record = dict()
        self.reactions = reacts

    def clear(self, input_binding):
        for react, confs in self.record.items():
            new_confs = []
            for conf in confs:
                if react.end.instantiate_fvs(conf).apply(input_binding):
                    continue
                new_confs.append(conf)
            self.record[react] = new_confs

    def activate(self, input_binding):
        for react in self.reactions:
            conf = react.get_fv_value_mapping(input_binding)
            if react.start.instantiate_fvs(conf).apply(input_binding):
                if react not in self.record:
                    self.record[react] = list()
                self.record[react].append(conf)

    def get_assignments(self, input_binding):
        ret = []
        for react, confs in self.record.items():
            for conf in confs:
                tmprhs = react.policy.instantiate_fvs(conf)
                print "tmp rhs = ",tmprhs
                rhs = tmprhs.apply(input_binding)
                print "rhs =",rhs
                if type(rhs) == Bool:
                    assert rhs.value
                    continue
                else:
                    ret.append(rhs)
        return ret


ActiveReactions = ActivatedReactions(reactions)
ActivePrecedences = ActivatedPrecedences(precedences)
ActiveInvariants = ActivatedInvariants(invariants)
ActiveSVs = StateVariables(state_var_list)
ActiveSSVs = SymbolicStateVariables(symbolic_state_var_list)

counter = 0
ports = None

class RepeaterApp(frenetic.App):

    def __init__(self):
        frenetic.App.__init__(self)

    def connected(self):
        def handle_current_switches(switches):
            dpid  = switches.keys()[0]
            global ports
            ports = switches[dpid]

            self.update(id >> SendToController("repeater_app"))

        self.current_switches(callback=handle_current_switches)

    def packet_in(self, dpid, port_id, payload):
        global counter
        print("pkt_count =", counter)
        counter += 1
        actions = []  # SetPort([1, 2, 3, 4, 5])
        pkt = Packet.from_payload(dpid, port_id, payload)
        print(pkt)
        input_binding = MapInputValue(pkt, port_id, ActiveSVs.records , ActiveSSVs.records)
        # print input_binding
        ActivePrecedences.record(input_binding)
        ActiveReactions.clear(input_binding)

        OA = OutputActionList([])
        print(OA.unsat)
        try:
            oas = ActiveInvariants.get_assignments(input_binding)
            for oa in oas:
                # print("before update oa = ", OA ,"rhs = ", oa)
                OA = OA * oa
            # print("after update oa = ", OA)
        except UnsatisfiableActionException:
            print("no satisfying assignment")
            raise Exception("QQ")
        print(OA.unsat)
        try:
            oas = ActiveReactions.get_assignments(input_binding)
            for oa in oas:
                print("before update oa = ", OA ,"rhs = ", oa)
                OA = OA * oa
                print("after update oa = ", OA)
        except UnsatisfiableActionException:
            print("no satisfying assignment")
            raise Exception("QQ")
        print("before filter, action = ", OA.get_action())
        try:
            action_filter = ActivePrecedences.get_filter()
            OA = OA.filter_output(action_filter)
        except UnsatisfiableActionException:
            raise Exception("QQ")
        print(OA.unsat)
        # Update Activated Reactions and Precedences
        ActiveReactions.activate(input_binding)
        # print("final oa = ", OA)
        # print "unsat ? ", OA.unsat
        action,indices = OA.get_action()
        # print "action = ",action
        # raw_input("#")
        set_port = []
        for k, v in action.items():
            if k == "port_id_out":
                # print "port = ",v
                if v > len(ports) + 1:
                    print ("haven't learnt destination = %s , broadcasting"%pkt.ip4Dst)
                    set_port.append(SetPort(ports))
                else:
                    print ("learnt destination = %s , sending to port %d"%(pkt.ip4Dst,v))
                    set_port.append(SetPort(v))  # TODO Check for Broadcast Port
            elif k == "ip4Dst_out":
                actions.append(SetIP4Dst(v))
            elif k == "ip4Src_out":
                actions.append(SetIP4Src(v))
            elif k == "ethSrc_out":
                actions.append(SetEthSrc(v))
            elif k == "ethDst_out":
                actions.append(SetEthDst(v))
            elif k == "ipProto_out":
                actions.append(SetIPProto(v))

        self.pkt_out(dpid, payload, Seq(actions + set_port))
        ActiveSVs.update(action)
        ActiveSSVs.update(action,indices)


app = RepeaterApp()
app.start_event_loop()
