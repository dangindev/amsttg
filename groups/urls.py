from django.urls import path
from .views import group_list_view, group_form_view, group_delete_view

urlpatterns = [
    path('', group_list_view, name='group_list'),
    path('create/', group_form_view, name='group_create'),  
    path('edit/<int:group_id>/', group_form_view, name='group_edit'),
    path('delete/<int:group_id>/', group_delete_view, name='group_delete'),
]
