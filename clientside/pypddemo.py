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

class PYPDDemo:
    def onModuleLoad(self):
        DocumentCollection.InitialiseDocumentCollection()
        DocumentCollection.documentcollection.Register(model.Drawing)
        DocumentCollection.documentcollection.Register(model.Triangle)

        self.mainpanel = MainPanel(self)
        RootPanel().add(self.mainpanel)

    

class MainPanel(VerticalPanel):
    CANVAS_WIDTH = 900
    CANVAS_HEIGHT = 700
    def __init__(self, owner):
        super(VerticalPanel, self).__init__()
        self.owner = owner

        uuidcompat.BufferUUIDs(100, self.InitialiseScreen)

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
        self.mouseisdown = False
        dc = DocumentCollection.documentcollection
        if len(dc.objects[model.Drawing.__class__.__name__]) == 0:
            self.drawing = model.Drawing()
            dc.AddDocumentObject(self.drawing)
        else:
            self.drawing = dc.objects[model.Drawing.__class__.__name__][0]
        self.Draw()

    def sortfn(self, t1, t2):
        return cmp(t1.z_order, t2.z_order)

    def Draw(self):
        self.canvas.setFillStyle(Color.WHITE)
        self.canvas.fillRect(0, 0, self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        #triangles = [self.drawing.triangles.GetDocument().documentobjects[objid] for objid in self.drawing.triangles]
        triangles = list()
        for triangle in self.drawing.triangles:
            #triangles = self.drawing.GetDocument().documentobjects[objid]
            triangles.append(triangle)
        if len(triangles) > 0:
            triangles.sort(self.sortfn)
        for t in triangles:
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

    def addtriangle(self, sender):
        pos = 50 + len(self.drawing.triangles) * 150
        t = model.Triangle(None)
        self.drawing.triangles.add(t)
        t.z_order = len(self.drawing.triangles)
        t.x1 = pos
        t.y1 = 50
        t.x2 = pos + 100
        t.y2 = 100
        t.x3 = pos + 50
        t.y3 = 150
        self.Draw()
    

    def onMouseDown(self, sender, x, y):
        pass

    def onMouseMove(self, sender, x, y):
        pass

    def onMouseUp(self, sender,x, y):
        pass

    def onMouseEnter(self, sender, x, y):
        pass

    def onMouseLeave(self, sender, x, y):
        pass

if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1/examples/jsonrpc/public/JSONRPCExample.html")
    app = PYPDDemo()
    app.onModuleLoad()
    #StyleSheetCssFileChanger("./indigo.css")
    pyjd.run()

