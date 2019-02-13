from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from builtins import super

from macros.exceptions import UnexpectedInputException, UnexpectedOutputException, DuplicateNameException
from macros.types import IPAddr, IPProto, Mac, Port, EthType , Bool


class Variable(object):
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name

    @property
    def __hash__(self):
        return self.name.__hash__

    pass


class Input(Variable):
    builtin = {"ip4Src": IPAddr, "ip4Dst": IPAddr, "ethType": EthType, "ethSrc": Mac, "ethDst": Mac, "ipProto": IPProto,
               "port_id": Port}
    symbolics = set()
    def __init__(self, name , fv = None):
        if name not in Input.builtin:
            raise UnexpectedInputException("expecting input, get %s" % name)
        super().__init__(name)
        self.type = self.builtin[self.name]
        self.is_symbolic = True if name in Input.symbolics else False
        if self.is_symbolic:
            assert fv is not None
        self.fv =fv

    def __repr__(self):
        return ("input(%s)" % self.name)

    @classmethod
    def add_var(cls, name, vartype , is_symbolic = False):
        if name in cls.builtin:
            raise UnexpectedInputException("declaring duplicate input %s" % name)
        cls.builtin[name] = vartype
        if is_symbolic:
            cls.symbolics.add(name)

    pass


class Output(Variable):
    builtin = {"ip4Src_out": IPAddr, "ip4Dst_out": IPAddr, "ethSrc_out": Mac
        , "ethDst_out": Mac, "ipProto_out": IPProto, "port_id_out": Port}
    symbolics = set()
    def __init__(self, name ,fv = None):
        if name not in self.builtin:
            raise UnexpectedOutputException("expecting output, get %s" % name)
        super().__init__(name)
        self.type = self.builtin[self.name]
        self.is_symbolic = True if name in Output.symbolics else False
        if self.is_symbolic:
            assert fv is not None
        self.fv = fv

    def __repr__(self):
        return "output(%s)" % self.name

    @classmethod
    def add_var(cls, name, vartype , is_symbolic = False):
        if name in cls.builtin:
            raise UnexpectedInputException("declaring duplicate input %s" % name)
        cls.builtin[name] = vartype
        if is_symbolic:
            cls.symbolics.add(name)
    pass


class StateVar(Variable):

    def __init__(self, name, vartype, init_value):
        print("creating state var", name, vartype, init_value)
        Input.add_var(name, vartype)
        Output.add_var(name + "_out", vartype)
        super().__init__(name)
        self.value = init_value
        self.vartype = vartype

    def update_value(self, value):
        self.value = value

"""
    name : Learnt [Mac] -> Bool 
    default : False
    SymbolicStateVar(Learnt,Mac,Bool,false)
"""
class SymbolicStateVar(Variable):
    def __init__(self,name,domain_type,var_type,init_value):
        super().__init__(name)
        self.value = dict()
        self.name = name
        self.domain_type = domain_type
        self.init_value = init_value
        Input.add_var(name,var_type , True)
        Output.add_var(name +"_out", var_type , True)
    
    def get(x):
        assert type(x) == self.domain_type
        if x in self.value:
            return self.value[x]
        return self.init_value

    def update_value(self,x,value):
        self.value[x] = value




class FreeVariable(Variable):
    builtin = {"IPAddr": IPAddr, "Mac": Mac, "IPProto": IPProto, "Port": Port , "Bool" : Bool}

    def __init__(self, name, type_str):
        if name in Input.builtin.keys() or name in Output.builtin.keys():
            raise DuplicateNameException("expecting free variable, get %s" % name)
        super().__init__(name)
        self.type_str = type_str
        self.type = self.builtin[type_str]

    def __repr__(self):
        return "fv(%s,%s)" % (self.name, self.type_str)

    pass
