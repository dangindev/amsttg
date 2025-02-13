import logging
from django import forms
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth.forms import UserChangeForm
from .models import UserProfile
from departments.models import Department

logger = logging.getLogger(__name__)

class UserForm(UserChangeForm):
    # UserProfile fields
    department = forms.ModelChoiceField(
        queryset=Department.objects.all(), 
        required=False,
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    old_employee_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    title = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    manager = forms.ModelChoiceField(
        queryset=UserProfile.objects.none(),
        required=False,
        label="Manager",
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )

    # NEW FIELD: employee_code
    employee_code = forms.CharField(
        required=False,
        label="Employee Code",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    # NEW FIELD: is_ldap_user
    is_ldap_user = forms.BooleanField(
        required=False,
        label="LDAP User?",
        help_text="If checked, this user is recognized as LDAP-based."
    )

    # Password fields
    password = forms.CharField(
        label="Password",
        widget=forms.TextInput(attrs={
            'readonly': 'readonly',
            'class': 'form-control'
        }),
        help_text="Raw passwords are not stored, so there is no way to see this user's password.",
        required=False
    )
    new_password = forms.CharField(
        label="New Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Set a password for the new user."
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=False,
        help_text="Enter the same password as before, for verification."
    )

    # Permission fields
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
        help_text="The groups this user belongs to. Hold down 'Control', or 'Command' on a Mac, to select more than one."
    )
    user_permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-control select2'}),
        required=False,
        help_text="Specific permissions for this user."
    )

    class Meta:
        model = User
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'password', 'new_password', 'confirm_password', 
            'is_active', 'is_staff', 'is_superuser', 
            'groups', 'user_permissions', 'last_login', 'date_joined', 
            'department', 'phone_number', 'old_employee_code', 'title', 'manager',

            # NEW FIELD: add them in Meta.fields
            'employee_code',
            'is_ldap_user',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_login': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'date_joined': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set manager queryset excluding current user's profile
        if self.instance and self.instance.pk:
            try:
                current_profile = UserProfile.objects.get(user=self.instance)
                self.fields['manager'].queryset = UserProfile.objects.exclude(pk=current_profile.pk)
            except UserProfile.DoesNotExist:
                self.fields['manager'].queryset = UserProfile.objects.all()
        else:
            self.fields['manager'].queryset = UserProfile.objects.all()
            
        self.fields['manager'].label_from_instance = self.get_manager_label

        # Load initial UserProfile data if exists
        if self.instance and hasattr(self.instance, 'userprofile'):
            up = self.instance.userprofile
            self.initial.update({
                'department': up.department,
                'phone_number': up.phone_number,
                'old_employee_code': up.old_employee_code,
                'title': up.title,
                'manager': up.manager,

                # NEW: load employee_code, is_ldap_user
                'employee_code': up.employee_code,
                'is_ldap_user': up.is_ldap_user,
            })

    def get_manager_label(self, obj):
        """Format the manager display in select box"""
        # obj is now a UserProfile instance
        title = obj.title if obj.title else "No Title"
        return f"{obj.user.username} - [{title}]"

    def clean_password(self):
        """Prevent direct password editing"""
        return self.initial.get("password", "")

    def clean(self):
        """Validate form data"""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and new_password != confirm_password:
            self.add_error('confirm_password', "The two password fields must match.")

        return cleaned_data

    def save(self, commit=True):
        """Save both User and UserProfile models"""
        # Save User instance
        user = super().save(commit=False)
        if self.cleaned_data.get('new_password'):
            user.set_password(self.cleaned_data['new_password'])
        
        if commit:
            user.save()
            self.save_m2m()  # Save many-to-many fields

            # Update or create UserProfile
            profile_data = {
                'department': self.cleaned_data.get('department'),
                'phone_number': self.cleaned_data.get('phone_number'),
                'old_employee_code': self.cleaned_data.get('old_employee_code'),
                'title': self.cleaned_data.get('title'),
                'manager': self.cleaned_data.get('manager'),

                # NEW: pass employee_code, is_ldap_user
                'employee_code': self.cleaned_data.get('employee_code'),
                'is_ldap_user': self.cleaned_data.get('is_ldap_user'),
            }

            try:
                user_profile, created = UserProfile.objects.update_or_create(
                    user=user,
                    defaults=profile_data
                )
                logger.info(f"User saved: {user.username}")
                logger.info(f"UserProfile {'created' if created else 'updated'}: {user_profile}")
                logger.info(f"Profile data: {profile_data}")
            except Exception as e:
                logger.error(f"Error saving UserProfile: {str(e)}")
                raise

        return user
