from typing import Tuple, List

from macros.binding import MapFVInput
from macros.bounded_expression import BoundedImplies, BoundedAction, BoundedMatch, \
    BoundedEQ, BoundedGT, BoundedLT, BoundedNEQ, BoundedActionList, BoundedAnd, BoundedGEQ, BoundedLEQ
from macros.variables import Input, FreeVariable, Output

"""
    What should apply returns ?
    Need to differentiate between arbitrary and unsatisfiable
"""


class Expr(object):
    def collect_fv_input_mapping(self):
        return MapFVInput()
        pass

    def instantiate_fvs(self, fv_value_mapping):
        raise NotImplementedError

    pass


class Predicate(Expr):
    left = None
    right = None

    def instantiate_fvs(self, fv_value_mapping):
        raise NotImplementedError;

    def negate(self):
        raise NotImplementedError;

    pass


class LEQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])
        return BoundedLEQ(left, right)

    def negate(self):
        return GT(self.left, self.right)


class GEQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])
        return BoundedGEQ(left, right)

    def negate(self):
        return LT(self.left, self.right)


class GT(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])
        return BoundedGT(left, right)

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def negate(self):
        return LEQ(self.left, self.right)


class LT(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        if isinstance(self.left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])
        return BoundedLT(left, right)

    def negate(self):
        return GEQ(self.left, self.right)


class EQ(Predicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collect_fv_input_mapping(self):
        # print ("collecing here")
        if isinstance(self.left, Input) and isinstance(self.right, FreeVariable):
            return MapFVInput(self.right, self.left)
        if isinstance(self.left, FreeVariable) and isinstance(self.right, Input):
            return MapFVInput(self.left, self.right)
        return MapFVInput()

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        left = fv_value_mapping.instantiate(left)
        right = fv_value_mapping.instantiate(right)
        """
        if isinstance(self.left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(self.right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])
        """
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

    def collect_fv_input_mapping(self):
        if isinstance(self.left, Input) and isinstance(self.right, FreeVariable):
            return MapFVInput(self.right, self.left)
        if isinstance(self.left, FreeVariable) and isinstance(self.right, Input):
            return MapFVInput(self.left, self.right)
        return MapFVInput()

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        if isinstance(left, FreeVariable):
            left = fv_value_mapping.binding[self.left]
        if isinstance(right, FreeVariable):
            right = fv_value_mapping.binding[self.right]
        if isinstance(left, Input) and left.is_symbolic:
            left = Input(left.name, fv_value_mapping.binding[left.fv])
        if isinstance(right, Input) and right.is_symbolic:
            left = Input(right.name, fv_value_mapping.binding[right.fv])

        return BoundedNEQ(left, right)

    def negate(self):
        return EQ(self.left, self.right)

    pass


class Match(Expr):

    def __init__(self, expr_list):
        self.expr_list = expr_list

    def collect_fv_input_mapping(self):
        # (print "QQ")
        ret = MapFVInput()
        for expr in self.expr_list:
            ret += expr.collect_fv_input_mapping()
        return ret

    def instantiate_fvs(self, fv_value_mapping):
        return BoundedMatch(list(map(lambda x: x.instantiate_fvs(fv_value_mapping), self.expr_list)))

    def __repr__(self):
        return "Match(%s)" % "".join(map(lambda x: x.__repr__(), self.expr_list))


"""
    A list of value assignment to variables, must be satisfied at the same time
"""


class And(Expr):

    def __init__(self, plist, index=-1):
        # type: (List[Predicate],int) -> None
        self.plist = plist
        self.index = index

    def split(self):
        # type: () -> Tuple[And,And]
        input_formula = list()
        output_formula = list()
        index = -1
        for assign in self.plist:
            if isinstance(assign.left, Output) or isinstance(assign.right, Output):
                if assign.collect_fv_input_mapping() != dict():
                    assert index == -1, " duplicate output symbolic variable %d and %d " % (index, len(output_formula))
                    index = len(output_formula)
                output_formula.append(assign)

            else:
                input_formula.append(assign)
            pass
        left = None if len(input_formula) == 0 else And(input_formula)
        right = None if len(output_formula) == 0 else And(output_formula, index)
        return left, right

    def collect_fv_input_mapping(self):
        ret = MapFVInput()
        for expr in self.plist:
            ret += expr.collect_fv_input_mapping()
        return ret

    def instantiate_fvs(self, fv_value_mapping):
        return BoundedAnd(
            list(
                map(lambda x: x.instantiate_fvs(fv_value_mapping), self.plist))
            , self.index)

    def __repr__(self):
        return "And(%s)" % (",".join(map(lambda x: x.__repr__(), self.plist)))

    pass


class Action(Expr):

    def __init__(self, assign_list):
        # type: (List[Predicate]) -> None
        self.assign_list = assign_list

    def split(self):
        # type: () -> Tuple[Action,Action]
        input_formula = list()
        output_formula = list()
        for assign in self.assign_list:
            if isinstance(assign.left, Output) or isinstance(assign.right, Output):
                output_formula.append(assign)
            else:
                input_formula.append(assign)
            pass
        left = None if len(input_formula) == 0 else Action(input_formula)
        right = None if len(output_formula) == 0 else Action(output_formula)
        return left, right

    def collect_fv_input_mapping(self):
        ret = MapFVInput()
        for expr in self.assign_list:
            ret += expr.collect_fv_input_mapping()
        return ret

    def instantiate_fvs(self, fv_value_mapping):
        return BoundedAction(list(map(lambda x: x.instantiate_fvs(fv_value_mapping), self.assign_list)))

    def __repr__(self):
        return "Action(%s)" % (",".join(map(lambda x: x.__repr__(), self.assign_list)))

    pass


"""
    A list of actions, at least one of which must be satisfied
"""


class ActionList(Expr):

    def __init__(self, action_list):
        self.action_list = action_list

    def collect_fv_input_mapping(self):
        ret = MapFVInput()
        for expr in self.action_list:
            ret += expr.collect_fv_input_mapping()
        return ret

    def instantiate_fvs(self, fv_value_mapping):
        return BoundedActionList(list(map(lambda x: x.instantiate_fvs(fv_value_mapping), self.action_list)))

    def __repr__(self):
        return "ActionList(%s)" % (",".join(map(lambda x: x.__repr__(), self.action_list)))


class Implies(Expr):
    # eft: Match
    # ight: ActionList

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def collect_fv_input_mapping(self):
        print("HH")
        return self.left.collect_fv_input_mapping() + self.right.collect_fv_input_mapping()

    def instantiate_fvs(self, fv_value_mapping):
        left = self.left
        right = self.right
        return BoundedImplies(left.instantiate_fvs(fv_value_mapping), right.instantiate_fvs(fv_value_mapping))

    def __repr__(self):
        return " %s  ->   %s  " % (self.left.__repr__(), self.right.__repr__())
