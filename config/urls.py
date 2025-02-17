from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
     path('admin/', admin.site.urls),
     path('', include('dashboard.urls')),  # Dashboard gốc
     # Tính năng Auth (login/logout)
     path('accounts/login/', 
          auth_views.LoginView.as_view(template_name='auth/login.html'), 
          name='login'),

     path('accounts/logout/',
          auth_views.LogoutView.as_view(next_page='/accounts/login/'), 
          name='logout'),

     path('assets/', include('assets.urls.web')),  # Web cho asset
     path('api/assets/', include('assets.urls.api')),  # API cho asset
     path('import-export/', include('import_export.urls')),  # App import_export
     path('import/', include('import_export.urls')), # App import_export
     path('users/', include('users.urls')),  # Include the users app URLs here
     path('groups/', include('groups.urls')),  # Include the groups app URLs here
     path('companies/', include('companies.urls')), # Include the companies app URLs here
     path('departments/', include('departments.urls')), # Include the departments app URLs here
     path('settings_config/', include('settings_config.urls.web')), # Include the settings app URLs here
]
