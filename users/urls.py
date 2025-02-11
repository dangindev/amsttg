from django.urls import path
from .views import user_list_view, user_form_view, user_delete_view

urlpatterns = [
    path('', user_list_view, name='user_list'),
    path('form/', user_form_view, name='user_create'),  # Create user
    path('form/<int:user_id>/', user_form_view, name='user_edit'),  # Edit user
    path('delete/<int:user_id>/', user_delete_view, name='user_delete'),
]
