# assets/urls/web.py

from django.urls import path
from assets.views.asset_views import (
    asset_list_view,
    asset_detail_view,
    asset_form_view,
    asset_delete_view,
    asset_import_view,       # new
    asset_export_view,       # new
)

urlpatterns = [
    path('', asset_list_view, name='asset_list'),
    path('<int:pk>/', asset_detail_view, name='asset_detail'),
    path('form/', asset_form_view, name='asset_create'),
    path('form/<int:pk>/', asset_form_view, name='asset_edit'),
    path('delete/', asset_delete_view, name='asset_delete'),

    # Import & Export
    path('import/', asset_import_view, name='asset_import'),
    path('export/', asset_export_view, name='asset_export'),
]
