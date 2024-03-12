# from re import escape
# from typing import Any
#
# # from core.admin.model_admin import GenericAdmin
# # from core.admin.model_admin import GenericStackedInline
# from django.conf import settings
# from django.contrib import admin
# from django.contrib import messages
# from django.contrib.admin import ModelAdmin
# from django.contrib.admin.options import IS_POPUP_VAR
# from django.contrib.admin.options import csrf_protect_m
# from django.contrib.admin.utils import unquote
# from django.contrib.auth import update_session_auth_hash
# from django.contrib.auth.admin import AdminPasswordChangeForm
# from django.contrib.auth.admin import GroupAdmin
# from django.contrib.auth.admin import UserChangeForm
# from django.contrib.auth.admin import UserCreationForm
# from django.contrib.auth.admin import sensitive_post_parameters_m
# from django.contrib.sessions.models import Session
# from django.core.exceptions import PermissionDenied
# from django.db import router
# from django.db import transaction
# from django.db.models import QuerySet
# from django.forms.models import ModelForm
# from django.http import Http404
# from django.http import HttpRequest
# from django.http import HttpResponse
# from django.http import HttpResponseRedirect
# from django.template.response import TemplateResponse
# from django.urls import URLPattern
# from django.urls import path
# from django.urls import reverse
#
# from apps.accounts.models import CustomGroup
# from apps.accounts.models import JobTitle
# from apps.accounts.models import Token
# from apps.accounts.models import User
# from apps.accounts.models import UserFavorite
# from apps.accounts.models import UserProfile
#
#
# # class ProfileInline(GenericStackedInline[User, UserProfile]):
# #     model = UserProfile
# #     fk_name = 'user'
#
#
# @admin.register(Token)
# class TokenAdmin(admin.ModelAdmin[Token]):
#     model = Token
#     list_display = ('user', 'created')
#     search_fields = ('user', 'key')
#
#
# @admin.register(User)
# class UserAdmin(admin.ModelAdmin[User]):
#     change_user_password_template = None
#     fieldsets = (
#         (
#             None,
#             {
#                 'fields': (
#                     'is_active',
#                     'business_unit',
#                     'organization',
#                     'department',
#                     'username',
#                     'email',
#                     'timezone',
#                     'password',
#                     'online',
#                 ),
#             },
#         ),
#         (
#             'Permissions',
#             {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')},
#         ),
#         ('Important dates', {'fields': ('last_login', 'date_joined')}),
#     )
#     add_fieldsets = (
#         None,
#         {
#             'classes': ('wide',),
#             'fields': (
#                 'business_unit',
#                 'organization',
#                 'department',
#                 'username',
#                 'email',
#                 'password1',
#                 'password2',
#             ),
#         },
#     )
#     form: type[UserChangeForm] = UserChangeForm
#     add_form: type[UserCreationForm] = UserCreationForm
#     change_password_form: type[AdminPasswordChangeForm] = AdminPasswordChangeForm
#     list_display = ('username', 'email', 'is_staff')
#     list_filter = ('is_staff', 'is_superuser', 'groups')
#     search_fields = ('username', 'email')
#     ordering = ('username',)
#     filter_horizontal = (
#         'groups',
#         'user_permissions',
#     )
#     autocomplete_fields: tuple[str, ...] = ('organization', 'department')
#     # inlines: tuple[type[ProfileInline]] = (ProfileInline,)
#
#     def get_queryset(self, request: HttpRequest) -> QuerySet[User]:
#         return (
#             super()
#             .get_queryset(request)
#             .filter(organization_id=request.user.organization_id)
#         )
#
#     def get_fieldsets(self, request: HttpRequest, obj: User | None = None):
#         return super().get_fieldsets(request, obj) if obj else self.add_fieldsets
#
#     def get_form(
#         self,
#         request: HttpRequest,
#         obj: Any | None = ...,
#         *,
#         change: bool = True,
#         **kwargs: Any,
#     ) -> type[ModelForm[User]]:
#         defaults = {}
#         if obj is None:
#             defaults['form'] = self.add_form
#         defaults |= kwargs
#         return super().get_form(request=request, obj=obj, change=True, **defaults)
#
#     def get_urls(self) -> list[URLPattern]:
#         return [
#             path(
#                 '<id>/password/',
#                 self.admin_site.admin_view(self.user_change_password),
#                 name='auth_user_change_password',
#             ),
#             *super().get_urls(),
#         ]
#
#     def lookup_allowed(self, lookup: str, value: str) -> bool:
#         return not lookup.startswith('password') and super().lookup_allowed(
#             lookup,
#             value,
#         )
#
#     @sensitive_post_parameters_m
#     @csrf_protect_m
#     def add_view(
#         self,
#         request: HttpRequest,
#         form_url: str = '',
#         extra_context: Any = None,
#     ) -> HttpResponse:
#         with transaction.atomic(using=router.db_for_write(self.model)):
#             return self._add_view(request, form_url, extra_context)
#
#     def _add_view(
#         self,
#         request: HttpRequest,
#         form_url: str = '',
#         extra_context: dict | None = None,
#     ) -> HttpResponse:
#         if not self.has_change_permission(request):
#             if self.has_add_permission(request) and settings.DEBUG:
#                 raise Http404(
#                     'Your user does not have the "Change user" permission. In '
#                     'order to add users, Django requires that your user '
#                     'account have both the "Add user" and "Change user" '
#                     'permissions set.',
#                 )
#             raise PermissionDenied
#
#         if extra_context is None:
#             extra_context = {}
#
#         username_field = self.model._meta.get_field(
#             self.model.USERNAME_FIELD,
#         )
#         defaults = {
#             'auto_populated_fields': (),
#             'username_help_text': username_field.help_text,
#         }
#         extra_context.update(defaults)
#         return super().add_view(request, form_url, extra_context)
#
#     @sensitive_post_parameters_m
#     def user_change_password(
#         self,
#         request: HttpRequest,
#         id: str,
#         form_url: str = '',
#     ) -> HttpResponseRedirect | TemplateResponse:
#         user = self.get_object(request, unquote(id))
#         if not self.has_change_permission(request, user):
#             raise PermissionDenied
#         if user is None:
#             raise Http404(
#                 f'{self.model._meta.verbose_name} object '
#                 f'with primary key {escape(id)} does not exist.',
#             )
#         if request.method == 'POST':
#             form: AdminPasswordChangeForm = self.change_password_form(
#                 user,
#                 request.POST,
#             )
#             if form.is_valid():
#                 form.save()
#                 change_message = self.construct_change_message(request, form, None)
#                 self.log_change(request, user, change_message)
#                 msg: str = 'Password changed successfully.'
#                 messages.success(request, msg)
#                 update_session_auth_hash(request, form.user)
#                 return HttpResponseRedirect(
#                     reverse(
#                         f'{self.admin_site.name}:{user._meta.app_label}_'
#                         '{user._meta.model_name}_change',
#                         args=(user.pk,),
#                     ),
#                 )
#         else:
#             form: AdminPasswordChangeForm = self.change_password_form(user)
#
#         fieldsets = [(None, {'fields': list(form.base_fields)})]
#         adminForm = admin.helpers.AdminForm(form, fieldsets, {})
#
#         context = {
#             'title': 'Change password: %s' % escape(user.get_username()),
#             'adminForm': adminForm,
#             'form_url': form_url,
#             'form': form,
#             'is_popup': (IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET),
#             'is_popup_var': IS_POPUP_VAR,
#             'add': True,
#             'change': False,
#             'has_delete_permission': False,
#             'has_change_permission': True,
#             'has_absolute_url': False,
#             'opts': self.model._meta,
#             'original': user,
#             'save_as': False,
#             'show_save': True,
#             **self.admin_site.each_context(request),
#         }
#
#         request.current_app = self.admin_site.name
#
#         return TemplateResponse(
#             request,
#             'admin/auth/user/change_password.html',
#             context,
#         )
#
#
# @admin.register(Session)
# class SessionAdmin(ModelAdmin):
#     def _session_data(self, obj):
#         return obj.get_decoded()
#
#     list_display = ('session_key', '_session_data', 'expire_data')
#
#
# # @admin.register(JobTitle)
# # class JobTitleAdmin(GenericAdmin[JobTitle]):
# #     search_fields = ('name',)
# #     list_display = ('name', 'status', 'description')
#
#
# @admin.register(CustomGroup)
# class CustomGroupAdmin(GroupAdmin):
#     list_display = ('name', 'organization', 'business_unit')
#
#
# @admin.register(UserFavorite)
# class UserFavoriteAdmin(ModelAdmin):
#     list_display = ('name', 'page')
