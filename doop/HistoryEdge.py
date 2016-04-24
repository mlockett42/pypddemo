#The base class for edges in DOOP

class HistoryEdge(object):
    def __init__(self, edgeid, startnodes, endnode, documentid):
        self.edgeid = edgeid
        self.startnodes = startnodes
        self.endnode = endnode
        self.documentid = documentid
        self.inactive = False
        self.played = False

        
    def RecordPastEdges(self, pastedges, graph):
        self.pastedges = self.pastedges | set(pastedges)
        edges = graph.edgesbystartnode[self.endnode]
        pastedges.add(self.edgeid)
        for edge in edges:
            edge.RecordPastEdges(set(pastedges), graph)

    
    def CanReplay(self, graph):
        for node in self.startnodes:
            if node != "":
                edge = graph.edgesbyendnode[node]
                if edge.isplayed == False:
                    return False
        return True

    def ResetPastEdges(self):
        self.pastedges = set()

    def HasPastEdge(self, pastedgeid):
        return pastedgeid in self.pastedges

    def CompareForConflicts(self, edge2):
	    if (self.__class__ != edge2.__class__):
		    return; #Different edge types can never conflict
	    if (self.inactive or edge2.inactive):
		    return; #Inactive edges can never conflict with active edges
	    conflictwinner = self.GetConflictWinner(edge2)
	    assert conflictwinner == -1 or conflictwinner == 0 or conflictwinner == 1
	    if conflictwinner == 1:
	        self.inactive = True
	    elif conflictwinner == -1:
	        edge2.inactive = True
        
    
    def asDict(self):
        return {"classname":self.__class__.__name__,
            "edgeid":self.edgeid,
            "startnodes":list(self.startnodes),
            "endnode":self.endnode,
            "propertyownerid":self.propertyownerid,
            "propertyvalue":self.propertyvalue,
            "propertyname":self.propertyname,
            "propertytype":self.propertytype,
            "documentid":self.documentid,
         }

    def __str__(self):
        return str(self.asDict())
