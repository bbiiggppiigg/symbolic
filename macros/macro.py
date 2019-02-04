from macros.binding import Configuration , Filter,InputBinding
from macros.expression import Match, Implies


class Macro(object):

    def get_configuration(self, input_binding):
        return Configuration(self.binding, input_binding)

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
    def __init__(self, before, after ) :
        self.before = before
        self.after = after
        self.binding = self.before.collect_binding()
        if self.binding.binding == dict():
            self.symbolic = False
        else:
            self.symbolic = True

    def happen(self, conf, input_binding):
        ret = self.before.apply_conf(conf).apply(input_binding)
        if ret:
            return True
        return False
    
    def collect_outputs(self):
        return self.after.collect_outputs()
        
    def get_filter(self):
        assert (self.symbolic == False)
        input_binding = InputBinding(None,0,[])
        return self.after.apply_conf(Configuration(input_binding,None)).apply(input_binding).get_filter()

    def __repr__(self):
        return " Precedence ( %s , %s ) " % (self.before.__repr__(),self.after.__repr__())

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
