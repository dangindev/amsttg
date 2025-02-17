from django.db import models

class LdapConfig(models.Model):
    """
    Bảng lưu cấu hình LDAP
    """
    server_uri = models.CharField(max_length=200, blank=True, null=True)
    bind_dn = models.CharField(max_length=200, blank=True, null=True)
    bind_password = models.CharField(max_length=200, blank=True, null=True)
    base_dn = models.CharField(max_length=300, blank=True, null=True)
    search_filter = models.CharField(max_length=300, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"LDAP Config (server={self.server_uri})"
