# fastfailoverwireless
Fast Failover in the Wireless Environment



Abstract – The spurt in interest in the Internet of Things (IoT) has spurred on wide-area deployments of IoT subnetworks. In IoT networks, multiple wireless communication solutions exist together. Some examples of these are cellular, WiFi, ZigBee, Bluetooth. These are integrated from geographically distributed networking infrastructures. Speaking in the context of Software Defined Networking (SDN), it is common knowledge that the control plane is disassociated from the data plane. For both wired and wireless networks, Link Failure is a common phenomenon in the elements present in the data plane. Link failure is handled locally by OpenFlow switches with the help of Fast Failover Group, which makes use of buckets to watch ports or groups. In case a port is down, the bucket associated with a live port in the list is chosen. This experiment aims to implement fast failover group in a wireless environment and study the consequent behaviour of the network based on evaluation metrics like throughput, hop count, etc. 


I.  INTRODUCTION
Software Defined Networking (SDN), in recent years, has gained traction as a scalability and programmability solution. This is of great importance in designing data centres and optical networks. SDN provides great network configurability with a platform for virtualising network functions at low costs.
Wireless Mesh Networks (WMN) have important applications in areas like transportation systems, health systems, disaster recovery and public safety networks, wireless community networks, and Google Wi-Fi.


Motivation: Of the many beneficial services that SDN provides, network configurability is of greater interest when working in a wireless environment. However, due to the inherent distributed nature of Wireless Mesh Network routing protocols the management and reconfiguration of routers becomes error-prone. Also, the flow routing is rigid, and the convergence times are huge.
In wireless networks, an issue of significant concern is the exploration of failure recovery mechanisms for data plane elements. A trustable failure recovery mechanism will ensure good quality of service (QoS) within the deployed network.


II. ROADMAP
Objective: In this project, we implement the fast failover mechanism by setting up a wireless network prototype. With focus on implementation of Fast Failover using Bidirectional Forwarding Detection (BFD) and Connectivity Fault Management (CFM), we consider a single link failure for UDP/TCP traffic and compare the throughput and hop length metrics. The OpenFlow-enabled network will make use of Fast Failover group tables to reroute packets and curb the ill effects of link failures. This is one way of protecting the network.


IV. EXPERIMENTAL SETUP
For the scope of this project, we make use of Mininet-WiFi, which is “a fork of Mininet SDN network emulator and extends the functionality of Mininet by adding virtualized WiFi stations and access points (AP) based on drivers and the 8011_hwsim wireless simulation driver”.

Mininet-WiFi not only supports all the normal SDN emulation functions of the standard Mininet network emulator but also adds new functionality. Additionally, it should be mentioned that Mininet-WiFi inherits all the limitations of Mininet such as using a single Linus kernel, not being able to create custom routing with the OpenFlow controller, etc.

In order to carry out this project, we used an initial test network that had the following setup: we consider five stations, five access points and one controller will create the nodes of our network. It is important to remember that these are virtual components on the Mininet-WiFi (v2.2.1d1) simulation environment and not tangible hardware. 

To understand the components better, let us look at them individually. Stations are devices that “connect to an access point through authentication and association”. In Mininet-WiFi each station has one wireless card. Access Points are the devices that manage the stations associated with them. 

The controller used for this project is the Ryu controller, running with ryu-manager 4.26. The Open vSwitch version supported by Mininet-WiFi by default is 1.10.0. As mentioned in the initial report, we went ahead with this configuration as we did not face any compatibility issues. The communication protocol OpenFlow was used to monitor and manage the flow of packets in the network.

During our experimentation, we faced software specific challenges. One case for instance was that we were able to ping from one station to the other even though there were no flow entries in the access points. A reason for this could be that each AP behaves as a hub. According to the documentation for Mininet-WiFi, “OpenFlow-enabled switches (using OpenFlow 1.0 or 1.3) will reject "hairpin connections", flows which cause traffic to be sent out the same port in which it was received. A wireless AP receives and sends packets on the same wireless interface. Stations connected to the same wireless access point would require a "hairpin connection" on the access point to communicate with each other. I surmise that, to handle this issue, Linux treats the WLAN interface in each access point like the radio network sta1-ap1-sta2 as if it is a "hub", where ap1-wlan0 provides the "hub" functionality for data passing between sta1 and sta2. ap1-wlan0 switches packets in the wireless domain and will not bring a packet into the "Ethernet switch" part of access point ap1 unless it must be switched to another interface on ap1 other than back out ap1-wlan0”. 

However, the reason for this could also be that the stations were in close proximity to the APs that they were initially connected to. For instance, sta1-ap1 and sta2-ap2 were the initial connections. There could be a possibility that sta2 was in the range of ap1 and hence communication between the two stations was possible without their being any flow entries in the flow tables of either access point.

Another issue we faced while conducting our experiment was the handling of looped networks. To resolve this issue, we used the Spanning Tree Protocol.

Spanning Tree Protocol (STP):
This protocol is used to build loop free logical topologies. Preventing bridge loops and the broadcast radiation, which is the accretion of large amounts of broadcast and multicast traffic, is the primary function of STP. It creates a spanning tree within the network, thereby removing loops.
Once this was done, we were able to insert flow entries into the access points of a looped network by using STP, we endeavoured to implement Fast Failover using BFD and CFM.
In implementing both BFD and CFM, we had to find out the shortest path from one access point to another access point, and the next shortest path after removing an edge that was used in the shortest path. This was done to use the second path in case of a link failure. Now that the two paths have been found, a link is failed at random and the packets should be forwarded on the next shortest path. Then we assess metrics such as throughput, hop count and delay.
 
Our first step was to implement BFD. When we ran our test topology with four APs and four stations, which we shall refer to as Topology #1, with a ryu controller. The results achieved are pasted below:
 
The edges of our second test topology, which we shall refer to as Topology #2, are defined below: 
edge_list = [(0,1,1), (0,5,1), (1,5,1), (1,2,1), (2,6,1), (2,3,1), (2,4,1), (3,6,1), (3,4,1), (4,7,1), (5,6,1), (5,8,1), (5,10,1), (6,7,1), (6,8,1), (7,9,1), (8,9,1), (8,10,1), (8,11,1), (9,12,1), (9,13,1), (10,18,1), (10,11,1), (10,14,1), (11,12,1), (11,15,1), (12,13,1), (12,16,1), (13,17,1), (14,15,1), (14,19,1), (15,16,1), (15,21,1), (15,20,1), (16,21,1), (16,22,1), (16,17,1), (17,23,1), (18,19,1), (19,20,1), (20,21,1), (21,22,1), (22,23,1)]

Three source-destination pairs, (0,1), (2,6), (8,9), were considered to evaluate the performance of fast failover with the following metrics: throughput, delay and hop count.
