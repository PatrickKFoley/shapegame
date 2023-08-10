class Request:
    def __init__(self, face_id = 0, color_id = 0, ready = False):
        self.face_id = face_id
        self.color_id = color_id
        self.ready = ready

    def getFaceId(self): return self.face_id
    
    def getColorId(self): return self.color_id

    def getReady(self): return self.ready