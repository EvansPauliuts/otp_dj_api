from core.admin import ExportToCSVMixin
from core.admin import ExportToJSONMixin
from core.admin import admin

from apps.users.models import PendingUser


@admin.register(PendingUser)
class PendingUserAdmin(
    ExportToJSONMixin,
    ExportToCSVMixin,
    admin.ModelAdmin,
):
    list_display = (
        'id',
        'phone',
        'verification_code',
    )
    list_per_page = 10
    list_filter = ('phone',)
    search_fields = ('phone',)
    readonly_fields = ('verification_code',)
    ordering = ('-created',)
    actions = ('export_as_json', 'export_as_csv')

    @admin.action(description='Export to JSON')
    def export_as_json(self, request, queryset):
        return super().export_as_json(request, queryset)

    @admin.action(description='Export to CSV')
    def export_as_csv(self, request, queryset):
        return super().export_as_csv(request, queryset)
