from typing import Union, List

from macros.actions import Assignment, OutputAction, Range, OutputActionList
from macros.binding import Filter, MapInputValue
from macros.exceptions import UnsatisfiableAssignmentException, UnsatisfiableActionException
from macros.types import Value, Bool
from macros.variables import Output

"""
    What should apply returns ?
    Need to differentiate between arbitrary and unsatisfiable
"""


class BoundedExpr(object):
    def apply(self, pkt):
        raise NotImplementedError


class BoundedPredicate(BoundedExpr):
    def apply(self, pkt):
        # type: (MapInputValue) -> Union[Bool,Assignment]
        raise NotImplementedError

    def get_filter(self):
        if isinstance(self.left, Output):
            return Filter({self.left: self.right})
        return Filter({})

    def get_range(self):
        # type: () -> List[Range]
        raise NotImplementedError


class BoundedLEQ(BoundedPredicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def negate(self):
        return BoundedGT(self.left, self.right)

    def get_range(self):
        if isinstance(self.left, Value):  # 3 <= X
            return [Range(self.left.get_value(), self.left.max_value)]
        if isinstance(self.right, Value):  # X <= 3
            return [Range(self.right.min_value, self.right.get_value())]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt):
        left = pkt.apply(self.left)
        right = pkt.apply(self.right)

        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")


class BoundedGEQ(BoundedPredicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def negate(self):
        return BoundedLT(self.left, self.right)

    def get_range(self):
        if isinstance(self.left, Value):  # 3 >= X
            return [Range(self.left.min_value, self.left.get_value())]
        if isinstance(self.right, Value):  # X >= 3
            return [Range(self.right.get_value(), self.right.max_value)]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt):
        left = pkt.apply(self.left)
        right = pkt.apply(self.right)
        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")


class BoundedGT(BoundedPredicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def negate(self):
        return BoundedLEQ(self.left, self.right)

    def get_range(self):
        if isinstance(self.left, Value):  # 3 > X
            return [Range(self.left.min_value, self.left.get_value() - 1)]
        if isinstance(self.right, Value):  # X > 3
            return [Range(self.right.get_value() + 1, self.right.max_value)]
        raise Exception("Shouldn't Reach")

    def __repr__(self):
        return "(%s  >  %s)" % (self.left.__repr__(), self.right.__repr__())

    def apply(self, pkt):
        # type:(MapInputValue) -> Union[Assignment,bool]
        left = pkt.apply(self.left)
        right = pkt.apply(self.right)
        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() > right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    pass


class BoundedLT(BoundedPredicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def negate(self):
        return BoundedGEQ(self.left, self.right)

    def get_range(self):
        # type:() -> List[Range]
        if isinstance(self.left, Value):  # 3 < X
            return [Range(self.left.get_value() + 1, self.left.max_value)]
        if isinstance(self.right, Value):  # X < 3
            return [Range(self.right.min_value, self.right.get_value() - 1)]
        raise Exception("Shouldn't Reach")

    def apply(self, pkt):
        # type: (MapInputValue) -> Union[Assignment,bool]

        left = pkt.apply(self.left)
        right = pkt.apply(self.right)
        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() < right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    pass


class BoundedEQ(BoundedPredicate):

    def __init__(self, left, right):
        self.left = left
        self.right = right

    def negate(self):
        return BoundedNEQ(self.left, self.right)

    def __repr__(self):
        return "( %s == %s )" % (self.left, self.right)

    def get_range(self):
        # type:() -> List[Range]
        return [Range(self.right.get_value(), self.right.get_value())]

    def apply(self, pkt):
        # type:(MapInputValue) -> Union[Assignment,bool]
        left = pkt.apply(self.left)
        right = pkt.apply(self.right)

        # print("haha %s == %s" % (left, right))
        # print pkt.binding.keys()
        """
        if isinstance(left, Input) and left in pkt.binding.keys():
            left = pkt.binding[left]
        if isinstance(right, Input) and right in pkt.binding.keys():
            right = pkt.binding[right]
        """
        # print("haha %s == %s" % (left, right))
        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            # print(left.get_value(), " ", right.get_value())
            return left.get_value() == right.get_value()
        else:
            print("pkt = ", pkt)
            print("left = ", left)
            print("right = ", right)
            print(type(left), type(right))
            raise Exception("Shouldn't reach here")

    pass


class BoundedNEQ(BoundedPredicate):

    def __init__(self, left, right):
        
        self.left = left
        self.right = right
        print self

    def get_range(self):
        # type:() -> List[Range]
        try:
            r1 = [Range(self.right.min_value, self.right.get_value() - 1)]
        except:
            r1 = []
        try:
            r2 = [Range(self.right.get_value() + 1, self.right.max_value)]
        except:
            r2 = []
        if r1 + r2 == []:
            Range(1,-1)
        return r1 + r2
    def apply(self, pkt):
        # type:(MapInputValue) -> Union[Assignment,bool]

        left = pkt.apply(self.left)
        right = pkt.apply(self.right)
        # print(type(right), right)
        if isinstance(left, Output) and isinstance(right, Value):
            return Assignment(left, self.get_range())
        elif isinstance(left, Value) and isinstance(right, Value):
            return left.get_value() != right.get_value()
        else:
            raise Exception("Shouldn't reach here")

    def negate(self):
        return BoundedEQ(self.left, self.right)

    def __repr__(self):
        return "BoundedNEQ( %s , %s )"  % (self.left.__repr__() , self.right.__repr__()) 
    pass


"""
class Bool(object):
    def __init__(self, value):
        self.value = value

    def __bool__(self):
        return self.value == True

    def __repr__(self):
        return self.value.__repr__()

    def __nonzero__(self):
        return self.value
"""


class BoundedMatch(BoundedExpr):

    def __init__(self, expr_list):
        self.expr_list = expr_list

    def apply(self, pkt):
        ret = True
        cond_list = list(map(lambda x: x.apply(pkt), self.expr_list))
        for cond in cond_list:
            ret &= cond
        return Bool(ret)
        # return BoundedMatch(list(map(lambda x: x.apply(pkt), self.expr_list)))

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.expr_list))


class BoundedAnd(BoundedExpr):

    def __init__(self, bplist, index=-1):
        # type:(List[BoundedPredicate],int) -> None
        self.bplist = bplist
        self.index = index

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.bplist))

    def apply(self, pkt):
        try:
            ret = list(
                map(lambda x: x.apply(pkt), self.bplist)
            )
            return OutputAction(ret)
        except UnsatisfiableAssignmentException:
            raise UnsatisfiableActionException

    def get_filter(self):
        # type:() -> Filter
        assert self.index < len(self.bplist)
        return self.bplist[self.index].get_filter()


"""
    Action should be a OR of ANDs, in DNF 
    (A & B & C)     
"""


class BoundedAction(BoundedExpr):

    def __init__(self, assign_list):
        self.assign_list = assign_list

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.assign_list))

    def apply(self, pkt):
        try:
            ret = list(
                map(lambda x: x.apply(pkt), self.assign_list)
            )
            return OutputAction(ret)
        except UnsatisfiableAssignmentException:
            raise UnsatisfiableActionException

    def get_filter(self):
        assert len(self.assign_list) == 1
        return self.assign_list[0].get_filter()


class BoundedGuard(BoundedExpr):

    def __init__(self, assign_list):
        self.assign_list = assign_list

    def __repr__(self):
        return "".join(map(lambda x: x.__repr__(), self.assign_list))

    def apply(self, pkt):
        try:
            ret = list(
                map(lambda x: x.apply(pkt), self.assign_list)
            )
            return OutputActionList([OutputAction(ret)])
        except UnsatisfiableAssignmentException:
            raise UnsatisfiableActionException


class BoundedActionList(BoundedExpr):

    def __init__(self, action_list):
        # type: (List[BoundedAction]) -> None
        self.action_list = action_list

    def get_filter(self):
        # type: () -> Filter
        assert len(self.action_list) == 1
        return self.action_list[0].get_filter()

    def apply(self, pkt):
        # type: (MapInputValue) -> OutputActionList
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

    def __init__(self, left, right):
        # type:(BoundedMatch,BoundedActionList) -> None
        self.left = left
        self.right = right

    def apply(self, pkt):
        # type:(MapInputValue) -> Union[Bool,OutputActionList]
        # print "bounded implies", self.left , self.right
        # print "left true ? ",self.left.apply(pkt)
        if self.left.apply(pkt):
            return self.right.apply(pkt)
        # print "returning true"
        return Bool(True)

    def __repr__(self):
        return " Match( %s ) ->  Action( %s ) " % (self.left.__repr__(), self.right.__repr__())
