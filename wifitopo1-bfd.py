import networkx as nx
from mininet.link import TCLink
from mininet.node import Controller, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
import re,random,time
from networkx.utils import pairwise
from mininet.wifi.link import wmediumd, mesh, physicalMesh
from mininet.wifi.cli import CLI_wifi
from mininet.wifi.net import Mininet_wifi
from mininet.wifi.wmediumdConnector import interference
from mininet.node import UserSwitch, OVSSwitch
from mininet.log import setLogLevel, info

def topobuild():
        net = Mininet_wifi(
                   controller=None,link=TCLink, switch=OVSSwitch, waitConnected=True,autoSetMacs=True)
        c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1', 
                           port=6653)
               
        net.start()
        graph=nx.DiGraph()
        edges=[(0, 1), (1,2), (2,3), (3,0)]
        for (x,y) in edges:
            if (y,x) in edges:
                edges.remove((y,x))
        graph.add_edges_from(edges)
        total_node=len(graph.nodes)
        aps = {}
        host = []
        for node in range(total_node):
            print 'node:', node
            aps['ap%s'%(node + 1)] = net.addAccessPoint('ap%s'%(node+1), ssid='ssid%s'%(node+1))
            sta1 =  net.addStation('sta%s'%(node+1),cpu=.5/total_node)
 
        info("*** Configuring wifi nodes\n")
        net.configureWifiNodes()
      
        for node in range(total_node):
            net.addLink('sta%s'%(node+1), 'ap%s'%(node + 1))

        
        for (sw1, sw2) in edges:
            sw1=int(sw1)+1
            sw2=int(sw2)+1
            net.addLink("ap%d" % sw1, "ap%d" % sw2)
  
        net.build()
        c0.start()
        for node in range(total_node):
            aps['ap%s'%(node+1)].start([c0])
            
        return net
 
def ping(net,nodes,size='',count='',rate='',timeout=''):
          """
          """
          if rate!='':
           rate=' -i '+str(rate)
          if timeout!='':
             timeout=' -w '+str(timeout)
          if size !='':
             size='-s '+str(size)
          if count !='':
             count=' -c '+str(count)
          src,dest=nodes
          pingstats=src.cmd( 'ping %s %s' % (size+count+rate+timeout, dest.IP()) )
          pingstats= pingstats.split('\r\n')
          
          try:
            sent,received,loss,time=re.findall('\d+', pingstats[-3])
          
            min_,avg,max_,mdev=pingstats[-2].split('=')[1].strip().split(' ')[0].split('/') 
          except:
           return 1,0,64,64 # 64 is the ttl
           #import pdb;pdb.set_trace() # 100% packet loss
          return sent,received,min_,avg 
def get_path_length(net,src,dst):
    
    result=src.cmd('traceroute -n %s'%dst.IP())
    
    try:
      return int(result.split('\r\n')[-2].strip()[0])-1
    except:
       return 'Can not find path length'
def getNum(string):
          return float(re.findall('\d+.\d+',string)[0])       
def doIperf(net,src,dst,port=5001,startLoad=10,time=5,datasize=1): # 10*96bytes per secodn
          dst.cmd('sudo pkill iperf')          
          dst.cmd(('iperf -s -p%s -u -D')%(port))
          output=src.cmd(('iperf  -c %s  -p %s -u -t %d -b %sM')%(dst.IP(),port,time,datasize)) 
          time=0.0
          datasize_tx=0.0
          bitrate=0.0          
          try:
             #import pdb;pdb.set_trace()
             print 'iperf running for load '+str(datasize)
             output=output.split('\r\n')[-4].split('-')[1].split('  ')
             time=getNum(output[0])
             datasize_tx=getNum(output[1])
             bitrate=getNum(output[2])
          except:
                return [time,datasize_tx,bitrate]
          return [time,datasize_tx,bitrate]
def getavg(lst):
   return sum(lst)/len(lst)
   
def enable_BFD(net):
    """
     Bidirectional Forwarding Detection(BFD) is a network protocol used to detect link failure between two forwarding elements. 
    """
    switches=net.switches
    for switch in switches:
        ofp_version(switch, ['OpenFlow13'])
        intfs=switch.nameToIntf.keys()[1:]
        for intf in intfs:
            switch.cmd('ovs-vsctl set interface "%s" bfd:enable=true'%intf)
            
def ofp_version(switch, protocols):
    """
     sets openFlow version for each switch from mininet.
    """
    protocols_str = ','.join(protocols)
    command = 'ovs-vsctl set Bridge %s protocols=%s stp-enable=true' % (switch, protocols)
    switch.cmd(command.split(' '))
def sw_link_map(net):
    """
     constructs a links map where keys are switches and values are link object 
     for links between switches
    """
    aps = net.aps
    for ap in aps:
      print 'net ap: ',ap
    links_obj=net.links
    link_objs_filtered={}
    for obj in links_obj:
        print 'obj: ', obj
        print 'obj.intf1.name.find', obj.intf1
        if "sta" not in str(obj):
          if "wifi" not in str(obj):
            intf1=int(str(obj.intf1).split('-')[0].replace('ap',''))
            print 'inft1: ', intf1
            intf2=int(str(obj.intf2).split('-')[0].replace('ap',''))
            print 'inft1: ', intf1
            link_objs_filtered[(intf1,intf2)]=obj

        # print 'obj.intf1.name.find', obj.intf2.name.find('sta')
        # if obj.intf1.name.find('sta')<1 or obj.intf2.name.find('sta')<1: 
        #  continue
        #    print 'intf1', obj.intf1
        #    print 'intf2', obj.intf2
        # if obj.intf1.name.find('ap')<1 or obj.intf2.name.find('ap')<1: 
        # intf1=int(obj.intf1.name.split('-')[0].replace('ap',''))
        # print 'inft1: ', intf1
        # intf2=int(obj.intf2.name.split('-')[0].replace('ap',''))
        # print 'inft1: ', intf1
        # link_objs_filtered[(intf1,intf2)]=obj
    return link_objs_filtered
def bi_direct_edges(edges):
    bidirectEdges=[]
    for item in edges:
        bidirectEdges.append(item)
        bidirectEdges.append((item[1],item[0])) 
    return bidirectEdges  
def runner():
    "Create and run a custom topo with adjustable link parameters"
    net = topobuild();
    # c = RemoteController('c0', controller=RemoteController, ip='127.0.0.1',
    #                        port=6653)
    # net = Mininet_wifi( topo=topo,
    #                controller=None,link=TCLink, switch=OVSSwitch)
    # c0 = net.addController('c0', controller=RemoteController, ip='127.0.0.1',
    #                        port=6653)
    # # net.addController(c)             
    # net.start()
    enable_BFD(net)# enable bfd
    link_fail_dict=sw_link_map(net)
    edges=link_fail_dict.keys() # keys of link_fail_dict has all the edges of the graph
    print 'edges: ', edges
    edges=bi_direct_edges(edges) # make edges bi directional so that nx can find path
    graph=nx.DiGraph()
    graph.add_edges_from(edges) # construct graph from edges obtained from mininet net obj
    print 'edges', graph.edges;
    random.seed(30) # set seed for random number
    test_pair=[(0,1)] 
    result={'hop':[],'delay':[],'throughput':[]}
    time.sleep(8)
    for pair in test_pair:
        host1,host2=pair
        print 'host1, host2: ', pair
        src=net.getNodeByName('sta'+str(host1+1))
        dst=net.getNodeByName('sta'+str(host2+1))
        path=nx.shortest_path(graph,host1+1,host2+1) # compute shortest path from graph
        print 'path: ', path
        links_between_pair=pairwise(path) # make links from path
        randindex=random.randint(0,len(links_between_pair)-1) # find random index  to be used to get failed link
        link_to_fail=links_between_pair[randindex] # get random link to be failed using random index
        print 'Failing link between',link_to_fail
        
        if link_fail_dict.has_key(link_to_fail):
           link_to_fail_obj=link_fail_dict[link_to_fail] # find the link obj to fail
        elif link_fail_dict.has_key(link_to_fail[::-1]): # link might be with reverse key
             link_to_fail_obj=link_fail_dict[link_to_fail[::-1]] # find the link obj to fail 
             link_to_fail= link_to_fail[::-1]  
        try:
           print ping(net,[src,dst],64,2)# send some packets before calculation
           net.delLink(link_to_fail_obj) # delete link to fail it
        except:
          import pdb;pdb.set_trace()
        time.sleep(5)        
        sent,received,min_,avg=ping(net,[src,dst],1024,5)
        print 'Delay ',avg,' for ',pair
        result['delay'].append(float(avg))
        hop=get_path_length(net,src,dst)
        print 'Hop ',hop,' for ',pair
        result['hop'].append(float(hop))
        time_perf,datasize_tx,bitrate=doIperf(net,src,dst)
        print 'Throughput ',bitrate,' for ',pair
        result['throughput'].append(float(bitrate))
        link_fail_dict[link_to_fail]=net.addLink("ap%d" %link_to_fail[0],"ap%d" %link_to_fail[1])
    print 'Average Number of Hop:', getavg(result['hop'])
    print 'Average Delay: ', getavg(result['delay'])
    print 'Throughput:',getavg(result['throughput'])
    CLI_wifi(net)
    net.stop()
if __name__ == '__main__':
    setLogLevel( 'info' )
    runner()      