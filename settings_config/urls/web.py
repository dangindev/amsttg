from django.urls import path
from settings_config.views.main_views import settings_list_view
from settings_config.views.ldap_views import ldap_list_view, ldap_edit_view

urlpatterns = [
    # Màn hình tổng hợp
    path('', settings_list_view, name='settingsconfig_list'),

    # Màn hình LDAP
    path('ldap/', ldap_list_view, name='ldap_list'),
    path('ldap/create/', ldap_edit_view, name='ldap_create'),
    path('ldap/<int:config_id>/edit/', ldap_edit_view, name='ldap_edit'),
]
