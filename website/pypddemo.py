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

class OscarPOS:
    def onModuleLoad(self):

        self.mainpanel = MainPanel(self)

	    RootPanel().add(self.mainpanel)
	    objfactory.InitialiseObjFactory()
	

class MainPanel(VerticalPanel):
    def __init__(self, owner):
        super(VerticalPanel, self).__init__()
        self.owner = owner
	vpanel = VerticalPanel()
	vpanel.add(Label("Hello world"))
    




























if __name__ == '__main__':
    # for pyjd, set up a web server and load the HTML from there:
    # this convinces the browser engine that the AJAX will be loaded
    # from the same URI base as the URL, it's all a bit messy...
    pyjd.setup("http://127.0.0.1/examples/jsonrpc/public/JSONRPCExample.html")
    app = PYPDDemo()
    app.onModuleLoad()
    #StyleSheetCssFileChanger("./indigo.css")
    pyjd.run()

