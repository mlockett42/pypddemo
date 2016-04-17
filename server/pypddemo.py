from twisted.internet import protocol, reactor
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File
from twisted.enterprise import adbapi
import uuid
import cgi
import time
from json import JSONEncoder, JSONDecoder
import datetime
from collections import defaultdict
import base64
from twisted.internet.defer import Deferred

#The main documentcollection
dc = None

class PYPDDemoSite(Site):
    def getResourceFor(self, request):
        request.setHeader('server',  'PYPDDemo/1.0')
        request.setHeader('cache-control: ',  'cache-control: private, max-age=0, no-cache')
        return Site.getResourceFor(self, request)

class PYPDDemo(Resource):
    #The root resource
    isLeaf = False
    def getChild(self, name, request):
        if name == '':
            request.setHeader('cache-control: ',  'cache-control: private, max-age=0, no-cache')
            return self
        return Resource.getChild(self, name, request)

    def addChildResources(self):
        self.putChild("StaticObjects", GetStaticObjects())
        self.putChild("GetUUIDs", GetUUIDsCommand())
        self.putChild("UploadEdges", UploadEdges())
        self.putChild("debug", File("../website/output"))
    def render_GET(self, request):
        return """
<script type="text/javascript">
<!--
window.location = "/debug/pypddemo.html"
//-->
</script>
"""

class GetUUIDsCommand(Resource):
    isLeaf = True

    def render_POST(self, request):
        requestsize = JSONDecoder().decode(request.args["requestsize"][0])
        l = list()
        for i in range(requestsize):
            l.append(str(uuid.uuid4()))
        return JSONEncoder().encode(l)

def _BuildTransaction(transaction, l):
    for sql in l:
        #print "Executing = " + sql
        transaction.execute(sql)
        
def BuildTransaction(l):
    return dbpool.runInteraction(_BuildTransaction, l)

class GetStaticObjects(Resource):
    # Get staticobjects is the 'product list'
    isLeaf = True

    def render_POST(self, request):
        edgeids = JSONDecoder().decode(request.args["edgeids"][0])
        global dc       
        return dc.asJson(set(edgeids))

class UploadEdges(Resource):
    # Get staticobjects is the 'product list'
    isLeaf = True

    def render_POST(self, request):
        edges = JSONDecoder().decode(request.args["edges"][0])
        global dc       
        dc.AddEdges(edges)
        return "OK"

def StartApplication(resource):
    #load the schema
    DocumentCollection.Register(model.Drawing)
    DocumentCollection.Register(model.Triangle)
    global dc
    dc = LoadDocumentCollection.Load('drawing.history.db', 'drawing.content.db')

    globalvars.uuidfn = lambda x: str(uuid.uuid4())

    resource.addChildResources()
    
    factory = PYPDDemoSite(resource)
    reactor.listenTCP(resource.GetPort(), factory)
    reactor.callLater(1, Tickle)
    reactor.run()

StartApplication(PYPDDemo())

