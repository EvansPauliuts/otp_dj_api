from datetime import datetime
from datetime import timedelta

from django.db import models

from core.models import TimeStampedModel


class Page(TimeStampedModel):
    name = models.CharField(max_length=500)

    def post_count(self):
        return self.post_set.all().count()

    def metric_now(self):
        _post_list = (
            self.post_set.all()
            .filter(created__range=(datetime.now(), datetime.now() - timedelta(days=7)))
            .values('like_count', 'comment_count')
        )

        return sum(
            _post_list,
            lambda post: post['like_count'] + post['comment_count'],
        )


class Snapshot(TimeStampedModel):
    follower_count = models.PositiveIntegerField(default=0)
    taken_at = models.DateTimeField()
    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
    )


class Post(TimeStampedModel):
    like_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    page = models.ForeignKey(
        Page,
        on_delete=models.PROTECT,
    )
