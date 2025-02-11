from django import forms
from .models.asset import Asset

class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['name', 'code', 'description']
