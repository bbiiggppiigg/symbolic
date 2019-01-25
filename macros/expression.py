from macros.binding import FVS
from macros.bounded_expression import BoundedImplies, BoundedAction, BoundedMatch, \
    BoundedEQ, BoundedGT, BoundedLT, BoundedNEQ, BoundedActionList, BoundedGuard, BoundedGEQ, BoundedLEQ
from macros.variables import Input, FreeVariable

"""
    What should apply returns ?
    Need to differentiate between arbitrary and unsatisfiable
"""


class Expr(object):
    def collect_binding(self):
        return FVS()
        pass

    def apply_conf(self, conf):
        raise NotImplementedError

    pass


class Predicate(Expr):
    def apply_conf(self, binding):
        raise NotImplementedError;

    def negate(self):
        raise NotImplementedError;

    pass


class LEQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedLEQ(left, right)

    def negate(self):
        return GT(self.left, self.right)


class GEQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedGEQ(left, right)

    def negate(self):
        return LT(self.left, self.right)


class GT(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedGT(left, right)

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def negate(self):
        return LEQ(self.left, self.right)


class LT(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedLT(left, right)

    def negate(self):
        return GEQ(self.left, self.right)


class EQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collect_binding(self):
        if isinstance(self.left, Input) and isinstance(self.right, FreeVariable):
            return FVS(self.right, self.left)
        if isinstance(self.left, FreeVariable) and isinstance(self.right, Input):
            return FVS(self.left, self.right)
        return FVS()

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedEQ(left, right)

    def __repr__(self):
        return "( %s == %s )" % (self.left, self.right)

    def negate(self):
        return NEQ(self.left, self.right)

    pass


class NEQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collect_binding(self):
        if isinstance(self.left, Input) and isinstance(self.right, FreeVariable):
            return FVS(self.right, self.left)
        if isinstance(self.left, FreeVariable) and isinstance(self.right, Input):
            return FVS(self.left, self.right)
        return FVS()

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = binding.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = binding.binding[self.right]
        return BoundedNEQ(left, right)

    def negate(self):
        return EQ(self.left, self.right)

    pass


class Match(Expr):

    def __init__(self, expr_list):
        self.expr_list = expr_list

    def collect_binding(self):
        ret = FVS()
        for expr in self.expr_list:
            ret += expr.collect_binding()
        return ret

    def apply_conf(self, conf):
        return BoundedMatch(list(map(lambda x: x.apply_conf(conf), self.expr_list)))

    def __repr__(self):
        return "Match(%s)" % "".join(map(lambda x: x.__repr__(), self.expr_list))


"""
    Action should be a OR of ANDs, in DNF 
    (A & B & C) | (A & !B & C) | , ... ()    
"""


class Guard(Expr):
    def __init__(self, assign_list):
        self.assign_list = assign_list

    def collect_binding(self):
        ret = FVS()
        for expr in self.assign_list:
            ret += expr.collect_binding()
        return ret

    def apply_conf(self, binding):
        return BoundedGuard(list(map(lambda x: x.apply_conf(binding), self.assign_list)))

    def __repr__(self):
        return "Action(%s)" % (",".join(map(lambda x: x.__repr__(), self.assign_list)))

    def negate(self):
        ret = []
        for assign in self.assign_list:
            ret.append(assign.negate())
        return Guard(ret)


class Action(Expr):

    def __init__(self, assign_list):
        self.assign_list = assign_list

    def collect_binding(self):
        ret = FVS()
        for expr in self.assign_list:
            ret += expr.collect_binding()
        return ret

    def apply_conf(self, binding):
        return BoundedAction(list(map(lambda x: x.apply_conf(binding), self.assign_list)))

    def __repr__(self):
        return "Action(%s)" % (",".join(map(lambda x: x.__repr__(), self.assign_list)))

    pass


class ActionList(Expr):

    def __init__(self, action_list):
        self.action_list = action_list

    def collect_binding(self):
        ret = FVS()
        for expr in self.action_list:
            ret += expr.collect_binding()
        return ret

    def apply_conf(self, binding):
        return BoundedActionList(list(map(lambda x: x.apply_conf(binding), self.action_list)))

    def __repr__(self):
        return "ActionList(%s)" % (",".join(map(lambda x: x.__repr__(), self.action_list)))


class Implies(Expr):
    # eft: Match
    # ight: ActionList

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collect_binding(self):
        return self.left.collect_binding() + self.right.collect_binding()

    def apply_conf(self, binding):
        left = self.left
        right = self.right
        return BoundedImplies(left.apply_conf(binding), right.apply_conf(binding))

    def __repr__(self):
        return " %s  ->   %s  " % (self.left.__repr__(), self.right.__repr__())
