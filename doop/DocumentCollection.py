#This module handles storing all documents in the database (and reloading)
from collections import defaultdict
from Document import Document
from HistoryEdgeSimpleProperty import HistoryEdgeSimpleProperty
from HistoryEdgeAddChild import HistoryEdgeAddChild
from HistoryEdgeRemoveChild import HistoryEdgeRemoveChild
from HistoryEdgeNull import HistoryEdgeNull
from HistoryEdge import HistoryEdge
from DocumentObject import DocumentObject
from FieldList import FieldList
from HistoryGraph import HistoryGraph
from jsoncompat import JSONEncoder, JSONDecoder
from FieldInt import FieldInt

class DocumentCollection(object):
    def __init__(self):
        self.documentsbyclass = defaultdict(dict)
        self.objectsbyid = dict()
        self.classes = dict()
        self.historyedgeclasses = dict()
        #for theclass in HistoryEdge.__subclasses__():
        #    self.historyedgeclasses[theclass.__name__] = theclass
        self.historyedgeclasses[HistoryEdgeSimpleProperty.__name__] = HistoryEdgeSimpleProperty
        self.historyedgeclasses[HistoryEdgeAddChild.__name__] = HistoryEdgeAddChild
        self.historyedgeclasses[HistoryEdgeRemoveChild.__name__] = HistoryEdgeRemoveChild
        self.historyedgeclasses[HistoryEdgeNull.__name__] = HistoryEdgeNull
        self.edgelistener = None

    def Register(self, theclass):
        self.classes[theclass.__name__] = theclass

    def asJSON(self, notinset):
        ret = list()
        if notinset == None:
            notinfn = lambda x: True
        else:
            notinfn = lambda x: x not in notinset
        for (objid, document) in self.objectsbyid.iteritems():
            if document.IsDocument():
                history = document.history
                for edgeid in history.edges:
                    edge = history.edges[edgeid]
                    startnodes = list(edge.startnodes)
                    if len(edge.startnodes) == 1:
                        startnode1id = startnodes[0]
                        startnode2id = ""
                    elif len(edge.startnodes) == 2:
                        startnode1id = startnodes[0]
                        startnode2id = startnodes[1]
                    else:
                        assert False
                    
                    if notinfn(edge.edgeid):
                        ret.append(edge.asDict())
        return JSONEncoder().encode(ret)

    def GetAllEdgeIDs(self):
        #Return a list of all of the edgeid in this document collection
        l = list()
        for (objid, document) in self.objectsbyid.iteritems():
            if document.IsDocument():
                history = document.history
                for edgeid in history.edges:
                    edge = history.edges[edgeid]
                    l.append(edge.edgeid)
        return l        

    def LoadFromJSON(self, edges):
        historygraphdict = defaultdict(HistoryGraph)
        documentclassnamedict = dict()

        for edge in edges:
            edge = self.historyedgeclasses[edge["classname"]](edge["edgeid"], edge["startnodes"], edge["endnode"], edge["propertyownerid"], 
                edge["propertyname"], edge["propertyvalue"], edge["propertytype"], edge["documentid"], edge["documentclassname"])

            if edge.documentid in historygraphdict:
                historygraph = historygraphdict[edge.documentid]
            elif edge.documentid in self.objectsbyid:
                historygraph = self.objectsbyid[edge.documentid].history.Clone()
                historygraphdict[edge.documentid] = historygraph
            else:
                historygraph = HistoryGraph()
                historygraphdict[edge.documentid] = historygraph
            if edge.propertytype == "FieldInt":
                propertyvalue = int(edge.propertyvalue)
            elif edge.propertytype == "FieldText":
                propertytype = basestring
                propertyvalue = str(edge.propertyvalue)
            elif edge.propertytype == "" and edgeclassname == "HistoryEdgeNull":
                edge.propertyvalue = ""
            documentclassnamedict[edge.documentid] = edge.documentclassname
            history = historygraphdict[edge.documentid]
            history.AddEdge(edge)

        for documentid in historygraphdict:
            history = historygraphdict[documentid]
            doc = self.classes[documentclassnamedict[documentid]](documentid)
            history.Replay(doc)
            self.AddDocumentObject(doc)
            
       
    def AddEdges(self, edges):
        #A set of edges is received over the internet add them and replay the objects
        changes = set()

        for edge in edges:
            if isinstance(edge, HistoryEdgeAddChild) and edge.propertyownerid == "" and edge.propertyname == "":
                #A new object is being created by this edge
                obj = self.classes[edge.propertytype](edge.propertyvalue)
                #This is a new document so it has no parent
                obj.history = HistoryGraph()
                #Fixme: Add a creation function that does put any thing into the historygraph
                self.AddDocumentObject(obj)
            else:
                obj = self.objectsbyid[edge.documentid].GetDocument()
            if edge.startnodes[0] == "":
                print "obj.history.edgesbystartnode = ",obj.history.edgesbystartnode
                print "obj.history.edges = ",obj.history.edges;
                assert "" not in obj.history.edgesbystartnode
            obj.history.AddEdge(edge)
            changes.add(obj.id)

        for documentid in changes:
            doc = self.objectsbyid[documentid]
            doc.history.Replay(doc)

       
    def GetByClass(self, theclass):
        return self.documentsbyclass[theclass.__name__]

    def AddDocumentObject(self, obj):
        assert isinstance(obj, DocumentObject)
        assert obj.__class__.__name__  in self.classes
        for propname in obj.doop_field:
            propvalue = obj.doop_field[propname]
            if isinstance(propvalue, FieldList):
                for obj2 in getattr(obj, propname):
                    assert obj2.__class__.__name__  in self.classes
                    self.objectsbyid[obj2.id] = obj2
        self.documentsbyclass[obj.__class__.__name__][obj.id] = obj
        self.objectsbyid[obj.id] = obj


documentcollection = None

def InitialiseDocumentCollection():
    global documentcollection
    documentcollection = DocumentCollection()


