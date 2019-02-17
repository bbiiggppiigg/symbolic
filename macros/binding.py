import copy

from macros.types import IPAddr, Mac, Vlan, PriorityCode, IPProto, Port, TCPPort, EthType, Value
from macros.variables import Input, StateVar, SymbolicStateVar , Output , FreeVariable


class Packet(object):

    def __init__(self, ethsrc, ethdst, ethtype, ip4src, ip4dst, ipproto, vlan=None, tcpsrcport=None):
        self.ethSrc = ethsrc
        self.ethDst = ethdst
        self.ethType = ethtype
        self.ip4Src = ip4src
        self.ip4Dst = ip4dst
        self.ipProto = ipproto
        self.vlan = vlan
        self.tcpSrcPort = tcpsrcport

    @classmethod
    def get_sample(cls):
        return Packet("c6:91:00:30:db:c7", "ff:ff:ff:ff:ff:ff", 2054, "10.0.0.1", "10.0.0.2", 1)

    def __eq__(self, other):
        return (self.ethSrc == other.ethSrc and self.ethDst == other.ethDst
                and self.ethType == other.ethType and self.ip4Src == other.ip4Src
                and self.ip4Dst == other.ip4Dst and self.ipProto == other.ipProto
                and self.vlan == other.vlan and self.tcpSrcPort == other.tcpSrcPort)

    def __hash__(self):
        return (self.ethSrc.__hash__() + self.ethDst.__hash__() +
                self.ethType.__hash__() + self.ip4Src.__hash__() + self.ip4Dst.__hash__() +
                self.ipProto.__hash__() + self.vlan.__hash__() + self.tcpSrcPort.__hash__() + "Packet".__hash__())


"""
    A dictionary of mapping from input variables to their value
"""


class MapInputValue(object):

    def __init__(self, pkt, port_id, state_vars_dict ,symbolic_state_vars_dict ):
        self.mapping = dict()
        if pkt is not None:
            self.mapping[Input('ethSrc')] = Mac(pkt.ethSrc)
            self.mapping[Input('ethDst')] = Mac(pkt.ethDst)
            self.mapping[Input('ethType')] = EthType(pkt.ethType)
            self.mapping[Input('port_id')] = Port(port_id)
            if pkt.vlan is not None:
                self.mapping[Input('vlan')] = Vlan(pkt.vlan)
                self.mapping[Input('vlanPcp')] = PriorityCode(pkt.vlanPcp)

            if pkt.ip4Src is not None:
                self.mapping[Input('ip4Src')] = IPAddr(pkt.ip4Src)
                self.mapping[Input('ip4Dst')] = IPAddr(pkt.ip4Dst)
                self.mapping[Input('ipProto')] = IPProto(pkt.ipProto)

            if pkt.tcpSrcPort is not None:
                self.mapping[Input('tcpSrcPort')] = TCPPort(pkt.tcpSrcPort)
                self.mapping[Input('tcpSrcPort')] = TCPPort(pkt.tcpDstPort)

        self.state_vars_dict = state_vars_dict
        for _, sv in state_vars_dict.items():
            self.mapping[Input(sv.name)] = sv.vartype(sv.value)
        self.symbolic_state_vars_dict = symbolic_state_vars_dict

    def apply(self, expr):
        if isinstance(expr, Input):
            if expr.is_symbolic:
                ssv = self.symbolic_state_vars_dict[expr.name]
                return expr.type(ssv.get(expr.fv))
            else:
                assert expr in self.mapping
                return self.mapping[expr]
        if isinstance(expr, StateVar):
            assert expr.name in self.state_vars_dict
            sv = self.state_vars_dict[expr.name]
            return sv.vartype[sv.value]
        if isinstance(expr,Output) and expr.is_symbolic:
            print "qqqqq",expr.fv 
            pass
        return expr

"""
    A dictionary from free variables to their corresponding input variable
"""


class MapFVInput(object):

    def __init__(self, fv=None, variable=None):
        self.mapping = dict()
        if fv is not None and variable is not None:
            self.mapping[fv] = variable

    def __add__(self, other):
        ret = copy.deepcopy(self)
        for key, value in other.mapping.items():
            if key in ret.mapping:
                if ret.mapping[key] != value:
                    raise Exception("Binding Single Free Variable to Multiple Variable")
            ret.mapping[key] = value

        return ret

    def __repr__(self):
        to_print = "binding = "
        for key, value in self.mapping.items():
            to_print += ("%s,%s\t" % (key, value))
        return to_print


"""
    Filter : 
        forcing the assignment to an output_variable to be limited to some set of value
    Filter.binding = 
        dict[ OutputVariable ] -> Set( integers )
    
    Note:
    1. output variables that are not in the dict are not enforced
    2. Filter 1 + Filter 2 = union of allowed values. In other words, they should have same set of keys
    
    
"""


class Filter(object):

    def __repr__(self):
        return "Filter( %s ) " % self.binding.__repr__()

    def __init__(self, binding_dict):
        self.binding = dict()
        for key, value in binding_dict.items():
            if value is not None:
                if isinstance(value, Value):
                    self.binding[key] = {value.get_value()}
                if isinstance(value, set):
                    self.binding[key] = value
            else:
                self.binding[key] = set()
        # print "creating filter"
        # print self.binding

    def __add__(self, other):
        ret = dict()
        assert (self.binding == dict() or set(self.binding.keys()) == set(other.binding.keys()))

        for key, value in self.binding.items():
            ret[key] = value
        for key, value in other.binding.items():
            if key in ret:
                ret[key] = ret[key].union(value)
            else:
                ret[key] = value

        return Filter(ret)

    def __iadd__(self, other):

        assert (self.binding == dict() or set(self.binding.keys()) == set(other.binding.keys()))
        for key, value in other.binding.items():
            if key in self.binding:
                self.binding[key] = self.binding[key].union(value)
            else:
                self.binding[key] = value
        return self

    def __mul__(self, other):
        ret = dict()
        for key, value in self.binding.items():
            ret[key] = value
        for key, value in other.binding.items():
            if key in ret:
                ret[key] = ret[key].intersection(value)
            else:
                ret[key] = value
        return Filter(ret)

    def __imul__(self, other):
        for key, value in other.binding.items():
            if key in self.binding:
                self.binding[key] = self.binding[key].intersection(value)
            else:
                self.binding[key] = value
        return self


class MapFVValue(object):

    def __init__(self, fv_to_input_var, pkt):
        self.mapping = dict()

        for fv, input_var in fv_to_input_var.mapping.items():

            if input_var not in pkt.mapping:
                raise Exception("UnBounded Free Variable %s " % input_var)

            self.mapping[fv] = pkt.mapping[input_var]

    def __repr__(self):
        ret = ""
        for key, value in self.mapping.items():
            ret += "(%s:%s),\t" % (key, value)
        return ret

    def __eq__(self, other):
        return self.mapping == other.mapping

    def __hash__(self):
        return self.mapping.__hash__()
    
    def instantiate(self, var):
        print ("my mapping ",self.mapping)
        if isinstance(var,Input):
            if var.is_symbolic:
                return Input(var.name,self.mapping[var.fv])
        elif isinstance(var,Output):
            if var.is_symbolic:
                return Output(var.name,self.mapping[var.fv])
        elif isinstance(var,FreeVariable):
            return self.mapping[var]
        return var
