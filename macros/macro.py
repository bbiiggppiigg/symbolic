from builtins import super
from typing import List, Tuple

from macros.binding import MapFVValue, MapInputValue, MapFVInput, Filter
from macros.bounded_expression import OutputActionList, OutputAction ,BoundedEQ
from macros.exceptions import UnsatisfiableActionException
from macros.expression import Match, Implies, Action


def get_fv_value_mapping(fvs, pkt):
    return MapFVValue(fvs, pkt)


class Macro(object):
    def get_fv_value_mapping(self, pkt):
        # type: (MapInputValue) ->  MapFVValue
        return MapFVValue(self.fvs, pkt)

    pass


class Invariant(Macro):
    def __init__(self, expr):
        # type: (Implies)-> None
        self.expr = expr
        self.fvs = self.expr.collect_fv_input_mapping()
        print("collected fvs = ", self.fvs.mapping)

    def apply(self, pkt):
        # type: (MapInput,Value) -> OutputActionList
        conf = MapFVValue(self.fvs, pkt)
        ret = self.expr.instantiate_fvs(conf).apply(pkt)

        return ret


class PrecedenceFactory(object):
    instance = None

    def __init__(self):
        # TODO: Use Dictionary instead
        self.records = dict()
        self.symbolics = dict()
        self.concretes = dict()
        self.concrete_id = 0
        self.symbolic_id = 0

    def insert(self, before, after):
        # type:(Action,Action) -> None
        print "calling insert"
        before_fvs = before.collect_fv_input_mapping()
        after_fvs = after.collect_fv_input_mapping()

        if before_fvs.mapping == dict() and after_fvs.mapping == dict():
            # is non-symbolic:

            p = NewConcretePrecedence(before, after, self.concrete_id)
            self.concretes[p.id] = p
            self.concrete_id += 1

        else:
            p = NewSymbolicPrecedence(before, after, self.symbolic_id, before_fvs + after_fvs)
            self.symbolics[p.id] = p
            self.records[p.id] = Filter({})
            self.symbolic_id += 1

        print "after printing records dict", self.records
        print "printing concrete", self.concretes
        print "printing symbolic ", self.symbolics

    def record(self, pkt):
        # type: (MapInputValue) -> None
        to_delete = list()
        for key, prec in self.concretes.items():
            if prec.before_trivially_satisfied(pkt):
                to_delete.append(key)
        for k in to_delete:
            print "deleting %d from concrete precedences" % k
            del self.concretes[k]

        for key, prec in self.symbolics.items():
            print "recoding symbolic " ,key , prec 
            if prec.before_trivially_satisfied(pkt):
                self.records[key] += prec.get_filter(pkt)

    def create_output_action_list(self, pkt):
        #ret = OutputActionList([])
        ret = list()
        for key, prec in self.concretes.items():
            # At this phase, all precedence are not trivially satisfied
            # Which means, either we set output of first to true or output of after to false
            # If there is no
            ret.append(prec.create_output_action_list(pkt))

        print "printing records dict", self.records
        for key, prec in self.symbolics.items():
            ret.append(prec.create_output_action_list(pkt,self.records[key]))

        return ret
        pass

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = PrecedenceFactory()
        return cls.instance

    def update(self, pkt, trace_list):
        # type:(List[Tuple[int,int,int]]) -> None
        to_delete = list()
        for trace in trace_list:
            ptype, pid, choice = trace
            if ptype == 0:
                if choice == 0:
                    to_delete.append(pid)
                else:  # TODO: Same as below
                    pass
            if ptype == 1:
                if choice == 0:
                    prec = self.symbolics[pid]
                    self.records[pid] += prec.get_filter(pkt)
                else:
                    pass
                # TODO: It might be the case that even if we choose to falsify the later,
                #  we still happened to staisfied the front, and we need to check that

        for target in to_delete:
            del self.concretes[target]


class NewConcretePrecedence(Macro):

    def __init__(self, before, after, id):
        # type:(And,And, int ) -> None
        self.id = id
        self.before = before
        self.after = after

        self.before_input, self.before_output = self.before.split()
        self.after_input, self.after_output = self.after.split()

    def before_trivially_satisfied(self, pkt):
        # type:(MapInputValue) -> bool
        if self.before_output is None:
            try:
                if self.before_input.instantiate_fvs(MapFVValue( None, pkt )).apply(pkt).is_true():
                    return True
            except UnsatisfiableActionException:
                pass

        return False

    def after_trivially_unsat(self, pkt):
        if self.after_input is not None:
            try:
                if not self.after_input.instantiate_fvs(MapFVValue(None , pkt)).apply(pkt).is_true():
                    return True
            except UnsatisfiableActionException:
                return True

        return False

    def create_output_action_list(self, pkt):
        ret = []
        if self.after_trivially_unsat(pkt):
            # TODO: somethign 
            print "if after is trivially unsatisfiable, we can choose between setting setting before to true or not"
            if self.before_trivially_satisfied(pkt):
                assert False, "should have been checked up front at record"
            else:
                before_output = self.before_output.instantiate_fvs(MapFVValue(None,pkt))
                bplist = before_output.bplist
                for bp in bplist:
                    if isinstance(bp,BoundedEQ):
                        ret.append(OutputAction([ ],[(0,self.id,1)],bp.negate().get_filter()))
                    else:
                        ret.append(OutputAction([bp.negate().apply(pkt)], [(0, self.id, 1)]))
 
                ret.append(OutputAction([ ],[(0,self.id,0)],Filter({}))) # Choose 0 by negating result
           
            return OutputActionList(ret, False)
        else:
            if self.before_output is not None:
                before_output = self.before_output.instantiate_fvs(MapFVValue(None,pkt)).apply(pkt)
                choose_before = before_output.associate([(0, self.id, 0)])
                ret.append(choose_before)
            if self.after_output is not None:
                after_output = self.after_output.instantiate_fvs(MapFVValue(None,pkt))
                bplist = after_output.bplist
                for bp in bplist:
                    if isinstance(bp,BoundedEQ):
                        ret.append(OutputAction([ ],[(0,self.id,1)],bp.negate().get_filter()))
                    else:
                        ret.append(OutputAction([bp.negate().apply(pkt)], [(0, self.id, 1)]))
            else:
                if self.before is None:
                    assert False, "We're doomed! "

            return OutputActionList(ret, False)

    def get_filter(self):
        pkt = MapInputValue(None, 0, [])
        return self.after.instantiate_fvs(MapFVValue(None,pkt)).apply(pkt).get_filter()

        pass


class NewSymbolicPrecedence(Macro):

    def __init__(self, before, after, id, fvs):
        # type:(Action,Action, int , MapFVInput) -> None
        self.id = id
        self.id = id
        self.before = before
        self.after = after
        self.fvs = fvs
        self.before_input, self.before_output = self.before.split()
        self.after_input, self.after_output = self.after.split()

    def before_trivially_satisfied(self, pkt):
        # type:(MapInputValue) -> bool
        conf = MapFVValue(self.fvs, pkt)
        if self.before_output is None:
            if self.before_input.instantiate_fvs(MapFVValue(conf,pkt)).apply(pkt):
                return True

        return False

    def after_trivially_unsat(self, pkt):
        # type:(MapInputValue) -> bool
        conf = MapFVValue(self.fvs, pkt)
        if not self.after_input.instantiate_fvs(MapFVValue(conf,pkt)).apply(pkt):
            return True
        return False

    def create_output_action_list(self, pkt, output_filter):
        ret = []
        if self.after_trivially_unsat(pkt):
            # TODO: somethign 
            pass
        else:
            if self.before_output is not None:
                before_output = self.before_output.instantiate_fvs(MapFVValue(None,pkt)).apply(pkt)
                choose_before = before_output.associate([(1, self.id, 0)])
                ret.append(choose_before)

            if self.after_output is not None:
                after_output = self.after_output.instantiate_fvs(MapFVValue(None,pkt))
                bplist = after_output.bplist
                for i, bp in enumerate(bplist):
                    if i != after_output.index:
                        ret.append(OutputAction([bp.negate().apply(pkt)], [(1, self.id, 1)]))
                    else:
                        ret.append(OutputAction([], [(1, self.id, 1)], output_filter))
            else:
                if self.before is None:
                    assert False, "We're doomed! "


def get_filter(self, pkt):
    conf = MapFVValue(self.fvs, pkt)
    return self.after.instantiate_fvs(conf).get_filter()

"""
class Precedence(Macro):
    def __init__(self, before, after, fvs, symbolic):
        self.before = before
        self.after = after
        self.fvs = fvs
        self.symbolic = symbolic

    def happen(self, pkt):
        conf = MapFVValue(self.fvs, pkt)
        ret = self.before.instantiate_fvs(conf).apply(pkt)
        return ret

    @classmethod
    def create(cls, before, after):
        fvs = before.collect_fv_input_mapping()
        if fvs.mapping == dict():
            return ConcretePrecedence(before, after, fvs)
        else:
            return SymbolicPrecedence(before, after, fvs)

    def __repr__(self):
        return " Precedence ( %s , %s ) " % (self.before.__repr__(), self.after.__repr__())


class ConcretePrecedence(Precedence):
    def __init__(self, before, after, binding):
        super().__init__(before, after, binding, False)

    def get_filter(self):
        input_binding = MapInputValue(None, 0, [])
        return self.after.instantiate_fvs(MapFVValue(input_binding, None)).apply(input_binding).get_filter()


class SymbolicPrecedence(Precedence):
    def __init__(self, before, after, binding):
        super().__init__(before, after, binding, True)

    def get_filter(self, pkt):
        conf = MapFVValue(self.fvs, pkt)
        return self.after.instantiate_fvs(conf).get_filter()
"""

class Reaction(Macro):
    def __init__(self, start, policy, end):
        # type:  (Match,Implies,Match) -> None
        self.start = start
        self.policy = policy
        self.end = end
        self.fvs = self.start.collect_fv_input_mapping()
        policy_binding = policy.collect_fv_input_mapping()
        end_binding = end.collect_fv_input_mapping()

        for k in policy_binding.mapping.keys():
            if k not in self.fvs.mapping.keys():
                raise Exception("Free Variable not bounded %s " % k)

        for k in end_binding.mapping.keys():
            if k not in self.fvs.mapping.keys():
                raise Exception("Free Variable not bounded %s " % k)

        self.policy_binding = policy_binding
        self.end_binging = end_binding
