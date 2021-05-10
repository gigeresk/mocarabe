class ScheduledNet:
    lastId = 0
    # have a source, a dest, an id, a hyperedge
    # print
    # ability to have or not to have travel
    def __init__( self ):
        self.enter_noc = None
        self.exit_noc = []
        self.noc_hops = []

        self.id = ScheduledNet.lastId
        ScheduledNet.lastId += 1