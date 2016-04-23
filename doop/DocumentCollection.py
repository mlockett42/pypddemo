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

    def Register(self, theclass):
        self.classes[theclass.__name__] = theclass

    def asJSON(self, notinset):
        ret = list()
        if notinset == None:
            notinfn = lambda x: True
        else:
            notinfn = lambda x: x in notinset
        for (objid, document) in self.objectsbyid:
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
                    
                    if edge.propertytype is None:
                        propertytypename = ""
                    else:
                        propertytypename = edge.propertytype.__name__
                    if notinfn(edge.edgeid):
                        ret.append([document.id, document.__class__.__name__, edge.__class__.__name__, edge.edgeid, startnode1id, startnode2id, edge.endnode, edge.propertyownerid, edge.propertyname, 
                            str(edge.propertyvalue), propertytypename])
        return JSONEncoder().encode(ret)

    def GetAllEdgeIDs(self):
        #Return a list of all of the edgeid in this document collection
        l = list()
        for (objid, document) in self.objectsbyid:
            if document.IsDocument():
                history = document.history
                for edgeid in history.edges:
                    edge = history.edges[edgeid]
                    l.append(edge.id)
        return l        

    def LoadFromJSON(self, jsontext):
        historygraphdict = defaultdict(HistoryGraph)
        documentclassnamedict = dict()

        rows = JSONDecoder().decode(jsontext)

        for row in rows:
            documentid = row[0]
            documentclassname = row[1]
            edgeclassname = row[2]
            edgeid = row[3]
            startnode1id = row[4]
            startnode2id = row[5]
            endnodeid = row[6]
            propertyownerid = row[7]
            propertyname = row[8]
            propertyvaluestr = row[9]
            propertytypestr = row[10]

            if documentid in historygraphdict:
                historygraph = historygraphdict[documentid]
            else:
                historygraph = HistoryGraph()
                historygraphdict[documentid] = historygraph
                documentclassnamedict[documentid] = documentclassname
            if propertytypestr == "int":
                propertytype = int
                propertyvalue = int(propertyvaluestr)
            elif propertytypestr == "basestring":
                propertytype = basestring
                propertyvalue = str(propertyvaluestr)
            elif propertytypestr == "" and edgeclassname == "HistoryEdgeNull":
                propertytype = None
                propertyvalue = ""
            else:
                propertytype = self.classes[propertytypestr]
                propertyvalue = propertyvaluestr
            documentclassnamedict[documentid] = documentclassname
            if startnode2id == "":
                startnodes = {startnode1id}
            else:
                startnodes = {startnode1id, startnode2id}
            edge = self.historyedgeclasses[edgeclassname](edgeid, startnodes, endnodeid, propertyownerid, propertyname, propertyvalue, propertytype)
            history = historygraphdict[documentid]
            history.AddEdge(edge)

        for documentid in historygraphdict:
            doc = self.classes[documentclassnamedict[documentid]](documentid)
            history.Replay(doc)
            self.AddDocumentObject(doc)
            
       
    def AddEdges(self, edges):
        #A set of edges is received over the internet add them and replay the objects
        changes = set()

        for edge in edges:
            if isinstance(edge, HistoryEdgeAddChild) and edge.propertyownerid == "" and edge.propertyname == "":
                #A new document is being created by this edge
                doc = self.classes[edge.propertytype](edge.propertyvalue)
                doc.history = HistoryGraph()
                #Fixme: Add a creation function that does put any thing into the historygraph
                self.AddDocumentObject(doc)
            else:
                doc = self.objectsbyid[edge.propertyownerid].GetDocument()
            #    continue
            #if edge.propertyownerid not in self.objectsbyid:
            #    doc = self.classes[edge.propertytype](edge.propertyownerid)
            #    self.AddDocumentObject(doc)
            #print "self.documentsbyclass = ",self.documentsbyclass
            #print "edge.propertytype = ",edge.propertytype
            #print "edge.propertyownerid = ",edge.propertyownerid
            doc.history.AddEdge(edge)
            changes.add(doc.id)

        for documentid in changes:
            doc = self.objectsbyid[documentid]
            doc.history.Replay(doc)

       
    def GetByClass(self, theclass):
        #print "Getting object of class " + theclass.__name__
        return self.documentsbyclass[theclass.__name__]

    def AddDocumentObject(self, obj):
        #print "Added object of class " + obj.__class__.__name__
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


