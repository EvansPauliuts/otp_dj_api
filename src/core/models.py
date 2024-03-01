from datetime import timezone

from django.db import models


class Timestamped(models.Model):
    created = models.DateTimeField(auto_now_add=True, db_index=True)
    updated = models.DateTimeField(
        auto_now=True,
        null=True,
        blank=True,
        db_index=True,
    )

    class Meta:
        abstract = True

    @property
    def changed(self):
        return True if self.updated else False

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated = timezone.now()
        return super().save(*args, **kwargs)


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self):
        return getattr(self, 'name', super().__str__())


class TimeStampedModel(DefaultModel, Timestamped):
    class Meta:
        abstract = True
