from macros.binding import InputBinding, Configuration, Packet
from macros.expression import Match, Implies, Guard


class Macro(object):
    def get_configuration(self, pkt        , port_id     ):
        return Configuration(self.binding, InputBinding(pkt, port_id))

    pass


class Invariant(Macro):
    def __init__(self, expr):
        self.expr = expr
        self.binding = self.expr.collect_binding()

    def apply(self, pkt        , port_id     ):
        conf = self.get_configuration(pkt, port_id)
        ret = self.expr.apply_conf(conf).apply(InputBinding(pkt, port_id))

        return ret


class Precedence(Macro):
    def __init__(self, before       , after       ):
        self.before = before
        self.after = after
        self.binding = self.before.collect_binding()

    def happen(self, conf               , pkt        , port_id     ):
        if self.before.apply_conf(conf).apply(InputBinding(pkt, port_id)):
            return True
        return False


class Reaction(Macro):
    def __init__(self, start       , policy         , end       ):
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

    def get_actions(self, pkt        , port_id     ):
        conf = self.get_configuration(pkt, port_id)
        match = self.policy.left.apply_conf(conf).apply(InputBinding(pkt, port_id))
        action = self.policy.right.apply_conf(conf).apply(InputBinding(pkt, port_id))
        ands = match
        cond = True
        for expr in ands.expr_list:
            cond &= expr
