from macros.types import IPAddr, Mac, Vlan, PriorityCode, IPProto, Port, TCPPort, EthType
import copy

from macros.variables import Input, FreeVariable, Variable


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

    def __eq__(self, other: "Packet"):
        return (self.ethSrc == other.ethSrc and self.ethDst == other.ethDst
                and self.ethType == other.ethType and self.ip4Src == other.ip4Src
                and self.ip4Dst == other.ip4Dst and self.ipProto == other.ipProto
                and self.vlan == other.vlan and self.tcpSrcPort == other.tcpSrcPort)

    def __hash__(self):
        return (self.ethSrc.__hash__() + self.ethDst.__hash__() +
                self.ethType.__hash__() + self.ip4Src.__hash__() + self.ip4Dst.__hash__() +
                self.ipProto.__hash__() + self.vlan.__hash__() + self.tcpSrcPort.__hash__() + "Packet".__hash__())


class InputBinding(object):

    def __init__(self, pkt, port_id: int):
        self.binding = dict()
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


class FVS(object):

    def __init__(self, fv: FreeVariable = None, variable: Variable = None):
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
    Binding :
    X -> SrcMac
    P -> Port

    Packet:
    SrcMac -> "ff:ff:ff:00:00:00"
    Port -> 100
"""


class Configuration(object):

    def __init__(self, binding: FVS, pkt: InputBinding):
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
