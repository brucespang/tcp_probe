import unittest
import tcp_probe

class TestParseTCPProbe(unittest.TestCase):
    def test_parse_line(self):
        line = "           iperf3-3829  [003] .... 1892945.576997: tcp_probe: src=10.0.1.1:58760 dest=10.0.0.1:5201 mark=0x0 data_len=0 snd_nxt=0x35a5a298 snd_una=0x35a4a298 snd_cwnd=10 ssthresh=2147483647 snd_wnd=65536 srtt=105 rcv_wnd=65536 sock_cookie=ab41"
        parsed = tcp_probe.parser.parse_tcp_probe_line(line)
        self.assertEqual(parsed['timestamp'], 1892945.576997)
        self.assertEqual(parsed['src'], '10.0.1.1:58760')
        self.assertEqual(parsed['dest'], '10.0.0.1:5201')
        self.assertEqual(parsed['mark'], 0)
        self.assertEqual(parsed['data_len'], 0)
        self.assertEqual(parsed['snd_nxt'], 900047512)
        self.assertEqual(parsed['snd_una'], 899981976)
        self.assertEqual(parsed['snd_cwnd'], 10)
        self.assertEqual(parsed['ssthresh'], 2147483647)
        self.assertEqual(parsed['snd_wnd'], 65536)
        self.assertEqual(parsed['srtt'], 105)
        self.assertEqual(parsed['rcv_wnd'], 65536)
        self.assertEqual(parsed['sock_cookie'], "ab41")

    def test_parse_with_extra_field(self):
        line = "           iperf3-3829  [003] .... 1892945.576997: tcp_probe: src=10.0.1.1:58760 dest=10.0.0.1:5201 mark=0x0 data_len=0 snd_nxt=0x35a5a298 snd_una=0x35a4a298 snd_cwnd=10 ssthresh=2147483647 snd_wnd=65536 srtt=105 rcv_wnd=65536 sock_cookie=ab41 test=test"
        parsed = tcp_probe.parser.parse_tcp_probe_line(line)
        self.assertEqual(parsed['test'], 'test')


class TestParseRetransmitSKB(unittest.TestCase):
    def test_parse_line(self):
        line = "          <idle>-0     [008] ..s2 1892947.095690: tcp_retransmit_skb: sport=58760 dport=5201 saddr=10.0.1.1 daddr=10.0.0.1 saddrv6=::ffff:10.0.1.1 daddrv6=::ffff:10.0.0.1 state=TCP_ESTABLISHED"
        parsed = tcp_probe.parser.parse_tcp_retransmit_skb_line(line)
        self.assertEqual(parsed['timestamp'], 1892947.095690)
        self.assertEqual(parsed['sport'], 58760)
        self.assertEqual(parsed['dport'], 5201)
        self.assertEqual(parsed['saddr'], '10.0.1.1')
        self.assertEqual(parsed['daddr'], '10.0.0.1')
        self.assertEqual(parsed['saddrv6'], '::ffff:10.0.1.1')
        self.assertEqual(parsed['daddrv6'], '::ffff:10.0.0.1')
        self.assertEqual(parsed['state'], 'TCP_ESTABLISHED')
        
        
if __name__ == '__main__':
    unittest.main()
