
from macros.exceptions import InvalidRangeException, UnsatisfiableAssignmentException, UnsatisfiableActionException
from macros.variables import Output, Variable


class Range(object):

    def __init__(self, min_value, max_value, care=True):
        if min_value > max_value:
            raise InvalidRangeException

        self.min_value = min_value
        self.max_value = max_value
        self.care = care

    def __mul__(self, other):
        new_min = self.min_value if self.min_value > other.min_value else other.min_value
        new_max = self.max_value if self.max_value < other.max_value else other.max_value

        return Range(new_min, new_max, self.care or other.care)

    def __imul__(self, other):
        new_min = self.min_value if self.min_value > other.min_value else other.min_value
        new_max = self.max_value if self.max_value < other.max_value else other.max_value
        self.min_value = new_min
        self.max_value = new_max
        self.care |= other.care

    def __repr__(self):
        return "[%d,%d]" % (self.min_value, self.max_value)


# Port = [[1,3] | [4,6] | [7,9]  ]

class OutputAssignment(object):
    def __init__(self, left        , right):
        if len(right) == 0:
            raise UnsatisfiableAssignmentException
        self.left = left
        self.ranges = right

        print("Creating Output Assignment , left = %s , right = %s\n" % (left, self.ranges))

    def __mul__(self, other):
        if self.left.name != other.left.name:
            raise Exception("Jointing Assignment to Different variables %s and %s" % (self.left.name, self.right.name))
        ret = []
        for mine in self.ranges:
            for its in other.ranges:
                try:
                    #print(mine, its)
                    combined = mine * its
                    ret.append(combined)
                except InvalidRangeException:
                    continue

        if len(ret) == 0:
            raise UnsatisfiableAssignmentException

        return OutputAssignment(self.left, ret)

    def __imul__(self, other):
        if self.left.name != other.left.name:
            raise Exception("Jointing Assignment to Different variables %s and %s" % (self.left.name, self.right.name))
        ret = []
        for mine in self.ranges:
            for its in self.ranges:
                try:
                    combined = mine * its
                    ret.append(combined)
                except InvalidRangeException as e:
                    print(e)
        if len(ret) == 0:
            raise UnsatisfiableAssignmentException

        self.ranges = ret

    def __repr__(self):
        return " %s  =  %s " % (self.left.name, self.ranges)


"""
    (Port_out = 5, True) and (IpProto_out = 2,False) and , ...    
"""


class OutputAssignments(object):
    default_list = dict()
    #ey: str
    #alue: Variable


    # for key, value in Input.builtin.items():
    #    default_list[key] = Range(value.min_value, value.max_value, False)

    def __init__(self, assignment_list):

        satisfiable = True
        print("assignment lists = ", assignment_list)
        bool_consts = filter(lambda x: type(x) == bool, assignment_list)

        for bool_const in bool_consts:
            satisfiable &= bool_const
            if not satisfiable:
                # print("Unsatisfiable Output Assignment")
                raise UnsatisfiableAssignmentException

        assignment_list                         = list(filter(lambda x: type(x) != bool, assignment_list))
        res                                 = dict()
        # Collapsing Output Assignment in the same List
        for assignment in assignment_list:
            try:
                if assignment.left not in res:
                    res[assignment.left] = assignment
                else:
                    res[assignment.left] = res[assignment.left] * assignment
            except UnsatisfiableAssignmentException:
                raise UnsatisfiableActionException

        self.assignment_dict = res
        # print(self.assignment_dict)

    """
        Assume no duplicate range for same input
    """

    def __mul__(self, other)                       :
        ret = dict()

        try:
            for my_output, my_assign in self.assignment_dict.items():
                ret[my_output] = my_assign

            for its_output, its_assign in other.assignment_dict.items():
                if its_output in ret:
                    #print("Case 1")
                    #print(ret[its_output], its_assign)
                    ret[its_output] = ret[its_output] * its_assign
                    #print(ret[its_output])
                else:
                    #print("Case 2")
                    ret[its_output] = its_assign
        except UnsatisfiableAssignmentException:
            #print("QQ")
            raise UnsatisfiableActionException

        return OutputAssignments(list(ret.values()))

    def __repr__(self):
        if self.assignment_dict:
            return "(%s) " % (self.assignment_dict)
        return "True"


pass


class OutputActionList(object):

    def __init__(self, assignment_list, unsat=False):
        self.assignment_list = assignment_list
        self.unsat = unsat

    def __repr__(self):
        # print(len(self.assignment_list))
        # print(len(self.assignment_list))
        return "output action list [%s]" % ("".join(map(lambda x: x.__repr__(), self.assignment_list)))

    def __mul__(self, other):

        mine = self.assignment_list
        its = other.assignment_list

        ret = []
        if self.unsat or other.unsat:
            return OutputActionList([], True)
        if len(mine) == 0:
            return OutputActionList(its)
        if len(its) == 0:
            return OutputActionList(mine)

        for my in mine:
            for it in its:
                try:
                    ret.append(my * it)
                except UnsatisfiableActionException:
                    continue

        return OutputActionList(ret)

    def __imul__(self, other):
        mine = self.assignment_list
        its = other.assignment_list
        ret = []

        self.unsat |= other.unsat
        if self.unsat:
            return

        for my in mine:
            for it in its:
                try:
                    ret.append(my * it)
                except UnsatisfiableAssignmentException:
                    pass
        self.assignment_list = ret
