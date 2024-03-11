from datetime import datetime, timedelta

from rest_framework import status
from django.db.models import F, Q, Max, Sum, Count, OuterRef, Subquery, IntegerField
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from apps.snapshot.models import Page, Post, Snapshot


class PageViewSet(ModelViewSet):
    queryset = Page.objects.all()
    http_method_names = ('get',)

    def list(self, request, *args, **kwargs):
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
