#A DOOP document
from DocumentObject import DocumentObject
import uuidcompat
from HistoryGraph import HistoryGraph
from ChangeType import ChangeType
from HistoryEdgeSimpleProperty import HistoryEdgeSimpleProperty
from HistoryEdgeAddChild import HistoryEdgeAddChild
from HistoryEdgeRemoveChild import HistoryEdgeRemoveChild

class Document(DocumentObject):
    def Clone(self):
        #Return a deep copy of this object. This object all of it's children and
        #it's history are cloned
        ret = self.__class__(self.id)
        ret.CopyDocumentObject(self)
        ret.history = self.history.Clone()
        ret.currentnode = self.currentnode
        return ret

    def Merge(self, doc2):
        assert self.id == doc2.id
        assert isinstance(doc2, Document)
        #Make a copy of self's history
        history = self.history.Clone()
        #Merge doc2's history
        history.MergeGraphs(doc2.history)
        history.RecordPastEdges()
        history.ProcessConflictWinners()
        #Create the return object and replay the history in to it
        ret = self.__class__(self.id)
        history.Replay(ret)
        return ret

    def __init__(self, id):
        super(Document, self).__init__(id)
        self.insetattr = True
        self.parent = None
        self.history = HistoryGraph()
        self.documentobjects = dict()
        self.currentnode = ""
        self.insetattr = False
        self.WasChanged(ChangeType.ADD_CHILD, "", "", self.id, self.__class__.__name__)
        
    def WasChanged(self, changetype, propertyownerid, propertyname, propertyvalue, propertytype):
        nextnode  = uuidcompat.getuuid()
        nodeset = set()
        nodeset.add(self.currentnode)
        if changetype == ChangeType.SET_PROPERTY_VALUE:
            edge = HistoryEdgeSimpleProperty(uuidcompat.getuuid(), nodeset, nextnode, propertyownerid, propertyname, propertyvalue, propertytype, self.id, self.__class__.__name__)
        elif changetype == ChangeType.ADD_CHILD:
            edge = HistoryEdgeAddChild(uuidcompat.getuuid(), nodeset, nextnode, propertyownerid, propertyname, propertyvalue, propertytype, self.id, self.__class__.__name__)
        elif changetype == ChangeType.REMOVE_CHILD:
            edge = HistoryEdgeRemoveChild(uuidcompat.getuuid(), nodeset, nextnode, propertyownerid, propertyname, propertyvalue, propertytype, self.id, self.__class__.__name__)
        else:
            assert False
        self.currentnode = nextnode
        self.history.AddEdge(edge)

    def GetDocumentObject(self, id):
        if id == self.id:
            return self
        return self.documentobjects[id]

    def GetDocument(self):
        #Return the document
        return self

    def IsDocument(self):
        #Return if this is a document. Documents have history graphs
        return True

    
