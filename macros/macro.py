from macros.binding import MapFVValue, MapInputValue
from builtins import super



def get_fv_value_mapping(fvs, pkt):
    return MapFVValue(fvs, pkt)

class Macro(object):
    pass


class Invariant(Macro):
    def __init__(self, expr):
        self.expr = expr
        self.fvs = self.expr.collect_fv_input_mapping()

    def apply(self, pkt):
        conf = MapFVValue(self.fvs,pkt)
        ret = self.expr.instantiate_fvs(conf).apply(pkt)

        return ret


class Precedence(Macro):
    def __init__(self, before, after, fvs, symbolic):
        self.before = before
        self.after = after
        self.fvs = fvs
        self.symbolic = symbolic

    def happen(self, pkt):
        conf =  MapFVValue(self.fvs,pkt)
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
        conf = MapFVValue(self.fvs,pkt)
        return self.after.instantiate_fvs(conf).get_filter()


class Reaction(Macro):
    def __init__(self, start, policy, end):
        self.start = start
        self.policy = policy
        self.end = end
        self.binding = self.start.collect_fv_input_mapping()
        policy_binding = policy.collect_fv_input_mapping()
        end_binding = end.collect_fv_input_mapping()

        for k in policy_binding.binding.keys():
            if k not in self.binding.binding.keys():
                raise Exception("Free Variable not bounded %s " % k)

        for k in end_binding.binding.keys():
            if k not in self.binding.binding.keys():
                raise Exception("Free Variable not bounded %s " % k)

        self.policy_binding = policy_binding
        self.end_binging = end_binding

    def get_actions(self, pkt):
        conf = MapFVValue(self.binding, pkt)
        match = self.policy.left.instantiate_fvs(conf).apply(pkt)
        action = self.policy.right.instantiate_fvs(conf).apply(pkt)
        ands = match
        cond = True
        for expr in ands.expr_list:
            cond &= expr
