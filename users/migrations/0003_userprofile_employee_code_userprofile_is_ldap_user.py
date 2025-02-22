# Generated by Django 5.1.6 on 2025-02-13 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0002_alter_userprofile_department_delete_department"),
    ]

    operations = [
        migrations.AddField(
            model_name="userprofile",
            name="employee_code",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="userprofile",
            name="is_ldap_user",
            field=models.BooleanField(default=False),
        ),
    ]
