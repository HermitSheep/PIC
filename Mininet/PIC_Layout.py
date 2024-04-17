#!/usr/bin/python

from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference
from subprocess import call


def myNetwork():

    net = Mininet_wifi(topo=None,
                       build=False,
                       link=wmediumd,
                       wmediumd_mode=interference,
                       ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    c0 = net.addController(name='c0',
                           controller=Controller,
                           protocol='tcp',
                           port=6633)

    info( '*** Add switches/APs\n')
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, listenPort=6633, ssid='ap1-ssid',
                             channel='1', mode='g', ip='10.0.1.0', position='204.0,188.0,0')
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, listenPort=6633, dpid='DPID_A2', ssid='ap2-ssid',
                             channel='1', mode='g', ip='10.0.2.0', position='671.0,174.0,0')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, listenPort=6633, dpid='DPID_S1')

    info( '*** Add hosts/stations\n')
    sta1 = net.addStation('sta1', ip='10.0.0.1',
                           position='200.0,27.0,0')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.3', defaultRoute=None)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, ap2)
    net.addLink(ap1, s1)

    net.plotGraph(max_x=1000, max_y=1000)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')
    net.get('ap1').start([])
    net.get('ap2').start([])
    net.get('s1').start([c0])

    info( '*** Post configure nodes\n')
    ap1.cmd('ifconfig ap1 10.0.1.0')
    ap2.cmd('ifconfig ap2 10.0.2.0')
    s1.cmd('ifconfig s1 10.1.0.0')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel( 'info' )
    myNetwork()

