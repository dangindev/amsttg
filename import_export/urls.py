from django.urls import path
from .views import (
    upload_csv_view,
    mapping_confirm_view,
    import_start_view,
    import_progress_view,
    import_progress_status_json,
)

urlpatterns = [
    path('upload/', upload_csv_view, name='upload_csv'),             # Bước 1
    path('map-confirm/', mapping_confirm_view, name='mapping_confirm'),  # Bước 2
    path('start/', import_start_view, name='import_start'),          # Bước 3
    path('progress/<str:task_id>/', import_progress_view, name='import_progress'),    # Bước 4
    path('progress-status/<str:task_id>/', import_progress_status_json, name='import_progress_status'),
]
