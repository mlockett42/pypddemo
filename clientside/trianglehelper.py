class TriangleHelper(object):
    #Handles the drawing of the triangle class in the client side

    def __init__(self, triangle):
        self.triangle = triangle

    def Draw(self, canvas):
        canvas.setFillStyle(Color.RED)
        canvas.setLineWidth(5)
        canvas.setStrokeStyle(Color.BLACK)
        canvas.setLineWidth(2)
        canvas.beginPath()
        canvas.moveTo(x1, y1)
        canvas.lineTo(x2, y2)
        canvas.lineTo(x3, y3)
        canvas.lineTo(x1, y1)
        canvas.fill()
        canvas.stroke()

