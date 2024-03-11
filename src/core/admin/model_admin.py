from django.contrib import admin


class ModelAdmin(admin.ModelAdmin):
    pass


class StackedInline(admin.StackedInline):
    pass


class TabularInline(admin.TabularInline):
    pass


__all__ = [
    'ModelAdmin',
    'StackedInline',
    'TabularInline',
    'admin',
]
