from django.db import models
from django.contrib.auth.models import User
from departments.models import Department

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=30, blank=True, null=True)  # Tăng lên 30
    old_employee_code = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, null=True)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    is_ldap_user = models.BooleanField(default=False)
    employee_code = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.username
