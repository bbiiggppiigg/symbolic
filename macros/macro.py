from macros.binding import Configuration, InputBinding
from builtins import super
class Macro(object):

    def get_configuration(self, pkt):
        return Configuration(self.binding, pkt)

    pass


class Invariant(Macro):
    def __init__(self, expr):
        self.expr = expr
        self.binding = self.expr.collect_binding()

    def apply(self, input_binding):
        conf = self.get_configuration(input_binding)
        ret = self.expr.apply_conf(conf).apply(input_binding)

        return ret


class Precedence(Macro):
    def __init__(self, before, after, binding, symbolic):
        self.before = before
        self.after = after
        self.binding = binding
        self.symbolic = symbolic

    def happen(self,input_binding):
        conf = self.get_configuration(input_binding)
        ret = self.before.apply_conf(conf).apply(input_binding)
        return ret

    @classmethod
    def create(cls, before, after):
        binding = before.collect_binding()
        if binding.binding == dict():
            return ConcretePrecedence(before, after, binding)
        else:
            return SymbolicPrecedence(before, after, binding)

    def __repr__(self):
        return " Precedence ( %s , %s ) " % (self.before.__repr__(), self.after.__repr__())


class ConcretePrecedence(Precedence):
    def __init__(self, before, after, binding):
        super().__init__(before, after, binding, False)

    def get_filter(self):
        input_binding = InputBinding(None, 0, [])
        return self.after.apply_conf(Configuration(input_binding, None)).apply(input_binding).get_filter()


class SymbolicPrecedence(Precedence):
    def __init__(self, before, after, binding):
        super().__init__(before, after, binding, True)

    def get_filter(self, input_binding):
        conf = self.get_configuration(input_binding)
        return self.after.apply_conf(conf).get_filter()


class Reaction(Macro):
    def __init__(self, start, policy, end):
        self.start = start
        self.policy = policy
        self.end = end
        self.binding = self.start.collect_binding()
        policy_binding = policy.collect_binding()
        end_binding = end.collect_binding()

        for k in policy_binding.binding.keys():
            if k not in self.binding.binding.keys():
                raise Exception("Free Variable not bounded %s " % k)

        for k in end_binding.binding.keys():
            if k not in self.binding.binding.keys():
                raise Exception("Free Variable not bounded %s " % k)

        self.policy_binding = policy_binding
        self.end_binging = end_binding

    def get_actions(self, input_binding):
        conf = self.get_configuration(input_binding)
        match = self.policy.left.apply_conf(conf).apply(input_binding)
        action = self.policy.right.apply_conf(conf).apply(input_binding)
        ands = match
        cond = True
        for expr in ands.expr_list:
            cond &= expr
