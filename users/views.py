import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UserForm

# Cấu hình logger
logger = logging.getLogger(__name__)

@login_required
def user_form_view(request, user_id=None):
    """
    Handles both user creation and editing.
    - If `user_id` is provided, loads user for editing.
    - If not, creates a new user.
    - Redirects back to user list after save.
    """
    if user_id:
        user_obj = get_object_or_404(User, pk=user_id)
    else:
        user_obj = None

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_obj)
        if form.is_valid():
            try:
                new_user = form.save(commit=False)
                new_user.save()
                form.save_m2m()  # Lưu groups và permissions
                messages.success(request, "User saved successfully.")
                return redirect('user_list')
            except Exception as e:
                logger.error(f"Error saving user: {str(e)}")
                messages.error(request, f"Error: {str(e)}")
        else:
            logger.error(f"Form validation failed: {form.errors.as_json()}")
            messages.error(request, "There were errors in the form. Please check the fields.")

    else:
        form = UserForm(instance=user_obj)

    return render(request, 'users/edit.html', {'form': form, 'user': user_obj})

@login_required
def user_list_view(request):
    users = User.objects.all()
    return render(request, 'users/list.html', {'users': users})

@login_required
def user_detail_view(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    return render(request, 'users/detail.html', {'user': user_obj})

@login_required
def user_delete_view(request, user_id):
    user_obj = get_object_or_404(User, pk=user_id)
    # Prevent deletion of Superadmin account.
    if user_obj.is_superuser:
        messages.error(request, "Superadmin account cannot be deleted.")
        return redirect('user_list')
    if request.method == 'POST':
        user_obj.delete()
        messages.success(request, "User deleted successfully.")
        return redirect('user_list')
    return render(request, 'users/delete_confirm.html', {'user': user_obj})