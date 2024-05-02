#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController, OVSKernelSwitch, UserSwitch, CPULimitedHost, Host, Node
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf, OVSLink

from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd
from mn_wifi.wmediumdConnector import interference

from subprocess import call

import sys
import os
import time
from mn_wifi.replaying import ReplayingMobility


def myNetwork(args):

    net = Mininet_wifi(topo=None, build=False, link=OVSLink, ipBase='10.0.0.0/8')

    info( '*** Adding Nodes\n' )
    c1 = net.addController(name='c1', controller=RemoteController, ip='172.17.0.2', protocol='tcp', port=6653)
    ap1 = net.addAccessPoint('ap1', cls=OVSKernelAP, protocols=["OpenFlow10"], ssid='ap1-ssid', channel='1', mode='g', ip='10.0.1.0', position='23.0,23.0,0', range='23')
    ap2 = net.addAccessPoint('ap2', cls=OVSKernelAP, protocols=["OpenFlow10"], ssid='ap2-ssid', channel='1', mode='g', ip='10.0.2.0', position='46.0,23.0,0', range='23')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, protocols=["OpenFlow10"])
    sta1 = net.addStation('sta1', ip='10.0.0.1', speed=1, position='23.0,33.0,0', range='23')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.3', defaultRoute=None)

    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=3)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    info( '*** Add links\n')
    net.addLink(s1, h1)
    net.addLink(s1, h2)
    net.addLink(s1, ap1)
    net.addLink(s1, ap2)
    
    info( '*** Mobility\n')
    net.isReplaying = True
    path = os.path.dirname(os.path.abspath(__file__)) + '/replayingMobility/'
    get_trace(sta1, '{}pic.dat'.format(path))
    if '-p' not in args:
        net.plotGraph(max_x=69, max_y=56)
    
    info( '*** Starting network\n')
    net.build()
    for controller in net.controllers:
        controller.start()
    ap1.start([c1])
    ap2.start([c1])
    s1.start([c1])
        
    info("*** Replaying Bandwidth\n")
    ReplayingMobility(net)
    
    info( '*** Commands\n')
    ap1.cmd('ifconfig ap1 10.0.1.0')
    ap2.cmd('ifconfig ap2 10.0.2.0')
    s1.cmd('ifconfig s1 10.1.0.0')
    s1.cmd('ovs-ofctl add-flow s1 action=normal')
    net.pingAll()
    

    CLI(net)
    info("*** Stopping network\n")
    net.stop()


def get_trace(sta, file_):
    file_ = open(file_, 'r')
    raw_data = file_.readlines()
    file_.close()

    sta.p = []
    pos = (-1000, 0, 0)
    sta.position = pos

    for data in raw_data:
        line = data.split()
        x = line[0]  # First Column
        y = line[1]  # Second Column
        pos = float(x), float(y), 0.0
        sta.p.append(pos)


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork(sys.argv)
