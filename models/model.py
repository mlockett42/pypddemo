from Document import Document
from DocumentObject import DocumentObject

class Drawing(Document):
    triangles = FieldList(Triangle)
    name = FieldText()

class Triangle(DocumentObject):
    x1 = FieldInt()
    y1 = FieldInt()
    x2 = FieldInt()
    y2 = FieldInt()
    x3 = FieldInt()
    y3 = FieldInt()

