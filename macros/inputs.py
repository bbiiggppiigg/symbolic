from macros.binding import Packet

pkt = Packet("c6:91:00:30:db:c7", "ff:ff:ff:ff:ff:ff", 2054, "10.0.0.1", "10.0.0.2", 1)
pkt2 = Packet("01:02:03:04:05:06", "c6:91:00:30:db:c7", 2054, "10.0.0.2", "10.0.0.1", 1)
pkt3 = Packet("c6:91:00:30:db:c7", "ff:ff:ff:ff:ff:ff", 2054, "127.0.0.1", "10.0.0.2", 1)
port_id = 10

input_sequence = [(pkt, 1), (pkt, 2), (pkt3, 10)]
