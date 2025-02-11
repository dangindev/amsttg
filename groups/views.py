import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, Permission
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import GroupForm

# Cấu hình logger
logger = logging.getLogger(__name__)

@login_required
def group_list_view(request):
    """
    Hiển thị danh sách các nhóm (groups)
    """
    groups = Group.objects.all()
    return render(request, 'groups/list.html', {'groups': groups})

@login_required
def group_form_view(request, group_id=None):
    """
    Xử lý tạo mới hoặc chỉnh sửa nhóm
    - Nếu `group_id` có giá trị -> Chỉnh sửa nhóm
    - Nếu không -> Tạo nhóm mới
    """
    if group_id:
        group_obj = get_object_or_404(Group, pk=group_id)
    else:
        group_obj = None

    if request.method == 'POST':
        form = GroupForm(request.POST, instance=group_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Group saved successfully.")
            return redirect('group_list')
        else:
            logger.error(f"Form validation failed: {form.errors.as_json()}")
            messages.error(request, "There were errors in the form. Please check the fields.")
    else:
        form = GroupForm(instance=group_obj)

    return render(request, 'groups/edit.html', {'form': form, 'group': group_obj})

@login_required
def group_delete_view(request, group_id):
    """
    Xóa nhóm (group)
    """
    group_obj = get_object_or_404(Group, pk=group_id)

    if request.method == 'POST':
        group_obj.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect('group_list')

    return redirect('group_list')
