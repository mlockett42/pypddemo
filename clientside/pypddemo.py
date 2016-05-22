import pyjd # dummy in pyjs

from pyjamas.ui.RootPanel import RootPanel
from pyjamas.ui.TextArea import TextArea
from pyjamas.ui.TextBox import TextBox
from pyjamas.ui.Label import Label
from pyjamas.ui.Button import Button
from pyjamas.ui.HTML import HTML
from pyjamas.ui.VerticalPanel import VerticalPanel
from pyjamas.ui.HorizontalPanel import HorizontalPanel
from pyjamas.ui.ListBox import ListBox
from pyjamas.JSONService import JSONProxy
from pyjamas.ui.RadioButton import RadioButton
from pyjamas.ui.CheckBox import CheckBox
from pyjamas import Window
import pygwt
from pyjamas.Timer import Timer
from pyjamas.HTTPRequest import HTTPRequest
import DocumentCollection
from pyjamas.Canvas.GWTCanvas import GWTCanvas
from pyjamas.Canvas import Color
import model
import uuidcompat
import math
import urllib
from jsoncompat import JSONEncoder, JSONDecoder

class PYPDDemo:
    def onError(self, text, code):
        Window.alert("Error code = " + str(code) + " text = " + text)

    def onTimeout(self, text):
        Window.alert("Error text = " + text)

    def onCompletion(self, text):
        edges = JSONDecoder(text)
        nulledges = DocumentCollection.documentcollection.LoadFromJSON(edges)

        #If we created any nulledges for merge send them back to the server
        edgequeue = [edge.asDict() for edge in nulledges]
        EdgePoster(edgequeue).schedule(1) #Schedule in the future so edges are sent in bulk

        self.mainpanel = MainPanel(self)
        RootPanel().add(self.mainpanel)

    def onModuleLoad(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(model.Drawing)
        DocumentCollection.documentcollection.Register(model.Triangle)

        uuidcompat.BufferUUIDs(1000, self.LoadStaticObjects)

    def LoadStaticObjects(self):
        params = urllib.urlencode({"edgeids": [] })
        HTTPRequest().asyncPost(url = "/StaticObjects", handler=self,returnxml=False, postData = params, content_type = "application/x-www-form-urlencoded")

class StaticObjectsTask(Timer):
    def __init__(self, callbackfn):
        super(StaticObjectsTask, self).__init__()
        self.callbackfn = callbackfn

    def run(self):
        edgeids = JSONEncoder(DocumentCollection.documentcollection.GetAllEndNodes())
        params = urllib.urlencode({"edgeids": edgeids })
        HTTPRequest().asyncPost(url = "/StaticObjects", handler=self,returnxml=False, postData = params, content_type = "application/x-www-form-urlencoded")

    def onError(self, text, code):
        print("Error code = " + str(code) + " text = " + text)
        self.ScheduleTask()

    def onTimeout(self, text):
        print("Error text = " + text)
        self.ScheduleTask()

    def onCompletion(self, text):
        edges = JSONDecoder(text)
        nulledges = DocumentCollection.documentcollection.LoadFromJSON(edges)

        #If we created any nulledges for merge send them back to the server
        edgequeue = [edge.asDict() for edge in nulledges]
        EdgePoster(edgequeue).schedule(1) #Schedule in the future so edges are sent in bulk

        self.ScheduleTask()
        self.callbackfn()

    def ScheduleTask(self):
        StaticObjectsTask(self.callbackfn).schedule(5000) #Poll every five seconds
        

class EdgePoster(Timer):
    def onError(self, text, code):
        Window.alert("Error code = " + str(code) + " text = " + text)

    def onTimeout(self, text):
        Window.alert("Error text = " + text)

    def onCompletion(self, text):
        pass

    def __init__(self, edges):
        super(EdgePoster,self).__init__()
        self.edges = edges

    def run(self):
        assert isinstance(self.edges, list)
        if len(self.edges) == 0:
            return #Another schuled task send our edges so do nothin
        params = urllib.urlencode({"edges":  JSONEncoder(self.edges)})
        HTTPRequest().asyncPost(url = "/UploadEdges", handler=self,returnxml=False, postData = params, content_type = "application/x-www-form-urlencoded")
        del self.edges[:] #delete the contents of the edge queue


class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y

#Determining if a point is inside a triangle copied from this stack overflow answer
#http://stackoverflow.com/a/2049593
def Sign (p1, p2, p3):
    return (p1.x - p3.x) * (p2.y - p3.y) - (p2.x - p3.x) * (p1.y - p3.y);

def PointInTriangle (pt, triangle):
    v1 = Point(triangle.x1, triangle.y1)
    v2 = Point(triangle.x2, triangle.y2)
    v3 = Point(triangle.x3, triangle.y3)

    b1 = Sign(pt, v1, v2) < 0.0;
    b2 = Sign(pt, v2, v3) < 0.0;
    b3 = Sign(pt, v3, v1) < 0.0;

    return ((b1 == b2) and (b2 == b3));

def HandleSelected(x1,y1,x2,y2):
    #Return True if the handle was selected
    return (x2 - x1)**2 + (y2 - y1)**2 <= 5**2

class MainPanel(VerticalPanel):
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 700
    def __init__(self, owner):
        super(VerticalPanel, self).__init__()
        self.edgequeue = list()
        self.owner = owner
        self.InitialiseScreen()
        StaticObjectsTask(self.Draw).schedule(5000) #Poll every five seconds

    def EdgeListener(self, edge):
        self.edgequeue.append(edge.asDict())
        EdgePoster(self.edgequeue).schedule(1) #Schedule in the future so edges are sent in bulk

    def InitialiseScreen(self):
        hpanel = HorizontalPanel()
        self.add(hpanel)
        vpanelMenu = VerticalPanel()
        hpanel.add(vpanelMenu)
        self.addbutton = Button("Add Triangle")
        vpanelMenu.add(self.addbutton)
        self.addbutton.addClickListener(getattr(self, "addtriangle"))
        self.canvas = GWTCanvas(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        vpanelCanvas = VerticalPanel()
        self.canvas.setWidth(self.CANVAS_WIDTH)
        self.canvas.setHeight(self.CANVAS_HEIGHT)
        hpanel.add(vpanelCanvas)
        vpanelCanvas.add(self.canvas)
        self.canvas.addMouseListener(self)
        self.selecteditem = None
        self.selectedhandle = None
        self.mouseisdown = False
        dc = DocumentCollection.documentcollection
        DocumentCollection.documentcollection.edgelistener = self.EdgeListener
        if len(dc.documentsbyclass[model.Drawing.__name__]) == 0:
            drawing = model.Drawing(None)
            dc.AddDocumentObject(drawing)
            EdgePoster([a.asDict() for a in drawing.history.GetAllEdges()])
        else:
            for k,v in dc.documentsbyclass[model.Drawing.__name__].iteritems():
                drawing = v
        self.drawingid = drawing.id
        self.Draw()

    def GetDrawing(self):
        return DocumentCollection.documentcollection.objectsbyid[self.drawingid]

    def sortfn(self, t1, t2):
        return cmp(t1.z_order, t2.z_order)

    def GetTrianglesAsList(self):
        #Return the triangles as an ordinary python list
        #triangles = [self.drawing.triangles.GetDocument().documentobjects[objid] for objid in self.drawing.triangles]
        triangles = list()
        for triangle in self.GetDrawing().triangles:
            #triangles = self.drawing.GetDocument().documentobjects[objid]
            triangles.append(triangle)
        if len(triangles) > 0:
            triangles.sort(self.sortfn)
        return triangles

    def DrawHandle(self,x,y):
        self.canvas.setFillStyle(Color.RED)
        self.canvas.beginPath()
        self.canvas.arc(x, y, 5, 0,  math.pi * 2, False)
        self.canvas.fill()

    def Draw(self):
        self.canvas.setFillStyle(Color.WHITE)
        self.canvas.fillRect(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        for t in self.GetTrianglesAsList():
            self.canvas.setFillStyle(Color.BLUE)
            self.canvas.setLineWidth(5)
            self.canvas.setStrokeStyle(Color.BLACK)
            self.canvas.setLineWidth(2)
            self.canvas.beginPath()
            self.canvas.moveTo(t.x1, t.y1)
            self.canvas.lineTo(t.x2, t.y2)
            self.canvas.lineTo(t.x3, t.y3)
            self.canvas.lineTo(t.x1, t.y1)
            self.canvas.fill()
            self.canvas.stroke()

            if self.selecteditem == t:
                self.canvas.setLineWidth(1)
                self.canvas.setStrokeStyle(Color.RED)
                self.canvas.beginPath()
                self.canvas.moveTo(t.x1, t.y1)
                self.canvas.lineTo(t.x2, t.y2)
                self.canvas.lineTo(t.x3, t.y3)
                self.canvas.lineTo(t.x1, t.y1)
                self.canvas.stroke()
            
                self.DrawHandle(t.x1, t.y1)
                self.DrawHandle(t.x2, t.y2)
                self.DrawHandle(t.x3, t.y3)

    def addtriangle(self, sender):
        left_margin = 50
        triangle_spacing = 150
        drawing = self.GetDrawing()
        c = len(drawing.triangles)
        posx = left_margin + c % ((self.CANVAS_WIDTH - left_margin) // triangle_spacing) * triangle_spacing
        posy = c // ((self.CANVAS_WIDTH - left_margin) // triangle_spacing) * triangle_spacing
        t = model.Triangle(None)
        drawing.triangles.add(t)
        t.z_order = c
        setattr(t, 'x1', posx)
        setattr(t, 'y1', posy + 50)
        setattr(t, 'x2', posx + 100)
        setattr(t, 'y2', posy + 100)
        setattr(t, 'x3', posx + 50)
        setattr(t, 'y3', posy + 150)
        self.Draw()
    

    def onMouseDown(self, sender, x, y):
        self.mouseisdown = True
        if self.selecteditem is not None:
            self.selectedhandle = None
            if HandleSelected(x,y, self.selecteditem.x1, self.selecteditem.y1):
                self.selectedhandle = 1
            elif HandleSelected(x,y, self.selecteditem.x2, self.selecteditem.y2):
                self.selectedhandle = 2
            elif HandleSelected(x,y, self.selecteditem.x3, self.selecteditem.y3):
                self.selectedhandle = 3
        if self.selectedhandle is None:
            self.selecteditem = self.FindTriangle(x,y)
        if self.selecteditem is None and self.selectedhandle is None:
            self.selectedhandle = None
        if self.selecteditem is not None:
            self.selecteditem.changessuspended = True
        self.Draw()
        self.lastx = x
        self.lasty = y

    def onMouseMove(self, sender, x, y):
        if self.selecteditem is not None and self.mouseisdown:
            diffx = x - self.lastx
            diffy = y - self.lasty
            t = self.selecteditem
            if self.selectedhandle is None:
                setattr(t, 'x1', t.x1 + diffx)
                setattr(t, 'y1', t.y1 + diffy)
                setattr(t, 'x2', t.x2 + diffx)
                setattr(t, 'y2', t.y2 + diffy)
                setattr(t, 'x3', t.x3 + diffx)
                setattr(t, 'y3', t.y3 + diffy)
            elif self.selectedhandle == 1:
                setattr(t, 'x1', t.x1 + diffx)
                setattr(t, 'y1', t.y1 + diffy)
            elif self.selectedhandle == 2:
                setattr(t, 'x2', t.x2 + diffx)
                setattr(t, 'y2', t.y2 + diffy)
            elif self.selectedhandle == 3:
                setattr(t, 'x3', t.x3 + diffx)
                setattr(t, 'y3', t.y3 + diffy)
            self.lastx = x
            self.lasty = y
            self.Draw()

    def onMouseUp(self, sender,x, y):
        if self.mouseisdown and self.selecteditem:
            t = self.selecteditem
            self.selecteditem.changessuspended = False
            setattr(t, 'x1', t.x1)
            setattr(t, 'y1', t.y1)
            setattr(t, 'x2', t.x2)
            setattr(t, 'y2', t.y2)
            setattr(t, 'x3', t.x3)
            setattr(t, 'y3', t.y3)
        self.mouseisdown = False

    def onMouseEnter(self, sender, x, y):
        pass

    def onMouseLeave(self, sender, x, y):
        pass

    def FindTriangle(self, x, y):
        pt = Point(x, y)
        for t in self.GetTrianglesAsList():
            if PointInTriangle(pt, t):
                return t
        return None

if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1/examples/jsonrpc/public/JSONRPCExample.html")
    app = PYPDDemo()
    app.onModuleLoad()
    #StyleSheetCssFileChanger("./indigo.css")
    pyjd.run()

