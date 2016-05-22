#A DOOP history graph
from collections import defaultdict
import uuidcompat
from HistoryEdgeNull import HistoryEdgeNull
import DocumentCollection

class HistoryGraph(object):
    def __init__(self):
        self.edgesbystartnode = defaultdict(list)
        self.edgesbyendnode = dict()
        self.orphanededgesbystartnode = defaultdict(list)
        self.orphanededgesbyendnode = dict()
        self.isreplaying = False

    def AddEdge(self, edge):
        if self.isreplaying:
            return
        if edge.GetEndNode() in self.edgesbyendnode or edge.GetEndNode() in self.orphanededgesbyendnode:
            return
        nodes = edge.startnodes
        if edge.IsOrphan(self):
            for node in nodes:
                self.orphanededgesbystartnode[node].append(edge)
            self.orphanededgesbyendnode[edge.GetEndNode()] = edge
        else:                        
            for node in nodes:
                if node == "":
                    assert len(self.edgesbystartnode[node]) == 0 #There should only be one start node
                self.edgesbystartnode[node].append(edge)
            self.edgesbyendnode[edge.GetEndNode()] = edge
            if edge.GetEndNode() in self.orphanededgesbystartnode:
                edge2list = self.orphanededgesbystartnode[edge.GetEndNode()]
                del self.orphanededgesbystartnode[edge.GetEndNode()]
                for edge2 in edge2list:
                    del self.orphanededgesbyendnode[edge2.GetEndNode()]
                    self.AddEdge(edge2)
        if DocumentCollection.documentcollection.edgelistener is not None:
            DocumentCollection.documentcollection.edgelistener(edge)

    def Replay(self, doc):
        assert len(self.GetGraphEndNodes()) <= 1 #Confirm we don't need to merge before doing the replay
        self.isreplaying = True
        for k in self.edgesbyendnode:
            edge = self.edgesbyendnode[k]
            edge.isplayed = False
        l = self.edgesbystartnode[""]
        assert len(l) == 1
        self.ReplayEdges(doc, l[0])
        doc.history = self.Clone()
        self.isreplaying = False

    def Clone(self):
        ret = HistoryGraph()
        for k in self.edgesbyendnode:
            edge = self.edgesbyendnode[k]
            ret.AddEdge(edge.Clone())
        return ret

    def ReplayEdges(self, doc, edge):
        #print "Replaying ",edge.GetEndNode()
        if edge.CanReplay(self) == False:
            return
        edge.Replay(doc)
        edge.isplayed = True
        edges = self.edgesbystartnode[edge.GetEndNode()]
        if len(edges) > 0:
            for edge2 in edges:
                self.ReplayEdges(doc, edge2)
        else:
            doc.currentnode = edge.GetEndNode()

    def RecordPastEdges(self):
        if len(self.edges) == 0:
            return
        for k in self.edgesbyendnode:
            edge = self.edgesbyendnode[k]
            edge.ResetPastEdges()
        l = self.edgesbystartnode[""]
        assert len(l) == 1
        pastedges = set()
        l[0].RecordPastEdges(pastedges, self)

    def MergeGraphs(self, graph):
        for k in graph.edgesbyendnode:
            edge = graph.edgesbyendnode[k]
            self.AddEdge(edge)
            documentid = edge.documentid
            documentclassname = edge.documentclassname
        presentnodes = set()
        for k in self.edgesbyendnode:
            edge = self.edgesbyendnode[k]
            documentid = edge.documentid
            documentclassname = edge.documentclassname
            l = self.edgesbystartnode[edge.GetEndNode()]
            if len(l) == 0:
                presentnodes.add(edge.GetEndNode())
        if len(presentnodes) > 1:
            assert len(presentnodes) == 2
            extnode = uuidcompat.getuuid()
            nulledge = HistoryEdgeNull(uuidcompat.getuuid(), presentnodes, nextnode, "", "", "", "", documentid, documentclassname)
            self.AddEdge(nulledge)

    def ProcessConflictWinners(self):
        for k in self.edgesbyendnode:
            edge = self.edgesbyendnode[k]
            edge.inactive = False
        for k1 in self.edgesbyendnode:
            edge1 = self.edgesbyendnode[k1]
            for k2 in self.edgesbyendnode:
                edge2 = self.edgesbyendnode[k2]
                if k1 != k2:
                    if not edge2.HasPastEdge(k1) and not edge1.HasPastEdge(k2):
                        edge1.CompareForConflicts(edge2)
                        
    def GetAllEdges(self):
        ret = list()
        for (k, v) in self.edgesbyendnode.iteritems():
            ret.append(v)
        for (k, v) in self.orphanededgesbyendnode.iteritems():
            ret.append(v)
        return ret

    def GetGraphEndNodes(self):
        return self.GetGraphEndNodesImpl("")

    def GetGraphEndNodesImpl(self, startnodeid):
        #Returns a set of the endnodes of edges where the end nodes have no start node
        ret = set()
        edge = None
        for edge in self.edgesbystartnode[startnodeid]:
            ret = ret.union(self.GetGraphEndNodesImpl(edge.GetEndNode()))
        if edge is None:
            return { startnodeid }
        else:
            return ret

    def MergeDanglingBranches(self):
        endnodes = self.GetGraphEndNodes()
        print "MergeDanglingBranches len(endnodes) = ",len(endnodes)
        if len(endnodes) <= 1:
            return list()#There are no dangling end node
        #Create a merge node for the first two dangling end node
        endnodes = list(endnodes)
        edge = self.edgesbyendnode[endnodes[0]]
        nulledge = HistoryEdgeNull(endnodes[0:2], "", "", "", "", edge.documentid, edge.documentclassname)
        ret = [nulledge]
        self.AddEdge(nulledge)
        ret.extend(self.MergeDanglingBranches()) #Recur because there may be more than two nodes waiting to be merged
        return ret #Return a list of all of the nulledges we created so we can save then in a higher level module

        
