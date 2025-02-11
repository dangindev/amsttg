from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserChangeForm

class UserForm(UserChangeForm):
    """
    User form for both creating and editing users.
    Includes:
    - Username
    - Email
    - Password Reset Link
    - First Name, Last Name
    - is_staff (Admin role)
    - is_superuser (Full permission)
    - Groups (User Groups)
    - User permissions (Custom permissions)
    - last_login, date_joined (Readonly)
    """
    
    password = forms.CharField(
        label="Password",
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        help_text="Raw passwords are not stored, so there is no way to see this user's password."
    )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        help_text="The groups this user belongs to. Hold down 'Control', or 'Command' on a Mac, to select more than one."
    )

    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control'}),
        required=False,
        help_text="Specific permissions for this user."
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'is_active', 'is_staff', 'is_superuser', 
            'groups', 'user_permissions', 'last_login', 'date_joined'
        ]
        widgets = {
            'last_login': forms.TextInput(attrs={'readonly': 'readonly'}),
            'date_joined': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean_password(self):
        """ Không cho phép chỉnh sửa mật khẩu trực tiếp từ form """
        return self.initial["password"]
