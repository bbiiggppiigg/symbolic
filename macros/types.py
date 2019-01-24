from abc import ABC, abstractmethod


class Value(ABC):
    # def to_int(self):
    #    raise NotImplementedError("");
    @property
    @classmethod
    @abstractmethod
    def min_value(cls):
        return NotImplementedError

    @property
    @classmethod
    @abstractmethod
    def max_value(cls):
        return NotImplementedError

    def get_value(self):
        return self.value

    def __repr__(self):
        return "%s" % self.value

    pass


class Mac(Value):
    # min_value = "00:00:00:00:00:00"
    # max_value = "ff:ff:ff:ff:ff:ff"
    min_value = 0
    max_value = 281474976710655

    def to_int(self):
        byte_array = self.mac_str.split(":")
        res = 0
        for byte in byte_array:
            res *= 256
            res += int(byte, 16)
        return res

    def __init__(self, mac_str: str):
        self.mac_str = mac_str
        self.value = self.to_int()
        if self.value < Mac.min_value or self.value > Mac.max_value:
            raise Exception("Invalid Mac Value : %s " % mac_str)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Mac".__hash__()


class Port(Value):
    min_value = 1
    max_value = 1024

    def __init__(self, port: int):
        self.value = port
        if self.value < Port.min_value or self.value > Port.max_value:
            raise Exception("Invalid Port Value : %d " % port)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Port".__hash__()


class Vlan(Value):
    min_value = 1
    max_value = 4096

    def __init__(self, vlan: int):
        self.value = vlan
        if self.value < Vlan.min_value or self.value > Vlan.max_value:
            raise Exception("Invalid Vlan Value %d " % vlan)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Vlan".__hash__()


class PriorityCode(Value):
    min_value = 1
    max_value = 8

    def __init__(self, p: int):
        self.value = p
        if self.value < PriorityCode.min_value or self.value > PriorityCode.max_value:
            raise Exception("Invalid Priority Code %d" % p)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "PriorityCode".__hash__()


class EthType(Value):
    min_value = -2147483648
    max_value = 2147483647

    def __init__(self, t: int):
        self.value = t
        if self.value < EthType.min_value or self.value > EthType.max_value:
            raise Exception("Invalid Eth Type %d " % t)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "EthType".__hash__()


class IPProto(Value):
    min_value = 0
    max_value = 255

    def __init__(self, p: int):
        self.value = p
        if self.value < IPProto.min_value or self.value > IPProto.max_value:
            raise Exception("Invalid IPProto %d " % p)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "IPProto".__hash__()


class IPAddr(Value):
    min_value = 0
    max_value = 4294967295

    def to_int(self):
        byte_array = self.ip_str.split(".")
        res = 0
        for byte in byte_array:
            res *= 256
            res += int(byte)
        return res

    def __init__(self, ip_str: str):
        self.ip_str = ip_str
        self.value = self.to_int()
        if self.value < IPAddr.min_value or self.value > IPAddr.max_value:
            raise Exception("Invalid IP Address %s " % ip_str)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "IPAddr".__hash__()


class TCPPort(Value):
    min_value = 0
    max_value = 65535

    def __init__(self, port: int):
        self.value = port
        if self.value < TCPPort.min_value or self.value > TCPPort.max_value:
            raise Exception("Invalid TCP Port %d " % port)

    def __eq__(self, other):
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "TCPPort".__hash__()
