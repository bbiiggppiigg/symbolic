from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from builtins import super

from macros.exceptions import UnexpectedInputException, UnexpectedOutputException, DuplicateNameException
from macros.types import IPAddr, IPProto, Mac, Port, EthType


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

    def __init__(self, name):
        if name not in Input.builtin:
            raise UnexpectedInputException("expecting input, get %s" % name)
        super().__init__(name)
        self.type = self.builtin[self.name]

    def __repr__(self):
        return ("input(%s)" % self.name)

    @classmethod
    def add_var(cls, name, vartype):
        if name in cls.builtin:
            raise UnexpectedInputException("declaring duplicate input %s" % name)
        cls.builtin[name] = vartype

    pass


class Output(Variable):
    builtin = {"ip4Src_out": IPAddr, "ip4Dst_out": IPAddr, "ethSrc_out": Mac
        , "ethDst_out": Mac, "ipProto_out": IPProto, "port_id_out": Port}

    def __init__(self, name):
        if name not in self.builtin:
            raise UnexpectedOutputException("expecting output, get %s" % name)
        super().__init__(name)
        self.type = self.builtin[self.name]

    def __repr__(self):
        return "output(%s)" % self.name

    @classmethod
    def add_var(cls, name, vartype):
        if name in cls.builtin:
            raise UnexpectedInputException("declaring duplicate input %s" % name)
        cls.builtin[name] = vartype

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


class FreeVariable(Variable):
    builtin = {"IPAddr": IPAddr, "Mac": Mac, "IPProto": IPProto, "Port": Port}

    def __init__(self, name, type_str):
        if name in Input.builtin.keys() or name in Output.builtin.keys():
            raise DuplicateNameException("expecting free variable, get %s" % name)
        super().__init__(name)
        self.type_str = type_str
        self.type = self.builtin[type_str]

    def __repr__(self):
        return "fv(%s,%s)" % (self.name, self.type_str)

    pass
