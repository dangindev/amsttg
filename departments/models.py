from django.db import models
from django.contrib.auth import get_user_model
from companies.models import Company

class Department(models.Model):
    name = models.CharField(max_length=200)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='departments')
    manager = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, related_name='managed_departments')
    location = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['company', 'name']

    def __str__(self):
        return f"{self.name} ({self.company.name})"