from django.db import models

class FileModel(models.Model):
    file = models.FileField(upload_to='file/')

    def __str__(self):
        return self.file.name


class ImageModel(models.Model):
    file = models.ImageField(upload_to='img/')

    def __str__(self):
        return self.file.name
