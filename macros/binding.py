import copy

from macros.types import IPAddr, Mac, Vlan, PriorityCode, IPProto, Port, TCPPort, EthType
from macros.variables import Input


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


class InputBinding(object):

    def __init__(self, pkt, port_id, state_var_list):
        self.binding = dict()
        if pkt is not None:
            self.binding[Input('ethSrc')] = Mac(pkt.ethSrc)
            self.binding[Input('ethDst')] = Mac(pkt.ethDst)
            self.binding[Input('ethType')] = EthType(pkt.ethType)
            self.binding[Input('port_id')] = Port(port_id)
            if pkt.vlan is not None:
                self.binding[Input('vlan')] = Vlan(pkt.vlan)
                self.binding[Input('vlanPcp')] = PriorityCode(pkt.vlanPcp)

            if pkt.ip4Src is not None:
                self.binding[Input('ip4Src')] = IPAddr(pkt.ip4Src)
                self.binding[Input('ip4Dst')] = IPAddr(pkt.ip4Dst)
                self.binding[Input('ipProto')] = IPProto(pkt.ipProto)

            if pkt.tcpSrcPort is not None:
                self.binding[Input('tcpSrcPort')] = TCPPort(pkt.tcpSrcPort)
                self.binding[Input('tcpSrcPort')] = TCPPort(pkt.tcpDstPort)

        for _, sv in state_var_list:
            self.binding[Input(sv.name)] = sv.vartype(sv.value)


"""
    A dictionary from free variables to their corresponding input variable
"""


class FVS(object):

    def __init__(self, fv=None, variable=None):
        self.binding = dict()
        if fv is not None and variable is not None:
            self.binding[fv] = variable

    def __add__(self, other):
        ret = copy.deepcopy(self)
        for key, value in other.binding.items():
            if key in ret.binding:
                if ret.binding[key] != value:
                    raise Exception("Binding Single Free Variable to Multiple Variable")
            ret.binding[key] = value

        return ret

    def __repr__(self):
        to_print = "binding = "
        for key, value in self.binding.items():
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
                self.binding[key] = {value.get_value()}
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


class Configuration(object):

    def __init__(self, binding, pkt):
        self.binding = dict()

        for key, value in binding.binding.items():

            if value not in pkt.binding:
                raise Exception("UnBounded Free Variable %s " % value)
            self.binding[key] = pkt.binding[value]

    def __repr__(self):
        ret = ""
        for key, value in self.binding.items():
            ret += "(%s:%s),\t" % (key, value)
        return ret

    def __eq__(self, other):
        return self.binding == other.binding

    def __hash__(self):
        return self.binding.__hash__()
