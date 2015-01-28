from PIL import Image

class Camera():
    def __init__(self):
        self._image = Image.open("test.jpg")
    def shoot(self):
        return self._image
