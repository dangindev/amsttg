from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required

@login_required
def index(request):
    """
    Trang dashboard chính, thống kê sơ bộ
    """
    user_count = User.objects.count()
    group_count = Group.objects.count()
    # Bạn có thể thêm thống kê khác ở đây (VD: số Assets, v.v.)
    return render(request, 'dashboard/index.html', {
        'user_count': user_count,
        'group_count': group_count,
    })

@login_required
def user_list_view(request):
    """
    Hiển thị danh sách tất cả user trong hệ thống
    """
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    """
    Hiển thị chi tiết 1 user. Lấy user theo ID
    """
    user_obj = get_object_or_404(User, pk=user_id)
    return render(request, 'users/detail.html', {'user': user_obj})

@login_required
def group_list_view(request):
    """
    Hiển thị danh sách tất cả groups
    """
    groups = Group.objects.all()
    return render(request, 'groups/list.html', {'groups': groups})

@login_required
def group_detail_view(request, group_id):
    """
    Hiển thị chi tiết 1 group (các permissions, member,...)
    """
    group_obj = get_object_or_404(Group, pk=group_id)
    return render(request, 'groups/detail.html', {'group': group_obj})
