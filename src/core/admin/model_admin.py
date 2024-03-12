from collections.abc import Sequence
from typing import Any

from django import forms
from django.contrib import admin
from django.core.exceptions import ImproperlyConfigured
from django.db.models import QuerySet
from django.db.models.base import Model
from django.http import HttpRequest


class ModelAdmin(admin.ModelAdmin):
    pass


class StackedInline(admin.StackedInline):
    pass


class TabularInline(admin.TabularInline):
    pass


class GenericAdmin[_M: Model](admin.ModelAdmin[_M]):
    autocomplete = True

    def get_queryset(self, request: HttpRequest) -> QuerySet[_M]:
        return (
            super()
            .get_queryset(request)
            .select_related(*self.get_autocomplete_fields(request))
            .filter(organization_id=request.user.organization_id)
        )

    def save_model(
        self,
        request: HttpRequest,
        obj: _M,
        form: type[forms.BaseModelForm],
        *,
        change: bool,
    ) -> None:
        obj.organization = request.user.organization
        obj.business_unit = request.user.organization.business_unit
        super().save_model(request, obj, form, change)

    def save_formset(
        self,
        request: HttpRequest,
        form: Any,
        formset: Any,
        *,
        change: bool,
    ) -> None:
        instances = formset.save(commit=False)

        for instance in instances:
            instance.organization = request.user.organization
            instance.business_unit = request.user.business_unit
            instance.save()

        formset.save_m2m()
        super().save_formset(request, form, formset, change)

    def get_form(
        self,
        request: HttpRequest,
        obj: _M | None = None,
        *,
        change: bool = False,
        **kwargs: Any,
    ) -> type[forms.ModelForm[_M]]:
        form = super().get_form(request, obj, **kwargs)
        for field in form.base_fields:
            if field == 'organization':
                form.base_fields[field].initial = request.user.organization
                form.base_fields[field].widget = form.base_fields[field].hidden_widget()
            elif field == 'business_unit':
                form.base_fields[
                    field
                ].initial = request.user.organization.business_unit
                form.base_fields[field].widget = form.base_fields[field].hidden_widget()

            form.base_fields[field].widget.attrs['placeholder'] = field.title()

        return form

    def get_autocomplete_fields(self, request: HttpRequest) -> Sequence[str]:
        if self.autocomplete:
            if not self.search_fields:
                raise ImproperlyConfigured(
                    f'{type(self).__name__} must define `search_fields`'
                    ' when self.autocomplete is True',
                )

            return [
                field.name
                for field in self.model._meta.get_fields()  # noqa: SLF001
                if field.is_relation and field.many_to_one
            ]

        return []


class GenericStackedInline[_C: Model, _P: Model](StackedInline[_C, _P]):
    model: type[_C]
    extra = 0

    def get_queryset(self, request: HttpRequest) -> QuerySet[_C]:
        return (
            super()
            .get_queryset(request)
            .select_related(*self.get_autocomplete_fields(request))
            .filter(organization_id=request.user.organization_id)
        )

    def get_autocomplete_fields(self, request: HttpRequest) -> Sequence[str]:
        return [
            field.name
            for field in self.model._meta.get_fields()  # noqa: SLF001
            if field.is_relation and field.many_to_one
        ]


class GenericTabularInline[_C: Model, _P: Model](GenericStackedInline[_C, _P]):
    template = 'admin/edit_inline/tabular.html'


__all__ = [
    'GenericAdmin',
    'GenericStackedInline',
    'GenericTabularInline',
    'ModelAdmin',
    'StackedInline',
    'TabularInline',
    'admin',
]
