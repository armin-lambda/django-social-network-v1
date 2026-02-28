import os
import uuid

from django.utils.text import slugify
from django.conf import settings


def get_user_image_upload_path(instance, filename):
    username = slugify(instance.username)
    filename = f"{username}{os.path.splitext(filename)[1]}"
    file_path = f"accounts/{username}/{filename}"
    full_path = os.path.join(settings.MEDIA_ROOT, file_path)

    if os.path.isfile(full_path):
        os.remove(full_path)
    return file_path


def get_gallery_image_upload_path(instance, filename):
    username = slugify(instance.user.username)
    filename = f"{uuid.uuid4()}{os.path.splitext(filename)[1]}"
    file_path = f"accounts/{username}/gallery_images/{filename}"

    return file_path
