from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def settings_list_view(request):
    """
    Màn hình tổng hợp Settings
    """
    return render(request, 'settings_config/list.html')
