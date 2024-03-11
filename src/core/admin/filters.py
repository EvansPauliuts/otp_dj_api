from django.contrib import admin

class BooleanFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        return [
            ('t', 'Yes'),
            ('f', 'No'),
        ]

    def queryset(self, request, queryset):
        if not self.value():
            return queryset

        if self.value() == 't':
            return self.t(request, queryset)

        return self.f(request, queryset)


class DefaultTrueBooleanFilter(BooleanFilter):
    def queryset(self, request, queryset):
        if not self.value() or self.value() == 't':
            return self.t(request, queryset)
        return self.f(request, queryset)


class DefaultFalseBooleanFilter(BooleanFilter):
    def queryset(self, request, queryset):
        if not self.value() or self.value() == 'f':
            return self.f(request, queryset)
        return self.t(request, queryset)


__all__ = [
    'BooleanFilter',
    'DefaultTrueBooleanFilter',
]
