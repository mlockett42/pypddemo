#The edge representing adding a child object in DOOP
from HistoryEdge import HistoryEdge
import DocumentCollection

class HistoryEdgeAddChild(HistoryEdge):
    def __init__(self, edgeid, startnodes, endnode, propertyownerid, propertyname, propertyvalue, propertytype, documentid):
        super(HistoryEdgeAddChild, self).__init__(edgeid, startnodes, endnode, documentid)
        assert isinstance(propertyownerid, basestring)
        self.propertyownerid = propertyownerid
        self.propertyvalue = propertyvalue
        self.propertyname = propertyname
        self.propertytype = propertytype

    def Replay(self, doc):
        newobj = DocumentCollection.documentcollection.classes[self.propertytype](self.propertyvalue)
        doc.documentobjects[newobj.id] = newobj
        if isinstance(self, HistoryEdgeAddChild) and self.propertyownerid == "" and self.propertyname == "":
            pass #There is no parent object and this edge is creating a stand alone object
        else:
            parent = doc.GetDocumentObject(self.propertyownerid)
            getattr(parent, self.propertyname).add(newobj)

    def Clone(self):
        return HistoryEdgeAddChild(self.edgeid, self.startnodes, self.endnode,
            self.propertyownerid, self.propertyname, self.propertyvalue, self.propertytype, self.documentid)

    def GetConflictWinner(self, edge2):
        return 0 #There can never be a conflict becuase all edges are new

            
