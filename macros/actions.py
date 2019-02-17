import random

from macros.binding import Filter
from macros.exceptions import InvalidRangeException, UnsatisfiableAssignmentException, UnsatisfiableActionException
from macros.variables import Output

class Range(object):

    def __init__(self, min_value, max_value, care=True):
        if min_value > max_value:
            raise InvalidRangeException

        self.min_value = min_value
        self.max_value = max_value
        self.care = care
        self.concrete = set(range(min_value, max_value + 1))

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
        self.concrete = set(range(self.min_value, self.max_value + 1))

    def __repr__(self):
        return "[%d,%d]" % (self.min_value, self.max_value)

    def get_action(self):
        # return random.randrange(self.min_value, self.max_value + 1)
        print self.concrete
        return random.choice(tuple(self.concrete))


    def filter_output(self, values):
        ret = self.concrete.intersection(values)

        print "after filter",self.concrete 
        if ret == set():
            raise InvalidRangeException
        return ret


class FilteredRange(object):

    def __init__(self, concrete):

        self.concrete = concrete

    def __mul__(self, other):
        return FilteredRange(self.concrete.intersection(other.concrete))

    def __imul__(self, other):
        self.concrete = self.concrete.intersection(other.concrete)

    def __repr__(self):
        return " %s " % (self.concrete)

    def get_action(self):
        # return random.randrange(self.min_value, self.max_value + 1)
        return random.choice(tuple(self.concrete.intersection(values)))



    def filter_output(self, values):
        ret = self.concrete.intersection(values)
        if ret == set():
            raise InvalidRangeException
        return ret


# Port = [[1,3] | [4,6] | [7,9]  ]

class OutputAssignment(object):
    
    def get_filter(self):
        denied = set()
        for myrange in self.ranges:
            denied = denied.union(myrange.concrete)
        universe = set(range(Output.builtin[self.left.name].min_value,Output.builtin[self.left.name].max_value+1))
        allowed  =  universe- denied
        ret = dict()
        ret[self.left]=allowed
        return Filter(ret)

    def __init__(self, left, right):
        if len(right) == 0:
            raise UnsatisfiableAssignmentException
        self.left = left
        self.ranges = right

        # print("Creating Output Assignment , left = %s , right = %s\n" % (left, self.ranges))

    def filter_output(self, values):
        ret = []
        for myrange in self.ranges:
            try:
                filtered_range = myrange.filter_output(values)
                ret.append(myrange)
            except InvalidRangeException:
                continue
        if len(ret) == 0:
            raise UnsatisfiableAssignmentException
        
        return OutputAssignment(self.left,ret)

    def get_action(self):
        #print self.ranges[0].get_action()
        return Output.builtin[self.left.name].to_output(random.choice(self.ranges).get_action())

    def __mul__(self, other):
        if self.left.name != other.left.name:
            raise Exception("Jointing Assignment to Different variables %s and %s" % (self.left.name, self.right.name))
        ret = []
        for mine in self.ranges:
            for its in other.ranges:
                try:
                    # print(mine, its)
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
        if self.left.is_symbolic:
            return " %s[%s]  =  %s " % (self.left.name,self.left.fv.__repr__(), self.ranges)
        return " %s  =  %s " % (self.left.name, self.ranges)


"""
    (Port_out = 5, True) and (IpProto_out = 2,False) and , ...    
    Corresponds to a single action
"""


class OutputAssignments(object):
    default_list = dict()

    def get_filter(self):
        assert (len(self.assignment_dict.keys()) == 1)
        return self.assignment_dict[self.assignment_dict.keys()[0]].get_filter()

    def filter_output(self, action_filter):
        ret = list() 
        for key, value in self.assignment_dict.items():
            try:
                if key in action_filter.binding:
                    ret.append(value.filter_output(action_filter.binding[key]))
                else:
                    ret.append(value)
            except UnsatisfiableAssignmentException:
                raise UnsatisfiableActionException

        return OutputAssignments(ret)
    # ey: str
    # alue: Variable

    # for key, value in Input.builtin.items():
    #    default_list[key] = Range(value.min_value, value.max_value, False)

    def get_action(self):
        # print "calling get action in oas "
        ret = dict()
        # print self.assignment_dict
        for out, assign in self.assignment_dict.items():
            ret[out.name] = assign.get_action()
        
        indices = dict()
        for out in self.assignment_dict.keys():
            if out.is_symbolic:
               indices[out.name] = out.fv
        return ret , indices

    def __init__(self, assignment_list):

        satisfiable = True
        # print("assignment lists = ", assignment_list)
        bool_consts = filter(lambda x: type(x) == bool, assignment_list)

        for bool_const in bool_consts:
            satisfiable &= bool_const
            if not satisfiable:
                # print("Unsatisfiable Output Assignment")
                raise UnsatisfiableAssignmentException

        assignment_list = list(filter(lambda x: type(x) != bool, assignment_list))
        res = dict()
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

    def __mul__(self, other):
        ret = dict()

        try:
            for my_output, my_assign in self.assignment_dict.items():
                ret[my_output] = my_assign

            for its_output, its_assign in other.assignment_dict.items():
                if its_output in ret:
                    # print("Case 1")
                    # print(ret[its_output], its_assign)
                    ret[its_output] = ret[its_output] * its_assign
                    # print(ret[its_output])
                else:
                    # print("Case 2")
                    ret[its_output] = its_assign
        except UnsatisfiableAssignmentException:
            # print("QQ")
            raise UnsatisfiableActionException

        return OutputAssignments(list(ret.values()))

    def __repr__(self):
        if self.assignment_dict:
            return "(%s) " % (self.assignment_dict)
        return "True"


pass


class OutputActionList(object):

    def get_filter(self):
        assert (len(self.assignment_list)==1)
        return self.assignment_list[0].get_filter()

    def filter_output(self, action_filter):
        if self.unsat:
            return self
        if len(self.assignment_list) ==0 :
            return self

        ret = []
        unsat = True
        for output_action in self.assignment_list:
            try:
                filtered_action = output_action.filter_output(action_filter)
                ret.append(filtered_action)
                unsat = False
            except UnsatisfiableActionException:
                continue

        return OutputActionList(ret, unsat)

    def __init__(self, assignment_list, unsat=False):
        self.assignment_list = assignment_list
        self.unsat = unsat

    def get_action(self):
        # return port assignment (if presents) as well as other actions
        assert (self.unsat is False)

        print
        "my assign list ", self.assignment_list
        if len(self.assignment_list) == 0:
            return dict()
        return random.choice(self.assignment_list).get_action()

    def __repr__(self):
        # print(len(self.assignment_list))
        # print(len(self.assignment_list))
        return "output action list [%s]" % ("".join(map(lambda x: x.__repr__(), self.assignment_list)))

    def __mul__(self, other):
        mine = self.assignment_list
        its = other.assignment_list
        print "mutiplying two", mine , its
        ret = []
        if self.unsat or other.unsat:
            return OutputActionList([], True)
        if len(mine) == 0:
            return OutputActionList(its, other.unsat)
        if len(its) == 0:
            return OutputActionList(mine, mine.unsat)
        unsat = True
        for my in mine:
            for it in its:
                try:
                    one = my * it
                    unsat = False
                    ret.append(one)
                except UnsatisfiableActionException:
                    continue

        return OutputActionList(ret, unsat)

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
