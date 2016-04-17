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
from DocumentCollection import DocumentCollection
from pyjamas.Canvas.GWTCanvas import GWTCanvas
from pyjamas.Canvas import Color

class PYPDDemo:
    def onModuleLoad(self):
        self.mainpanel = MainPanel(self)
        RootPanel().add(self.mainpanel)
    

class MainPanel(VerticalPanel):
    CANVAS_WIDTH = 3000
    CANVAS_HEIGHT = 3000
    def __init__(self, owner):
        super(VerticalPanel, self).__init__()
        self.owner = owner
        hpanel = HorizontalPanel()
        self.add(hpanel)
        vpanelMenu = VerticalPanel()
        hpanel.add(vpanelMenu)
        self.addbutton = Button("Add Triangle")
        vpanelMenu.add(self.addbutton)
        self.addbutton.addClickListener(getattr(self, "addtriangle"))
        self.canvas = GWTCanvas(self.CANVAS_WIDTH, self.CANVAS_HEIGHT)
        vpanelCanvas = VerticalPanel()
        vpanelCanvas.setWidth(600)
        hpanel.add(vpanelCanvas)
        vpanelCanvas.add(self.canvas)
        self.canvas.addMouseListener(self)
        self.selecteditem = None
        self.mouseisdown = False
        self.canvas.setFillStyle(Color.RED)
        self.canvas.fillRect(0, 0, self.CANVAS_WIDTH-1, self.CANVAS_HEIGHT-1)

    def addtriangle(self, sender):
        pass

    def onMouseDown(self, sender, x, y):
        pass

    def onMouseMove(self, sender, x, y):
        pass

    def onMouseUp(self, sender,x, y):
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

