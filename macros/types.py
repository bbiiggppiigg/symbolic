from abc import ABCMeta, abstractmethod


class Value(object):
    # def to_int(self):
    #    raise NotImplementedError("");
    __metaclass__ = ABCMeta

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

    @classmethod
    def to_output(cls, value):
        return value

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

    def __init__(self, mac_str):
        self.mac_str = mac_str
        self.value = self.to_int()
        if self.value < Mac.min_value or self.value > Mac.max_value:
            raise Exception("Invalid Mac Value : %s " % mac_str)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Mac".__hash__()

    def int_mac2str(mac):
        a0 = str(mac & 0xff)
        a1 = str((mac & 0xff00) >> 8)
        a2 = str((mac & 0xff0000) >> 16)
        a3 = str((mac & 0xff000000) >> 24)
        a4 = str((mac & 0xff00000000) >> 32)
        a5 = str((mac & 0xff0000000000) >> 40)

        return ".".join([a5, a4, a3, a2, a1, a0])

    @classmethod
    def to_output(cls, value):
        return int_mac2str(value)


class Bool(Value):
    min_value = 0
    max_value = 1

    def __init__(self, truth):
        value = 1 if truth else 0
        self.value = value

    def __bool__(self):
        return self.value == 1

    def __repr__(self):
        if self.value == 0:
            return False.__repr__()
        return True.__repr__()

    def __nonzero__(self):
        return self.value == 1


class Port(Value):
    min_value = 0
    max_value = 1024

    def __init__(self, port):
        self.value = port
        if self.value < Port.min_value or self.value > Port.max_value:
            raise Exception("Invalid Port Value : %d " % port)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        if type(other) != type(self):
            return False
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Port".__hash__()


class Vlan(Value):
    min_value = 1
    max_value = 4096

    def __init__(self, vlan):
        self.value = vlan
        if self.value < Vlan.min_value or self.value > Vlan.max_value:
            raise Exception("Invalid Vlan Value %d " % vlan)

    def __eq__(self, other):

        if type(other) != type(self):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "Vlan".__hash__()


class PriorityCode(Value):
    min_value = 1
    max_value = 8

    def __init__(self, p):
        self.value = p
        if self.value < PriorityCode.min_value or self.value > PriorityCode.max_value:
            raise Exception("Invalid Priority Code %d" % p)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "PriorityCode".__hash__()


class EthType(Value):
    min_value = -2147483648
    max_value = 2147483647

    def __init__(self, t):
        self.value = t
        if self.value < EthType.min_value or self.value > EthType.max_value:
            raise Exception("Invalid Eth Type %d " % t)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "EthType".__hash__()


class IPProto(Value):
    min_value = 0
    max_value = 255

    def __init__(self, p):
        self.value = p
        if self.value < IPProto.min_value or self.value > IPProto.max_value:
            raise Exception("Invalid IPProto %d " % p)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

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

    def __init__(self, ip_str):
        self.ip_str = ip_str
        self.value = self.to_int()
        if self.value < IPAddr.min_value or self.value > IPAddr.max_value:
            raise Exception("Invalid IP Address %s " % ip_str)

    def __eq__(self, other):
        if type(other) != type(self):
            return False
        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "IPAddr".__hash__()

    @classmethod
    def int_ip2str(cls, int_ip):
        a0 = str(int_ip & 0xff)
        a1 = str((int_ip & 0xff00) >> 8)
        a2 = str((int_ip & 0xff0000) >> 16)
        a3 = str((int_ip & 0xff000000) >> 24)

        return ".".join([a3, a2, a1, a0])

    @classmethod
    def to_output(cls, value):
        return cls.int_ip2str(value)


class TCPPort(Value):
    min_value = 0
    max_value = 65535

    def __init__(self, port):
        self.value = port
        if self.value < TCPPort.min_value or self.value > TCPPort.max_value:
            raise Exception("Invalid TCP Port %d " % port)

    def __eq__(self, other):
        if type(other) != type(self):
            return False

        return self.value == other.value

    def __hash__(self):
        return self.value.__hash__() + "TCPPort".__hash__()
