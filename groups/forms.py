from django import forms
from django.contrib.auth.models import Group, Permission

class GroupForm(forms.ModelForm):
    """
    Form quản lý Groups (nhóm người dùng)
    - Hỗ trợ chọn các permissions có sẵn
    """
    permissions = forms.ModelMultipleChoiceField(
        queryset=Permission.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Group
        fields = ['name', 'permissions']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['permissions'].queryset = Permission.objects.all()
