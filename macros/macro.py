from macros.binding import InputBinding, Configuration


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
    def __init__(self, before, after):
        self.before = before
        self.after = after
        self.binding = self.before.collect_binding()

    def happen(self, conf, input_binding):
        if self.before.apply_conf(conf).apply(input_binding):
            return True
        return False


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
