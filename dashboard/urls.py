from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='dashboard_index'),  # Trang gốc => Dashboard
    path('users/', views.user_list_view, name='user_list'),
    path('users/<int:user_id>/', views.user_detail_view, name='user_detail'),
    path('groups/', views.group_list_view, name='group_list'),
    path('groups/<int:group_id>/', views.group_detail_view, name='group_detail'),
]
