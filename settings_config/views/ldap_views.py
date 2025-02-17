from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from settings_config.models import LdapConfig
from settings_config.forms import LdapConfigForm

@login_required
def ldap_list_view(request):
    """
    Hiển thị danh sách cấu hình LDAP.
    """
    configs = LdapConfig.objects.all()
    return render(request, 'settings_config/ldap/list.html', {
        'configs': configs
    })

@login_required
def ldap_edit_view(request, config_id=None):
    """
    Tạo hoặc sửa 1 LdapConfig
    """
    if config_id:
        config_obj = get_object_or_404(LdapConfig, pk=config_id)
    else:
        config_obj = None

    if request.method == 'POST':
        form = LdapConfigForm(request.POST, instance=config_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "LDAP config saved successfully.")
            return redirect('ldap_list')
        else:
            messages.error(request, "Error saving LDAP config.")
    else:
        form = LdapConfigForm(instance=config_obj)

    return render(request, 'settings_config/ldap/edit.html', {
        'form': form,
        'config_obj': config_obj
    })
