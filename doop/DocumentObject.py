#A DOOP Document Object
import uuidcompat
from Field import Field
from ChangeType import *
from FieldList import FieldList

class DocumentObject(object):
    def Clone(self):
        ret = self.__class__(self.id)
        ret.CopyDocumentObject(self)
        for prop in self.doop_field:
            if isinstance(prop, FieldList):
                retlist = ret.getattr(prop.name)
                retlist.empty()
                for obj in prop:
                    retlist.add(obj.Clone())
        return ret
    
    def __init__(self, id):
        self.insetattr = True
        self.changessuspended = False
        self.doop_field = dict()
        self.parent = None
        if id is None or id == "":
            id = uuidcompat.getuuid()
        self.id = id
        variables = [a for a in dir(self.__class__) if not a.startswith('__') and not callable(getattr(self.__class__,a))]
        for k in variables:
            var = getattr(self.__class__, k)
            self.doop_field[k] = var
            if isinstance(var, Field):
                setattr(self, k, var.CreateInstance(self, k))
        self.insetattr = False
        
    def __setattr__(self, name, value):
        haspreviousvalue = hasattr(self, name)
        if haspreviousvalue:
            previousvalue = getattr(self, name)
        super(DocumentObject, self).__setattr__(name, value)
        if name == "insetattr" or name == "parent" or name == "isreplaying" or name == "doop_field" or self.insetattr:
            return
        self.insetattr = True
        if name in self.doop_field:
            if haspreviousvalue and previousvalue != value:
                self.WasChanged(ChangeType.SET_PROPERTY_VALUE, self.id, name, value, self.doop_field[name].__class__.__name__)
        self.insetattr = False
         
    def WasChanged(self, changetype, propertyownerid, propertyname, propertyvalue, propertytype):
        if self.changessuspended:
            return
        if self.parent is not None:
            assert isinstance(propertyownerid, basestring)
            self.parent.WasChanged(changetype, propertyownerid, propertyname, propertyvalue, propertytype)

    def CopyDocumentObject(self, src):
        for k in src.doop_field:
            v = src.doop_field[k]
            setattr(self, k, v.Clone(k, src, self))

    def GetDocument(self):
        #Return the document
        return self.parent.GetDocument()

    def AsDict(self):
        #Return this object as a dictionary 
        for propname in self.doop_field:
            if isinstance(self.doop_field[propname], FieldList):
                ret[propname] = GetListAsDicts(getattr(self, propname))
            else:
                ret[propname] = getattr(self, propname)
    
    def GetDictableClassName(self):
        return self.__class__.__name__

    def PostProcessCreateFromDict(self, parentobj):
        pass

    def IsDocument(self):
        #Return if this is a document. Documents have history graphs
        return False

def GetListAsDicts(l):
    l2 = list()
    for obj in l:
        l2.append(obj.AsDict())
    return l2


def FillFromDict(d, classdict, parentobj):
    ret = classdict[d["classname"]]()
    #Set up a document object from the values in the dict
    for propname in self.doop_field:
        setattr(ret, propname, d[propname])
    ret.PostProcessCreateFromDict(parentobj)

