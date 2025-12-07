from flask import request, session
import os

def save_image(image):
    if 'images' in session:
        image_path = os.path.join(session['images'], image.filename)
    else:
        image_path = '/path/to/default/images'

    image.save(image_path)

    return image_path
