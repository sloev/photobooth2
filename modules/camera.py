from PIL import Image

class Camera():
    self._image = Image.open("test.jpg")
    def shoot(self):
        return self._image
