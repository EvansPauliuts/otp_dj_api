from datetime import datetime
from datetime import timedelta

from django.db.models import Count
from django.db.models import F
from django.db.models import IntegerField
from django.db.models import Max
from django.db.models import OuterRef
from django.db.models import Q
from django.db.models import Subquery
from django.db.models import Sum
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.snapshot.models import Page
from apps.snapshot.models import Post
from apps.snapshot.models import Snapshot

# from operator import itemgetter


class PageViewSet(ModelViewSet):
    queryset = Page.objects.all()
    http_method_names = ('get',)

    def list(self, request, *args, **kwargs):
        """
        Show the list of Pages by its name, number of posts and the
        sum of all the post’s like_count and comment_count that was created
        in the last 7 days. Order DESC by its number of posts
        """
        _filter = Q(created__range=(datetime.now(), datetime.now() - timedelta(days=7)))

        pages_1 = (
            self.queryset.annotate(
                metric_sum=Sum('post__comment_count', filter=_filter)
                + Sum('like_count', filter=_filter),
                post_count=Count('post', distinct=True),
            )
            .order_by('post_count')
            .values(
                'metric_sum',
                'post_count',
                'name',
            )
        )

        """
        Show the list of Pages by its name, Max of it followers in the last 7
        days and the sum of all the post’s like_count and comment_count that was created
        in the last 7 days. Order DESC by its number of followers
        """

        pages_2 = (
            self.queryset.annotate(
                metric_sum=Sum('post__comment_count', filter=_filter)
                + Sum('post__like_count', filter=_filter),
                max_follower=Max('snapshot__follower_count', filter=_filter),
            )
            .order_by('max_follower')
            .values(
                'metric_sum',
                'max_follower',
                'name',
            )
        )

        return Response(
            {
                'message': 'Page',
                'pages_1': pages_1,
                'pages_2': pages_2,
            },
            status=status.HTTP_200_OK,
        )


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    http_method_names = ('get',)

    def list(self, request, *args, **kwargs):
        _filter = Q(created__range=(datetime.now(), datetime.now() - timedelta(days=7)))

        sub_query = (
            self.queryset.filter(
                page=OuterRef('id'),
                created__range=_filter,
            )
            .annotate(
                sum_value=F('comment_count') + F('like_count'),
            )
            .values('sum_value')
        )

        pages_1 = (
            Page.objects.all()
            .annotate(
                metric_sum=Subquery(
                    sub_query,
                    template='(SELECT SUM(sum_value) FROM (%(subquery)s) _sum',
                    output_field=IntegerField(),
                ),
                max_follower=Max('point__point', filter=_filter),
            )
            .order_by('-max_follower')
        )

        """
        All this line just make 1 query, so don’t worry. Now, there just one JOINs
        so it make fastest query and less time to load your website.
        Remember to check the numbers is correct.
        """

        sub_query_max = (
            Snapshot.objects.filter(
                page=OuterRef('id'),
            )
            .order_by('-follower_count')
            .values('follower_count')[:1]
        )

        pages_2 = (
            Page.objects.all()
            .annotate(
                metric_sum=Subquery(
                    sub_query,
                    template='(SELECT SUM(sum_value) FROM (%(subquery)s) _sum)',
                    output_field=IntegerField(),
                ),
                max_follower=Subquery(
                    sub_query_max,
                    output_field=IntegerField(),
                ),
            )
            .order_by('-max_follower')
        )

        return Response(
            {
                'message': 'Post',
                'pages_1': pages_1,
                'pages_2': pages_2,
            },
            status=status.HTTP_200_OK,
        )
