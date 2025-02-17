from django import forms
from .models import LdapConfig

class LdapConfigForm(forms.ModelForm):
    class Meta:
        model = LdapConfig
        fields = ['server_uri', 'bind_dn', 'bind_password', 'base_dn', 'search_filter']
        widgets = {
            'bind_password': forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        }
