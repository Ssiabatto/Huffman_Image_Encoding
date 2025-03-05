from PIL import Image

def split_image_channels(image):
    r, g, b = image.split()
    return r, g, b

def merge_image_channels(r, g, b):
    return Image.merge('RGB', (r, g, b))

def save_image(image, path):
    image.save(path)