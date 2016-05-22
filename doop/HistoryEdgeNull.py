#A null edge is used to merge a branched hypergraph back together
from HistoryEdge import HistoryEdge

class HistoryEdgeNull(HistoryEdge):
    def __init__(self, startnodes, propertyownerid, propertyname, propertyvalue, propertytype, documentid, documentclassname):
        super(HistoryEdgeNull, self).__init__(startnodes, documentid, documentclassname)
        self.propertyownerid = propertyownerid
        self.propertyname = propertyname
        self.propertyvalue = propertyvalue
        self.propertytype = propertytype

    def Clone(self):
        return HistoryEdgeNull(set(self.startnodes), self.propertyownerid, self.propertyname, self.propertyvalue, self.propertytype, self.documentid, self.documentclassname)

    def Replay(self, doc):
        pass
    

