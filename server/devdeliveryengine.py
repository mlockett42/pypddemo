from twisted.internet import protocol, reactor
from twisted.web.resource import Resource
from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.static import File

import deliveryengine
import setting
import datetime
import utils

class DebugMockTime(Resource):
    isLeaf = True

    def render_POST(self, request):
        dummytime = request.args["dummytime"][0]

        if dummytime == "livetime":
            #print "Setting server time to livetime"
            utils.storeddate = None
            utils.setGetNowFn(utils.getNowOriginal)
        else:
            #print "Setting server time to " + dummytime
            utils.storeddate = datetime.datetime.strptime( dummytime, "%Y-%m-%d %H:%M:%S" )
            utils.setGetNowFn(utils.getStoredDate)

        return "OK"

class DebugDeleteAllSales(Resource):
    isLeaf = True

    def reply(self, data):
        self.request.write("OK")
        self.request.finish()
        self.request = None
        

    def render_POST(self, request):
        sql = list()
        sql.append("DELETE FROM SaleItem")
        sql.append("DELETE FROM PaymentSale")
        sql.append("DELETE FROM Sale")
        sql.append("DELETE FROM Payment")
        sql.append("DELETE FROM printout")
        sql.append("DELETE FROM scheduledsale")
        sql.append("DELETE FROM scheduledsaleupdaterequest")
        self.request = request
        d = deliveryengine.BuildTransaction(sql)
        d.addCallback(lambda x: PrintMessage("Finished DebugDeleteAllSales"))
        d.addCallback(self.reply)
        deliveryengine.opensales = dict()
        setting.SetSettingValue('NextSaleNumber', '1')
        return NOT_DONE_YET

def PrintMessage(s):
    print s

class DebugReloadFromDatabase(Resource):
    isLeaf = True

    def reply(self, data):
        self.request.write("OK")
        self.request.finish()
        self.request = None
        

    def render_POST(self, request):
        self.request = request
        d = deliveryengine.loadDatabase2(None)
        d.addCallback(lambda x: deliveryengine.createWordList())
        d.addCallback(lambda x: deliveryengine.LoadUserDict())
        d.addCallback(lambda x: PrintMessage("Finished DebugReloadFromDatabase"))
        d.addCallback(self.reply)
        return NOT_DONE_YET

class DebugReinitialiseDatabase(Resource):
    isLeaf = True

    def reply(self, data):
        self.request.write("OK")
        self.request.finish()
        self.request = None
        

    def render_POST(self, request):
        self.request = request
        d = deliveryengine.reinitialiseDebugDatabase()
        #d.addCallback(deliveryengine.loadDatabase())
        deliveryengine.loadDatabase2(d)
        d.addCallback(lambda x: deliveryengine.createWordList())
        d.addCallback(lambda x: deliveryengine.LoadUserDict())
        d.addCallback(lambda x: PrintMessage("Finished DebugReinitialiseDatabase"))
        d.addCallback(self.reply)
        return NOT_DONE_YET

class DebugDeleteAllPrintouts(Resource):
    isLeaf = True

    def reply(self, data):
        self.request.write("OK")
        self.request.finish()
        self.request = None
        

    def render_POST(self, request):
        sql = list()
        sql.append("DELETE FROM printout")
        self.request = request
        d = deliveryengine.BuildTransaction(sql)
        d.addCallback(lambda x: PrintMessage("Finished DebugDeleteAllPrintouts"))
        d.addCallback(self.reply)
        return NOT_DONE_YET

class DevDeliveryEngine(deliveryengine.DeliveryEngine):
    def render_GET(self, request):
        return """
<script type="text/javascript">
<!--
window.location = "/debug/deliveryengine.html"
//-->
</script>
"""

    def GetPort(self):
        return 8081

    def addChildResources(self):
        self.addChildResources2()
        self.putChild("debug", File("/home/mark/deliveryengine/website/clientside/output"))
        self.putChild("bootstrap", File("/home/mark/deliveryengine/website/clientside/bootstrap"))
        self.putChild("images", File("/home/mark/deliveryengine/website/clientside/images"))
        self.putChild("DebugDeleteAllSales", DebugDeleteAllSales())
        self.putChild("DebugReloadFromDatabase", DebugReloadFromDatabase())
        self.putChild("DebugReinitialiseDatabase", DebugReinitialiseDatabase())
        self.putChild("DebugDeleteAllPrintouts", DebugDeleteAllPrintouts())
        self.putChild("DebugMockTime", DebugMockTime())

deliveryengine.shouldcache = False
deliveryengine.StartApplication(DevDeliveryEngine())
