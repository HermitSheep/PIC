#!/usr/bin/python

import os
import sys

from mn_wifi.replaying import ReplayingMobility

from mininet.node import Controller, OVSKernelSwitch, Host
from mininet.log import setLogLevel, info
from mn_wifi.net import Mininet_wifi
from mn_wifi.node import Station, OVSKernelAP
from mn_wifi.cli import CLI
from mn_wifi.link import wmediumd, adhoc
from mn_wifi.wmediumdConnector import interference
from subprocess import call
#* coordinates: (x, y, z)

def myNetwork():

    net = Mininet_wifi(topo=None, build=False, link=wmediumd, wmediumd_mode=interference, ipBase='10.0.0.0/8')

    #* Controller
    info( '*** Adding controller\n' ) 
    c0 = net.addController(name='c0', controller=Controller, protocol='tcp', port=6633)

    #* Switches and APs
    info( '*** Add switches/APs\n')
    ap1 = net.addAccessPoint('ap1', range=6, cls=OVSKernelAP, ssid='ap1-ssid', mode='g', channel='1', position='10.0,10.0,0')
    ap2 = net.addAccessPoint('ap2', range=6, cls=OVSKernelAP, ssid='ap2-ssid', mode='g', channel='1', position='20.0,10.0,0')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)

    #* Station and host (internet)
    info( '*** Add hosts/stations\n')
    sta1 = net.addStation('sta1', range= 2, ip='10.0.0.1', position='15.0,15.0,0', speed=2)
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.2', defaultRoute=None, position='15.0,5.0,0')
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.3', defaultRoute=None, position='15.0,10,0')

    #* Configure Interface
    info("*** Configuring Propagation Model\n")
    net.setPropagationModel(model="logDistance", exp=4.5)

    info("*** Configuring wifi nodes\n")
    net.configureWifiNodes()

    #* Links
    info( '*** Add links\n')
    net.addLink(s1, ap1)
    net.addLink(s1, ap2)
    net.addLink(s1, h1)
    net.addLink(s1, h2)

    net.plotGraph(max_x=30, max_y=20)

    #* Mobility
    net.isReplaying = True
    path = os.path.dirname(os.path.abspath(__file__)) + '/replayingMobility/'
    get_trace(sta1, '{}pic.dat'.format(path))

    #* Starting network
    info( '*** Starting network\n')
    net.build() 
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches/APs\n')
    net.get('ap1').start([c0])
    net.get('ap2').start([c0])
    net.get('s1').start([c0])
    #? do i also need to start the host and station?

    #* do Mobility
    ReplayingMobility(net)

    info( '*** Post configure nodes\n')
    s1.cmd('sh ovs-ofctl add-flow s1 action=normal')
    ap1.cmd('sh ovs-ofctl add-flow ap1 action=normal')
    ap2.cmd('sh ovs-ofctl add-flow ap2 action=normal')

    CLI(net)
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
    setLogLevel( 'info' )
    myNetwork()

