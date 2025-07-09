from io import BytesIO

from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class InMemoryStorage(Storage):
    """
    Простое файловое хранилище, которое держит файлы в памяти.
    Идеально для тестов.
    """

    def __init__(self):
        self.files = {}

    def _save(self, name, content):
        self.files[name] = BytesIO(content.read())
        return name

    def _open(self, name, mode="rb"):
        return self.files[name]

    def exists(self, name):
        return name in self.files

    def url(self, name):
        return f"/memory-media/{name}"
