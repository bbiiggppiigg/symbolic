
from macros.actions import OutputAssignment, OutputAssignments, Range, OutputActionList
from macros.binding import InputBinding
from macros.exceptions import UnsatisfiableAssignmentException, UnsatisfiableActionException
from macros.types import Value
from macros.variables import Variable, Output

"""
    What should apply returns ?
    Need to differentiate between arbitrary and unsatisfiable
"""


class BoundedExpr(object):
    def apply(self, pkt              ):
        raise NotImplementedError


class BoundedPredicate(BoundedExpr):
    def apply(self, pkt              ):
        raise NotImplementedError;


class BoundedLEQ(BoundedPredicate):

    def __init__(self, left          , right):
        self.left = left
        self.right = right

    def get_range(self):
        if isinstance(self.left, Value):  # 3 <= X
            return [Range(self.left.get_value(), self.left.max_value)]
        if isinstance(self.right, Value):  # X <= 3
            return [Range(self.right.min_value, self.right.get_value())]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt              ):
        left = self.left
        right = self.right
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]

        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")


class BoundedGEQ(BoundedPredicate):

    def __init__(self, left          , right)        :
        self.left = left
        self.right = right

    def get_range(self):
        if isinstance(self.left, Value):  # 3 >= X
            return [Range(self.left.min_value, self.left.get_value())]
        if isinstance(self.right, Value):  # X >= 3
            return [Range(self.right.get_value(), self.right.max_value)]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt              ):
        left = self.left
        right = self.right
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]

        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")


class BoundedGT(BoundedPredicate):

    def __init__(self, left          , right)        :
        self.left = left
        self.right = right

    def get_range(self):
        if isinstance(self.left, Value):  # 3 > X
            return [Range(self.left.min_value, self.left.get_value() - 1)]
        if isinstance(self.right, Value):  # X > 3
            return [Range(self.right.get_value() + 1, self.right.max_value)]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt              ):
        left = self.left
        right = self.right
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]

        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    pass


class BoundedLT(BoundedPredicate):

    def __init__(self, left          , right)        :
        self.left = left
        self.right = right

    def get_range(self):
        if isinstance(self.left, Value):  # 3 < X
            return [Range(self.left.get_value() + 1, self.left.max_value)]
        if isinstance(self.right, Value):  # X < 3
            return [Range(self.right.min_value, self.right.get_value() - 1)]
        raise Exception("Shouldn't Reach")

    def apply(self, pkt              ):
        left = self.left
        right = self.right
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]

        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() < right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    pass


class BoundedEQ(BoundedPredicate):

    def __init__(self, left, right)        :
        self.left = left
        self.right = right

    def __repr__(self):
        return "( %s == %s )" % (self.left, self.right)

    def get_range(self):
        return [Range(self.right.get_value(), self.right.get_value())]

    def apply(self, pkt              ):

        left = self.left
        right = self.right

        #print("haha %s == %s" % (left, right))
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]
        #print("haha %s == %s" % (left, right))
        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            #print(left.get_value(), " ", right.get_value())
            return left.get_value() == right.get_value()
        else:
            print("pkt = ", pkt)
            print("left = ", left)
            print("right = ", right)
            print(type(left), type(right))
            raise Exception("Shouldn't reach here")

    pass


class BoundedNEQ(BoundedPredicate):

    def __init__(self, left, right)        :
        self.left = left
        self.right = right

    def get_range(self):
        return [Range(self.right.min_value, self.right.get_value() - 1),
                Range(self.right.get_value() + 1, self.right.max_value)]

    def apply(self, pkt              ):
        left = self.left
        right = self.right
        if left in pkt.binding.keys():
            left = pkt.binding[left]
        if right in pkt.binding.keys():
            right = pkt.binding[right]
        # print(type(right), right)
        if isinstance(left, Output) and isinstance(right, Value):
            return OutputAssignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() != right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    pass


class Bool(object):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return self.value

    def __repr__(self):
        return self.value.__repr__()


class BoundedMatch(BoundedExpr):

    def __init__(self, expr_list)        :
        self.expr_list = expr_list

    def apply(self, pkt              )        :
        ret = True
        cond_list = list(map(lambda x: x.apply(pkt), self.expr_list))
        for cond in cond_list:
            ret &= cond
        return Bool(ret)
        # return BoundedMatch(list(map(lambda x: x.apply(pkt), self.expr_list)))

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.expr_list))


"""
    Action should be a OR of ANDs, in DNF 
    (A & B & C)     
"""


class BoundedAction(BoundedExpr):

    def __init__(self, assign_list)        :
        self.assign_list = assign_list

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.assign_list))

    def apply(self, pkt              )                       :
        try:
            ret                                      = list(
                map(lambda x: x.apply(pkt), self.assign_list)
            )
            return OutputAssignments(ret)
        except UnsatisfiableAssignmentException:
            raise UnsatisfiableActionException


class BoundedGuard(BoundedExpr):

    def __init__(self, assign_list)        :
        self.assign_list = assign_list

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.assign_list))

    def apply(self, pkt              ):
        try:
            ret = list(
                map(lambda x: x.apply(pkt), self.assign_list)
            )
            return OutputActionList([OutputAssignments(ret)])
        except UnsatisfiableAssignmentException:
            raise UnsatisfiableActionException


class BoundedActionList(BoundedExpr):

    def __init__(self, action_list):
        self.action_list = action_list

    def apply(self, pkt              )                      :
        ret = []
        for action in self.action_list:
            try:
                ret.append(action.apply(pkt))
            except UnsatisfiableActionException:
                continue
        if len(ret) != 0:
            return OutputActionList(ret)
        else:
            return OutputActionList(ret, True)

    def __repr__(self):
        return "ActionList(%s)" % (",".join(map(lambda x: x.__repr__(), self.action_list)))


class BoundedImplies(BoundedExpr):
    #eft: BoundedMatch
    #ight: BoundedActionList

    def __init__(self, left              , right                   ):
        self.left = left
        self.right = right

    def apply(self, pkt              ):
        if self.left.apply(pkt):
            return self.right.apply(pkt)
        return Bool(True)

    def __repr__(self):
        return " Match( %s ) ->  Action( %s ) " % (self.left.__repr__(), self.right.__repr__())
