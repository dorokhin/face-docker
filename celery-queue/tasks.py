import os
import uuid
from celery import Celery
from PIL import Image, ImageDraw
import cognitive_face as CF
from io import BytesIO


KEY = '2a3f3331cee5467792531b245be3154f'
CF.Key.set(KEY)

BASE_URL = 'https://northeurope.api.cognitive.microsoft.com/face/v1.0'  # Replace with your regional Base URL
CF.BaseUrl.set(BASE_URL)

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379'),
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379')

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', '/home/deepblack/projects/python/face-docker/api/uploads/')
SERVICE_URL = os.getenv('SERVICE_URL', 'http://127.0.0.1:5000')

celery = Celery('tasks', broker=CELERY_BROKER_URL, backend=CELERY_RESULT_BACKEND)


def get_rectangle(face_dictionary):
    rect = face_dictionary['faceRectangle']
    left = rect['left']
    top = rect['top']
    bottom = left + rect['height']
    right = top + rect['width']
    return left, top, bottom, right


def get_filename():
    return '{}.jpg'.format(str(uuid.uuid4()))


@celery.task(name='tasks.mark_faces')
def mark_faces(filename):
    img_url = '{0}/uploads/{1}'.format(SERVICE_URL, filename)
    faces = CF.face.detect(img_url)

    with open(os.path.join(UPLOAD_FOLDER, filename)) as f:
        image = f.read()
    img = Image.open(BytesIO(image))

    # For each face returned use the face rectangle and draw a red box.
    draw = ImageDraw.Draw(img)
    for face in faces:
        draw.rectangle(get_rectangle(face), outline='red')

    image_name = get_filename()
    img.save(os.path.join(UPLOAD_FOLDER, image_name))
    return '''
    <!doctype html>
    <img src="{0}/uploads/{1}">
    '''.format(SERVICE_URL, image_name)
