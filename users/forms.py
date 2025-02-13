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
        help_text="Raw passwords are not stored, so there is no way to see this user's password.",
        required=False
    )

    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Set a password for the new user."
    )

    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput,
        required=False,
        help_text="Enter the same password as before, for verification."
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
            'password', 'new_password', 'confirm_password', 'is_active', 'is_staff', 'is_superuser', 
            'groups', 'user_permissions', 'last_login', 'date_joined'
        ]
        widgets = {
            'last_login': forms.TextInput(attrs={'readonly': 'readonly'}),
            'date_joined': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def clean_password(self):
        """ Không cho phép chỉnh sửa mật khẩu trực tiếp từ form """
        return self.initial.get("password", "")

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.cleaned_data['new_password']:
            user.set_password(self.cleaned_data['new_password'])
        if commit:
            user.save()
        return user