import csv

from django.core import serializers
from django.http.response import HttpResponse

class ResponseTypeContext:
    file_type = None

    def type_context(self):
        if self.file_type is None:
            raise TypeError('Need add attribute file_type to application json or csv')
        return HttpResponse(
            content_type=self.file_type,
        )


class ExportToJSONMixin(ResponseTypeContext):
    file_type = 'application/json'

    def meta_fields(self):
        return self.model._meta

    def export_as_json(self, request, queryset):
        meta = self.meta_fields()
        fields_names = [field.name for field in meta.fields]
        response = super().type_context()
        response['Content-Disposition'] = f'attachment; filename={meta}.json'
        serializers.serialize('json', queryset, fields=fields_names, stream=response)
        return response


class ExportToCSVMixin(ResponseTypeContext):
    file_type = 'text/csv'

    def meta_fields(self):
        return self.model._meta

    def export_as_csv(self, request, queryset):
        meta = self.meta_fields()
        fields_names = [field.name for field in meta.fields]
        response = super().type_context()
        writer = csv.writer(response)
        writer.writerow(fields_names)
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in fields_names])
        return response
