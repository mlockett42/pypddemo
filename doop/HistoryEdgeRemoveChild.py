#A DOOP edge that removes a child
from HistoryEdge import HistoryEdge

class HistoryEdgeRemoveChild(HistoryEdge):
    def __init__(self, startnodes, propertyownerid,
                 propertyname, propertyvalue, propertytype, documentid, documentclassname):
        super(HistoryEdgeRemoveChild, self).__init__(startnodes, documentid, documentclassname)
        self.propertyownerid = propertyownerid
        self.propertyname = propertyname
        self.propertyvalue = propertyvalue
        self.propertytype = propertytype

    def Replay(self, doc):
        parent = doc.GetDocumentObject(self.propertyownerid)
        getattr(parent, self.propertyname).remove(self.propertyvalue)

    def Clone(self):
        return HistoryEdgeRemoveChild(self.startnodes, 
            self.propertyownerid, self.propertyname, self.propertyvalue, self.propertytype, self.documentid, self.documentclassname)

    def GetConflictWinner(self, edge2):
        return 0

    
        
