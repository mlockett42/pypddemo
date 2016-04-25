#A DOOP history graph
from collections import defaultdict
import uuidcompat
from HistoryEdgeNull import HistoryEdgeNull
import DocumentCollection

class HistoryGraph(object):
    def __init__(self):
        self.edgesbystartnode = defaultdict(list)
        self.edgesbyendnode = dict()
        self.edges = dict()
        self.isreplaying = False

    def AddEdge(self, edge):
        if self.isreplaying:
            return
        if edge.edgeid in self.edges:
            return
        nodes = edge.startnodes
        for node in nodes:
            if node == "":
                assert len(self.edgesbystartnode[node]) == 0 #There should only be one start node
            self.edgesbystartnode[node].append(edge)
        self.edgesbyendnode[edge.endnode] = edge
        self.edges[edge.edgeid] = edge
        if DocumentCollection.documentcollection.edgelistener is not None:
            DocumentCollection.documentcollection.edgelistener(edge)

    def Replay(self, doc):
        assert len(self.GetGraphEndNodes()) <= 1 #Confirm we don't need to merge before doing the replay
        self.isreplaying = True
        for k in self.edges:
            edge = self.edges[k]
            edge.isplayed = False
        l = self.edgesbystartnode[""]
        assert len(l) == 1
        self.ReplayEdges(doc, l[0])
        doc.history = self.Clone()
        self.isreplaying = False

    def Clone(self):
        ret = HistoryGraph()
        for k in self.edges:
            edge = self.edges[k]
            ret.AddEdge(edge.Clone())
        return ret

    def ReplayEdges(self, doc, edge):
        if edge.CanReplay(self) == False:
            return
        edge.Replay(doc)
        edge.isplayed = True
        edges = self.edgesbystartnode[edge.endnode]
        if len(edges) > 0:
            for edge2 in edges:
                self.ReplayEdges(doc, edge2)
        else:
            doc.currentnode = edge.endnode

    def RecordPastEdges(self):
        if len(self.edges) == 0:
            return
        for k in self.edges:
            edge = self.edges[k]
            edge.ResetPastEdges()
        l = self.edgesbystartnode[""]
        assert len(l) == 1
        pastedges = set()
        l[0].RecordPastEdges(pastedges, self)

    def MergeGraphs(self, graph):
        for k in graph.edges:
            edge = graph.edges[k]
            self.AddEdge(edge)
            documentid = edge.documentid
            documentclassname = edge.documentclassname
        presentnodes = set()
        for k in self.edges:
            edge = self.edges[k]
            documentid = edge.documentid
            documentclassname = edge.documentclassname
            l = self.edgesbystartnode[edge.endnode]
            if len(l) == 0:
                presentnodes.add(edge.endnode)
        if len(presentnodes) > 1:
            assert len(presentnodes) == 2
            nextnode = uuidcompat.getuuid()
            nulledge = HistoryEdgeNull(uuidcompat.getuuid(), presentnodes, nextnode, "", "", "", "", documentid, documentclassname)
            self.AddEdge(nulledge)

    def ProcessConflictWinners(self):
        for k in self.edges:
            edge = self.edges[k]
            edge.inactive = False
        for k1 in self.edges:
            edge1 = self.edges[k1]
            for k2 in self.edges:
                edge2 = self.edges[k2]
                if k1 != k2:
                    if not edge2.HasPastEdge(k1) and not edge1.HasPastEdge(k2):
                        edge1.CompareForConflicts(edge2)
                        
    def GetAllEdges(self):
        ret = list()
        for (k, v) in self.edges.iteritems():
            ret.append(v)
        return ret

    def GetGraphEndNodes(self):
        return self.GetGraphEndNodesImpl("")

    def GetGraphEndNodesImpl(self, startnodeid):
        print "GetGraphEndNodesImpl called for ",startnodeid
        #Returns a set of the edgeids of edges where the end nodes have no start node
        ret = set()
        edge = None
        for edge in self.edgesbystartnode[startnodeid]:
            ret = ret.union(self.GetGraphEndNodesImpl(edge.endnode))
        if edge is None:
            print "GetGraphEndNodesImpl endnode found at ",startnodeid
            return { startnodeid }
        else:
            print "GetGraphEndNodesImpl no endnode found returning ",ret
            return ret
        
