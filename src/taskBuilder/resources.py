class Element(object):
    name = ""
    filePath = None
    image = None

    def __init__(self, name, filePath, imgPath):
        self.name = name
        self.filePath = filePath
        self.image = imgPath

    def setImage(image):
        self.image = image