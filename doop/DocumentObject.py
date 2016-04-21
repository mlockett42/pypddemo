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
        #print "Debug 1"
        self.insetattr = True
        self.changessuspended = False
        self.doop_field = dict()
        self.parent = None
        #if id is None:
        #    id = uuidcompat.getuuid()
        id = uuidcompat.getuuid()
        self.id = id
        variables = [a for a in dir(self.__class__) if not a.startswith('__') and not callable(getattr(self.__class__,a))]
        for k in variables:
            var = getattr(self.__class__, k)
            self.doop_field[k] = var
            if isinstance(var, Field):
                setattr(self, k, var.CreateInstance(self, k))
        self.insetattr = False
        #print "Debug 10 self.insetattr = ",self.insetattr
        
    def __setattr__(self, name, value):
        #print "__setattr__ called self = ", self, " name = ", name, " value = ", value, " self.insetattr = ",self.insetattr
        super(DocumentObject, self).__setattr__(name, value)
        if name == "insetattr" or name == "parent" or name == "isreplaying" or name == "doop_field" or self.insetattr:
            return
        self.insetattr = True
        if name in self.doop_field:
            self.WasChanged(ChangeType.SET_PROPERTY_VALUE, self.id, name, value, type(value))
        self.insetattr = False
         
    def WasChanged(self, changetype, propertyownerid, propertyname, propertyvalue, propertytype):
        if self.changessuspended:
            return
        #print "was changed called self = ", self, changetype, propertyownerid, propertyname, propertyvalue, propertytype
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

def GetListAsDicts(l):
    l2 = list()
    for obj in l:
        #print "obj = " + repr(obj)
        l2.append(obj.AsDict())
    return l2


def FillFromDict(d, classdict, parentobj):
    ret = classdict[d["classname"]]()
    #Set up a document object from the values in the dict
    for propname in self.doop_field:
        setattr(ret, propname, d[propname])
    ret.PostProcessCreateFromDict(parentobj)

