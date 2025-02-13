import logging
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .forms import UserForm
from .models import UserProfile

# Cấu hình logger
logger = logging.getLogger(__name__)

@login_required
def user_form_view(request, user_id=None):
    """
    Handles both user creation and editing.
    """
    if user_id:
        user_obj = get_object_or_404(User, pk=user_id)
        user_profile, created = UserProfile.objects.get_or_create(user=user_obj)
    else:
        user_obj = None
        user_profile = None

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user_obj)
        if form.is_valid():
            try:
                # Save User model first
                user = form.save(commit=False)
                if form.cleaned_data['new_password']:
                    user.set_password(form.cleaned_data['new_password'])
                user.save()
                form.save_m2m()  # Save groups and permissions

                # Now handle UserProfile
                profile_data = {
                    'department': form.cleaned_data.get('department'),
                    'phone_number': form.cleaned_data.get('phone_number'),
                    'old_employee_code': form.cleaned_data.get('old_employee_code'),
                    'title': form.cleaned_data.get('title'),
                    'manager': form.cleaned_data.get('manager')
                }

                # Update or create UserProfile
                user_profile, created = UserProfile.objects.update_or_create(
                    user=user,
                    defaults=profile_data
                )

                print(f"Debug - Profile Data: {profile_data}")  # Debug print
                print(f"Debug - Updated Profile: {user_profile.__dict__}")  # Debug print

                messages.success(request, "User saved successfully.")
                return redirect('user_list')
                
            except Exception as e:
                print(f"Debug - Error: {str(e)}")  # Debug print
                messages.error(request, f"Error: {str(e)}")
        else:
            print(f"Debug - Form Errors: {form.errors}")  # Debug print
            messages.error(request, "There were errors in the form.")
    else:
        # GET request - show form
        initial_data = {}
        if user_profile:
            initial_data = {
                'department': user_profile.department,
                'phone_number': user_profile.phone_number,
                'old_employee_code': user_profile.old_employee_code,
                'title': user_profile.title,
                'manager': user_profile.manager
            }
        form = UserForm(instance=user_obj, initial=initial_data)

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