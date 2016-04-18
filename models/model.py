from Document import Document
from DocumentObject import DocumentObject
from FieldList import FieldList
from FieldText import FieldText
from FieldInt import FieldInt

class Triangle(DocumentObject):
    x1 = FieldInt()
    y1 = FieldInt()
    x2 = FieldInt()
    y2 = FieldInt()
    x3 = FieldInt()
    y3 = FieldInt()
    z_order = FieldInt()

class Drawing(Document):
    triangles = FieldList(Triangle)


