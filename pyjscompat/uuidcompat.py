#pyjs has no native support for UUID's
#disabled this may not be necessary

from pyjamas.HTTPRequest import HTTPRequest
import urllib
from json import JSONParser

uuidlist = list()

class GetUUIDsCommand(object):
    #This class handles the asyncronous login to the website for tests
    def __init__(self):
        self.completionNotifier = None
        self.requestsize = 100
        
    def onError(self, text, code):
        print "GetUUIDsCommand attempt reports error"
        print "code = " + str(code)
        print "text = " + text
        assert False

    def onTimeout(self, text):
        print "text = " + text
        print "GetUUIDsCommand attempt reports timeout"
        assert False

    def doCommand(self):
        params = urllib.urlencode({"requestsize":self.requestsize })
        HTTPRequest().asyncPost(url = "/GetUUIDs", handler=self,returnxml=False,
            postData = params, content_type = "application/x-www-form-urlencoded",
                                headers={})
        #cloudconnection.Connect("POST",  "/GetUUIDs", {"requestsize":self.requestsize }, sessionid, self.onCompletion)

    def onCompletion(self, text):
        global uuidlist
        assert text != "Error"
        l = JSONParser().decode(text)
        uuidlist.extend(l)
        if self.completionNotifier != None:
            self.completionNotifier(text)

def getuuid():
    global uuidlist
    #print "In getUUID len(uuidlist) = " + str(len(uuidlist))
    ret = uuidlist.pop()
    if len(uuidlist) < 50:
        GetUUIDsCommand().doCommand(sessionid)
    if len(uuidlist) == 0:
        assert False
    return ret

def BufferUUIDs(numberrequired, completionfn):
    global uuidlist
    #print "len(pyjsuuid.uuidlist) = " + str(len(uuidlist))
    #print "numberrequired = " + str(numberrequired)
    if len(uuidlist) < numberrequired:
        command = GetUUIDsCommand()
        command.completionNotifier = completionfn
        command.requestsize = numberrequired
        command.doCommand()
    else:
        if completionfn:
            completionfn("")

