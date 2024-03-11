from django_filters import filters

class UUIDInFilter(filters.BaseInFilter, filters.CharFilter):
    pass
