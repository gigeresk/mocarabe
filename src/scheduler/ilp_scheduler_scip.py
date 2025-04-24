import ast
import time
import numpy as np

import pyscipopt as scip

import src.device

from src.resource_graph import ResourceGraph
from .scheduled_netlist import ScheduledNetlist
from .scheduled_net import ScheduledNet

class Return:
    def __init__( self, setupTime, solveTime, ioTime ):
        self.setupTime = setupTime
        self.solveTime = solveTime
        self.ioTime = ioTime

def schedule( self, device, dataflow_mode,netlist, io_pes,boundingBoxEnabled,file_name, benchmark, solFilename, file_helper ):
        '''
        provide the following: Nx,Ny,P,C,T,dataflow_mode,IO_I,II,io_pes,boundingBoxEnabled,file_name, benchmark
        '''
        # TODO remove benchmark, file_helper, solFilename, file_name from arguments here

        Nx = device.Nx
        Ny = device.Ny
        P = device.P
        C = device.physical_channels
        T = device.T
        II = device.II
        IO_I = device.IO_I # should be 2, so that one can go come from south, one from west
        IO_O = device.IO_O  #leave PE: 1 is ok...
        NOC_PIPE = device.noc_pipelining_stages
        # print(f'IO_O:{IO_O}')
        boundingBoxSize = [0]*P

        t0 = time.time()
        # new parameter
        # if we're not at our destination, we can roll over.
        # keep the ability to suppress stuff
        T_rollover = False

        # read list of nets to route
        f = open(file_name, 'r')

        lines = f.read().splitlines()
        maxP=len(lines)+1 # number of nets = number of lines in the file
        fanout = [0] * maxP
        src_x = dict()
        src_y = dict()
        for p, line in enumerate(lines):
            line = line.partition('#')[0] # comments
            rawnet=ast.literal_eval(line)
            net=np.array(rawnet)
            fanout[p]=net.shape[0]-1
            if(dataflow_mode==1 and len(net.shape)>1):
                src_x[int(net[0][2])]=int(net[0][0])
                src_y[int(net[0][2])]=int(net[0][1])
            elif(dataflow_mode==1 and len(net.shape)==1):
                print("if this is ever true, I want to know where it comes from")
                assert False
                src_x[int(net[2])]=int(net[0])
                src_y[int(net[2])]=int(net[1])
        f.close()
        noNocInitialAndFinal = False

        m = scip.Model("mip-partition")
        # m.Params.Threads = 6
        # m.Params.TimeLimit = 1800
        # m.Params.MipFocus = 1

        # Initialize dictionaries to store variables
        h = {}
        v = {}
        enter = {}
        exit_ = {}
        enterc = {}
        exitc = {}

        # Create variables
        for i in range(Nx):
            for j in range(Ny):
                for c in range(C):
                    for p in range(P):
                        for t in range(T):
                            h[i,j,c,p,t] = m.addVar(vtype="B", name=f"h_{i}_{j}_{c}_{p}_{t}")
                            v[i,j,c,p,t] = m.addVar(vtype="B", name=f"v_{i}_{j}_{c}_{p}_{t}")
                            enter[i,j,c,p,t] = m.addVar(vtype="B", name=f"enter_{i}_{j}_{c}_{p}_{t}")
                            exit_[i,j,c,p,t] = m.addVar(vtype="B", name=f"exit_{i}_{j}_{c}_{p}_{t}")

                for p in range(P):
                    for t in range(T):
                        enterc[i,j,p,t] = m.addVar(vtype="B", name=f"enterc_{i}_{j}_{p}_{t}")
                        exitc[i,j,p,t] = m.addVar(vtype="B", name=f"exitc_{i}_{j}_{p}_{t}")
        # h = m.addVars(Nx, Ny, C, P, T, vtype=GRB.BINARY, name='h')
        # v = m.addVars(Nx, Ny, C, P, T, vtype=GRB.BINARY, name='v')
        # enter = m.addVars(Nx, Ny, C, P, T, vtype=GRB.BINARY, name='enter')
        # exit_ = m.addVars(Nx, Ny, C, P, T, vtype=GRB.BINARY, name='exit_')

        # enterc = m.addVars(Nx, Ny, P, T, vtype=GRB.BINARY, name='enterc')
        # exitc = m.addVars(Nx, Ny, P, T, vtype=GRB.BINARY, name='exitc')

        # Add constraint: allow path to enter and exit_ anytime from specified src
        # and dest locations
        # path *must* enter from given x,y within alloted time range
        # path *must* exit_ at given x,y within alloted time range
        if(T>1):
            for p, line in enumerate(lines):
                if(p>=P): # limit batch to first P-1 paths
                    break

                rawnet=ast.literal_eval(line)
                net=np.array(rawnet)
                fanout[p]=net.shape[0]-1
                if(dataflow_mode==1 and len(net.shape)==1):
                    # no fanout
                    m.addCons(scip.quicksum(exit_[x,y,net[2],t]
                        for x in range(0,Nx)
                        for y in range(0,Ny)
                        for t in range(0,T))==0)
                    continue

                srcx=int(net[0][0])
                srcy=int(net[0][1])
                if(dataflow_mode==1 and fanout[p]!=0):
                    srcid=int(net[0][2])
                    assert(srcid<P)
                elif(dataflow_mode==1 and fanout[p]==0):
                    continue
                else:
                    srcid=p

                # path can enter the NoC anytime
                try:
                    m.addCons(scip.quicksum(enterc[srcx,srcy,srcid,t] for t in range(0,T))==1)
                    m.addCons(scip.quicksum(enter[srcx,srcy,c,srcid,t] for t in range(0,T) for c in range(C) )==1)

                except KeyError:
                    print("bad key error")
                    f = open("keyerrors.txt", "a")
                    f.write("bad key error for " + solFilename)
                    f.close()
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        if(not(x==srcx and y==srcy)):
                            for t in range(0,T):
                                # if you're not the chosen one, don't leave at all.
                                m.addCons(enterc[x,y,srcid,t]==0)
                                for c in range(0,C):
                                    m.addCons(enter[x,y,c,srcid,t]==0)
                # loop over destinations..
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        match=0

                        net_dest_xy = []
                        for dest in net[1:]:
                            # import pdb pdb.set_trace()
                            net_dest_xy.append((int(dest[0]),int(dest[1])))

                            net_dest_xy = list(set(net_dest_xy))
                            # print(net_dest_xy)
                        # import pdb pdb.set_trace()
                        for dest in range(0,len(net_dest_xy)):
                            destx=net_dest_xy[dest][0]
                            desty=net_dest_xy[dest][1]
                            if(dataflow_mode==1):
                                destid=int(net[dest][2])
                                #assert(destid<P)
                                distance=(destx-srcx+Nx)%Nx+(desty-srcy+Ny)%Ny
                            else:
                                destid=p

                            if(x==destx and y==desty):
                                # path can leave the NoC anytime
                                m.addCons(scip.quicksum(exitc[x,y,srcid,t] for t in range(0,T))==1) #uhh... changed this!
                                match=1
                                if(dataflow_mode==1 and destid<P):
                                    for t in range(1,T):
                                        m.addCons(exitc[x,y,srcid,t] <= 1 -scip.quicksum(enterc[src_x[destid],src_y[destid],destid,t1]
                                                    for t1 in
                                                    range(0,min(T-1,t+NOC_PIPE))))

                        if (match==0):
                            for t in range(0,T):
                                m.addCons(exitc[x,y,srcid,t]==0)
                                for c in range(0,C):
                                    m.addCons(exit_[x,y,c,srcid,t]==0)


                if boundingBoxEnabled == True:
                    #boundingBoxSize[p] = 4
                    # Enabled bounding box constraints
                    destBoundary = [[Nx,Ny], [0,0]] #min (x,y) and max (x,y)


                    for dest in range(1,len(net)):
                        # find min x,y and max x,y to find bounding box boundaries
                        destBoundary[0][0] = min(destBoundary[0][0], int(net[dest][0]))
                        destBoundary[0][1] = min(destBoundary[0][1], int(net[dest][1]))
                        destBoundary[1][0] = max(destBoundary[1][0], int(net[dest][0]))
                        destBoundary[1][1] = max(destBoundary[1][1], int(net[dest][1]))

                    #if min < start, set min as BB boundary
                    # import pdb pdb.set_trace()
                    # if destBoundary[0][0] < int(net[0][0]) or destBoundary[0][1] < int(net[0][1]):
                    #     boundingBox = Box( int(net[0][0]),int(net[0][1]),Nx,Ny ) #TODO SUPPORT NX AND NY
                    # else:
                    if False: a=1
                    else:
                        boundingBox = Box( net[0][0:2], destBoundary, Nx, Ny )
                        #inBound = 0 #TODO deal with i/o of bound
                        #TODO add boundary conditions (first make it not broken!)
                        #TODO make sure behaviour is same for > and <
                        #outOfBound = 0
                        # for x in range(0,Nx):
                        #     for y in range(0,Ny):
                        # import pdb pdb.set_trace()
                        m.addCons( scip.quicksum( h[x,y,c,p,t] for x,y in boundingBox.negativeBox for c in range(C) for t in range(0,T) ) ==0 )
                        m.addCons( scip.quicksum( v[x,y,c,p,t] for x,y in boundingBox.negativeBox for c in range(C) for t in range(0,T) ) ==0 )
                                # for c in range(0,C):
                                #     for t in range(0,T):
                                        #TODO remove the outgoing arrows too


                                        # if ( (x,y) in boundingBox.negativeBox ):#or y not in boundingBox[1] ): #S<dataflow_mode (default)
                                        #     # print('constraint')
                                        #     m.addCons( h[x,y,c,p,t] == 0)
                                        #     m.addCons( v[x,y,c,p,t] == 0)
                                        #     # m.addCons( enter[x,y,c,p,t] == 0)
                                            # m.addCons( exit_[x,y,c,p,t] == 0)
                                            # m.addCons( enterc[x,y,p,t] == 0)
                                            # m.addCons( exitc[x,y,p,t] == 0)
                #                         outOfBound = outOfBound + 2 #h,v not in bounding box

                                #    else:
                                #         inBound = inBound + 2 #h,v within bounding box

        # boundingBoxSize[p] =  float(inBound) / float(inBound + outOfBound)

        # T==1 netlist loading
        if(T==1):
            for p, line in enumerate(lines):
                if(p>=P): # limit bacth to first P-1 paths
                    break
                net=ast.literal_eval(line)
                fanout[p]=len(net)-1
                srcx=int(net[0][0])
                srcy=int(net[0][1])

                # path must enter NoC
                m.addCons(enterc[srcx,srcy,p,0]==1)

                for x in range(0,Nx):
                    for y in range(0,Ny):
                        if(not(x==srcx and y==srcy)):
                            m.addCons(enterc[x,y,p,0]==0)

                # loop over destinations
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        match=0
                        for dest in range(1,len(net)):
                            destx=int(net[dest][0])
                            desty=int(net[dest][1])
                            if(x==destx and y==desty):
                                # paths can leave the NoC
                                # print(f'destx,desty: {x},{y}')
                                m.addCons(exitc[x,y,p,0]==1)
                                match=1

                        if (match==0):
                            m.addCons(exitc[x,y,p,0]==0)

            # channel exclusivity constraint for T=1 mode
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for p in range(0,P):
                        for c in range(0,C):
                            m.addCons(scip.quicksum(h[x,y,c,p,t] for t in range(0,T)) <= 1)
                            m.addCons(scip.quicksum(v[x,y,c,p,t] for t in range(0,T)) <= 1)


        # T>1 II resource constraint (the only constraints that should involve II)

        if(T>1):
        # # TODO DO THIS FOR T=1
            if II > 0:
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        for t in range(0, T):
                            m.addCons(scip.quicksum(enterc[x,y,p,t] for p in range(P) ) <= 1) # enter noc = IO_O
                            for c in range(0,C):
                                m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(P)  ) <= 1) #enter noc IO_O

                            m.addCons(scip.quicksum(exitc[x,y,p,t] for p in range(P)  ) <= IO_I)  # exit_ noc = IO_I
                            for c in range(0,C):
                                m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(P)  ) <= IO_O) #enter noc IO_O
                                m.addCons(scip.quicksum(exit_[x,y,c,p,t] for p in range(P) ) <= 1) #exit_ noc IO_I
                                m.addCons(scip.quicksum(h[x,y,c,p,t] for p in range(P) ) <= 1)
                                m.addCons(scip.quicksum(v[x,y,c,p,t] for p in range(P) ) <= 1)
        elif( T == 1 ):
            if( tuple((x,y)) in io_pes):
                m.addCons(scip.quicksum(enterc[x,y,p,t] for p in range(P) for t in [0] ) <= IO_O) # enter noc = IO_O
                for c in range(0,C):
                    m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(P) for t in [0] ) <= 1) #enter noc IO_O
            #If we're not an IO PE, can leave one at a time
            else:
                m.addCons(scip.quicksum(enterc[x,y,p,t] for p in range(P) for t in [0] ) <= 1) # enter noc = IO_O
                for c in range(0,C):
                    m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(P) for t in [0] ) <= 1) #enter noc IO_O

            m.addCons(scip.quicksum(exitc[x,y,p,t] for p in range(P) for t in [0] ) <= IO_I)  # exit_ noc = IO_I
            for c in range(0,C):
                # m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(P) for t in ii_range ) <= IO_O) #enter noc IO_O
                m.addCons(scip.quicksum(exit_[x,y,c,p,t] for p in range(P) for t in [0] ) <= 1) #exit_ noc IO_I
                m.addCons(scip.quicksum(h[x,y,c,p,t] for p in range(P) for t in [0] ) <= 1)
                m.addCons(scip.quicksum(v[x,y,c,p,t] for p in range(P) for t in [0] ) <= 1)
            print('do this rn')

            #TODO

        # Add constraints: if multiple paths start at same source, but leave at
        # different times, must ensure that they don't do so at the same time?
        # if they do, its essentially fanout. Order enforcement between departures?

        if(T>1):
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for c in range(0,C):
                        for p in range(0,P):
                            for t in range(0,T):
                                # what leaves must have entered
                                # you can leave more than once (fanout)
                                m.addCons(h[(x+1)%Nx,y,c,p,(t+NOC_PIPE+1)%T] <= h[x,y,c,p,t] + v[x,y,c,p,t] + enter[x,y,c,p,t])
                                m.addCons(v[x,(y+1)%Ny,c,p,(t+NOC_PIPE+1)%T] <= h[x,y,c,p,t] + v[x,y,c,p,t] + enter[x,y,c,p,t])
                                m.addCons(exit_[x,y,c,p,(t+NOC_PIPE+1)%T] <= h[x,y,c,p,t] + v[x,y,c,p,t] + enter[x,y,c,p,t])
                                m.addCons(h[x,y,c,p,t] + v[x,y,c,p,t] + enter[x,y,c,p,t] <= h[(x+1)%Nx,y,c,p,(t+NOC_PIPE+1)%T] + v[x,(y+1)%Ny,c,p,(t+NOC_PIPE+1)%T] + exit_[x,y,c,p,(t+NOC_PIPE+1)%T])

        elif(T == 1):
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for c in range(0,C):
                        for p in range(0,P):
                            # what leaves must have entered
                            # you can leave more than once (fanout)
                            m.addCons(h[(x+1)%Nx,y,c,p,0] <= h[x,y,c,p,0] + v[x,y,c,p,0] + enter[x,y,c,p,0])
                            m.addCons(v[x,(y+1)%Ny,c,p,0] <= h[x,y,c,p,0] + v[x,y,c,p,0] + enter[x,y,c,p,0])
                            m.addCons(exit_[x,y,c,p,0] <= h[x,y,c,p,0] + v[x,y,c,p,0] + enter[x,y,c,p,0])
                            m.addCons(h[x,y,c,p,0] + v[x,y,c,p,0] + enter[x,y,c,p,0] <= h[(x+1)%Nx,y,c,p,0] + v[x,(y+1)%Ny,c,p,0] + exit_[x,y,c,p,0])


        if( noNocInitialAndFinal and T>1):
            # Originally we removed this, but it actualy helps if we throw out
            # the whole "T=II" approach, where T isn't just the upper bound but is the actual guaranteed schedule length.

            # regardless of IO_I or IO_O, only one path can hop onto a channel at x,y in a given cycle.
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for c in range(0,C):
                        for p in range(0,P):
                            # Do not use horizontal and vertical resources in cycle 0
                            m.addCons(h[x,y,c,p,0] == 0)
                            m.addCons(v[x,y,c,p,0] == 0)
                            # pretty sure below isn't necessary, since we are forced to exit_ already
                            #i will check though
                            # Do not use horizontal and vertical resources in the final cycle
                            # m.addCons(h[x,y,c,p,T-1] == 0)
                            # m.addCons(v[x,y,c,p,T-1] == 0)

        if(P>1):
            if (T>1):
                # for individual channel resources, can't use more than once a cycle
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        for c in range(0,C):
                            for t in range(0,T):
                                m.addCons(scip.quicksum(h[x,y,c,p,t] for p in range(0,P))<=1)
                                m.addCons(scip.quicksum(v[x,y,c,p,t] for p in range(0,P))<=1)
                                # I don't think this is necessary?
                                # m.addCons(scip.quicksum(enter[x,y,c,p,t] for p in range(0,P))<=1)
                                # m.addCons(scip.quicksum(exit_[x,y,c,p,t] for p in range(0,P))<=1)
            elif( T==1 ):
                for x in range(0,Nx):
                    for y in range(0,Ny):
                        for c in range(0,C):
                            m.addCons(scip.quicksum(h[x,y,c,p,0] for p in range(0,P))<=1)
                            m.addCons(scip.quicksum(v[x,y,c,p,0] for p in range(0,P))<=1)

                            m.addCons(scip.quicksum(enter[x,y,c,p,0] for p in range(0,P))<=1)
                            m.addCons(scip.quicksum(exit_[x,y,c,p,0] for p in range(0,P))<=1)

        if(T>1):
            # regardless of IO_I or IO_O, only one path can hop onto a channel at x,y in a given cycle.
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for t in range(0,T):
                        if( tuple((x,y)) in io_pes):
                            m.addCons(scip.quicksum(enterc[x,y,p,t] for p in range(0,P))<=IO_O)
                        else:
                            m.addCons(scip.quicksum(enterc[x,y,p,t] for p in range(0,P))<=1)

        # Ensure single entry and exit_ across channels
        for p in range(0,P):
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for t in range(0,T):
                        m.addCons(scip.quicksum(enter[x,y,c,p,t] for c in range(0,C))>=enterc[x,y,p,t])
                        m.addCons(scip.quicksum(exit_[x,y,c,p,t] for c in range(0,C))>=exitc[x,y,p,t])
                        for c in range(0,C):
                            m.addCons(enter[x,y,c,p,t]<=enterc[x,y,p,t])
                            m.addCons(exit_[x,y,c,p,t]<=exitc[x,y,p,t])

        # Set objective
        m.setObjective(scip.quicksum(h[x,y,c,p,t] + v[x,y,c,p,t]
            for x in range(0,Nx)
            for y in range(0,Ny)
            for c in range(0,C)
            for p in range(0,P)
            for t in range(0,T)), sense='minimize')

        # solve
        t1 = time.time()
        # m.write('debug.mps')
        # m.write('debug.lp')
        m.optimize()

        num_vars = 10#m.NumVars
        num_constrs = 10#m.NumConstrs

        # status = m.Status
        # if status != 2 and status != 10:
        #     del m #garbage collect

        # assert( status == 2 or status == 10), "Could not find a feasible solution with these parameters"
        print( "Found a feasible solution!" )
        VERBOSE = False
        t2 = time.time()


        solFilename = file_helper.schedule_filepath = file_helper.schedule_dir  +'-Nx%d-Ny%d-C%d-P%d-T%d.sol' % ( Nx, Ny, C, P, T)
        solFile = open(solFilename, "w+")
        print(f"printing to {solFilename}")

        # instantiate a ResourceGraph so that
        # 1) don't worry about tuples
        # 2) possibly be able to keep things ordered
        # 3) hidden, simpler implementation
        # 4) interoperability...
        # hope it doesn't take too long: only has to be done once as we error out before this

        resource_graph = ResourceGraph( )
        resource_graph.create( device )

        # todo is getLbLocal() ok?  also how do i check if feasible
        scheduled_netlist = ScheduledNetlist( resource_graph )
        for p in range(0,P):
            scheduled_net = ScheduledNet()
            for x in range(0,Nx):
                for y in range(0,Ny):
                    for t in range(0,T):
                        for c in range(0,C):
                            enterLine = 'enter[%d][%d][%d][%d][%d] = %d' % (x, y, c, p, t, m.getVal(enter[x,y,c,p,t]))
                            
                            if m.getVal(enter[x,y,c,p,t]) == 1.0: # none == 0
                                # import pdb; pdb.set_trace()
                                solFile.write(enterLine + '\n')
                                if( m.getVal(enter[x,y,c,p,t]) == 1.0 ):
                                    scheduled_net.enter_noc = resource_graph.pe_out_switch[(x,y,c,t)]

                            exitLine = 'exit[%d][%d][%d][%d][%d] = %d' % (x, y, c, p, t, m.getVal(exit_[x,y,c,p,t]))
                            if  m.getVal(exit_[x,y,c,p,t]) == 1.0:
                                # import pdb; pdb.set_trace()
                                solFile.write(exitLine + '\n')
                                if m.getVal(exit_[x,y,c,p,t]) == 1.0 :
                                    scheduled_net.exit_noc.append( resource_graph.pe_in_switch[(x,y,c,t)] )

                            hLine = 'h[%d][%d][%d][%d][%d] = %d' % (x, y, c, p, t, m.getVal(h[x,y,c,p,t]))
                            if m.getVal(h[x,y,c,p,t]) == 1.0:
                                solFile.write(hLine + '\n')
                                if m.getVal(h[x,y,c,p,t]) == 1.0:
                                    scheduled_net.noc_hops.append( resource_graph.h_noc[(x,y,c,t)] )

                            vLine = 'v[%d][%d][%d][%d][%d] = %d' % (x, y, c, p, t, m.getVal(v[x,y,c,p,t]))
                            if m.getVal(v[x,y,c,p,t]) == 1.0 :
                                solFile.write(vLine + '\n')
                                if m.getVal(v[x,y,c,p,t]) == 1.0 :
                                    scheduled_net.noc_hops.append( resource_graph.v_noc[(x,y,c,t)] )
            scheduled_netlist.append( scheduled_net )
        solFile.close()
        print(f"scip ilp scheduler status: {m.getStatus()}")
        print("Wrote solution to {0}".format(solFilename))

        return scheduled_netlist, num_vars, num_constrs

if __name__ == "__main__":

    device_ = device.Device( Nx=8, Ny=9, C=2, T=2, IO_I=2,IO_O=1, layout='', pe_pipelining_stages=2, noc_pipelining_stages=2, unroll=4, P=140, II=2 )
    dataflow_mode = False

    schedule( 0, device_, dataflow_mode,netlist=0, io_pes=[],boundingBoxEnabled=False,file_name='proj/int_gaussian_--28-11-20-22.34.33/netlist/int_gaussian.net', benchmark='int_gaussian', solFilename='gargo.sol', file_helper=None )