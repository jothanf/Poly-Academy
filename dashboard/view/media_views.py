import os
import uuid
from django.core.files.storage import default_storage

def save_multimedia_file(file, media_type):
    if not file:
        return None

    ext = os.path.splitext(file.name)[1]
    filename = f"content_media/{uuid.uuid4()}{ext}"
    path = default_storage.save(filename, file)
    
    return {
        'name': file.name,
        'url': default_storage.url(path),
        'path': path,
        'media_type': media_type,
        'size': file.size
    }
  