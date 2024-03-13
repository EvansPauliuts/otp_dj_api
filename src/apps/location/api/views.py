from core.permissions import CustomObjectPermissions
from django.db.models import F
from django.db.models import Prefetch

# from django.db.models import QuerySet
from rest_framework import permissions
from rest_framework import viewsets

from apps.location.api.serializers import LocationSerializer
from apps.location.api.serializers import StatesSerializer
from apps.location.models import Location
from apps.location.models import LocationComment
from apps.location.models import LocationContact
from apps.location.models import States


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    filterset_fields = (
        'location_category__name',
        'depot__name',
        'is_geocoded',
        'status',
    )
    search_fields = (
        'name',
        'code',
    )
    permission_classes = (CustomObjectPermissions,)
    http_method_names = ('get', 'post', 'put', 'patch', 'head', 'options')

    def get_queryset(self):
        return (
            self.queryset.filter(
                organization_id=self.request.user.organization_id,
            )
            .prefetch_related(
                Prefetch(
                    lookup='location_comments',
                    queryset=LocationComment.objects.filter(
                        organization_id=self.request.user.organization_id,
                    )
                    .select_related(
                        'entered_by',
                        'comment_type',
                        'entered_by__profiles',
                    )
                    .annotate(
                        comment_type_name=F('comment_type__name'),
                    )
                    .all(),
                ),
                Prefetch(
                    lookup='location_contacts',
                    queryset=LocationContact.objects.filter(
                        organization_id=self.request.user.organization_id,
                    ).all(),
                ),
            )
            .select_related('location_category')
            # .annotate(
            #     # wait_time_avg=Avg(
            #     #     ExpressionWrapper(
            #     #         (
            #     #             Extract('stop__departure_time', 'epoch')
            #     #             - Extract('stop__arrival_time', 'epoch')
            #     #         )
            #     #         / 60,
            #     #         output_field=FloatField(),
            #     #     ),
            #     # ),
            #     # pickup_count=Count(
            #     #     Case(
            #     #         When(
            #     #             stop__type_type__in=['P', 'SP'],
            #     #             stop__arrival_time__isnull=False,
            #     #             stop__status=StatusChoices.COMPLETED,
            #     #             then=1,
            #     #         ),
            #     #         default=None,
            #     #         output_field=IntegerField(),
            #     #     ),
            #     # ),
            #     location_color=F('location_category__color'),
            #     location_category_name=F('location_category__name'),
            # )
        )


class StateViewSet(viewsets.ModelViewSet):
    queryset = States.objects.all()
    serializer_class = StatesSerializer
    permission_classes = (permissions.AllowAny,)
    http_method_names = ('get', 'head', 'options')
