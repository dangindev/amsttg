from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User
from users.models import UserProfile

# Thư viện ldap3
from ldap3 import Server, Connection, ALL, SUBTREE

PAGE_SIZE = 500

class Command(BaseCommand):
    help = "Sync all LDAP users via ldap3, avoiding SIZELIMIT_EXCEEDED"

    def handle(self, *args, **options):
        ldap_server = getattr(settings, "AUTH_LDAP_SERVER_URI", None)  # "ldap://10.1.4.21"
        bind_dn = getattr(settings, "AUTH_LDAP_BIND_DN", None)         # "CN=SV-BCNTT.AMS,..."
        bind_password = getattr(settings, "AUTH_LDAP_BIND_PASSWORD", None)

        base_dn = "OU=USERS,OU=HO,OU=HANOI,DC=ttgroup,DC=com,DC=vn"
        search_filter = "(&(cn=*))"
        attributes = [
            "sAMAccountName", "employeeID", "givenName", "sn",
            "mail", "mobile", "title", "department"
        ]

        self.stdout.write(self.style.NOTICE(f"Connecting to {ldap_server} via ldap3..."))

        # 1) Tạo server + connection
        server = Server(ldap_server, get_info=ALL)  # get_info=ALL optional
        conn = Connection(server, user=bind_dn, password=bind_password, auto_bind=True)

        count_created = 0
        count_updated = 0
        total_processed = 0

        # cookie cho paging
        cookie = None

        while True:
            # 2) Thực hiện search với paged_size
            conn.search(
                search_base=base_dn,
                search_filter=search_filter,
                search_scope=SUBTREE,
                attributes=attributes,
                paged_size=PAGE_SIZE,
                paged_cookie=cookie
            )

            # 3) Lấy kết quả
            entries = conn.entries
            for entry in entries:
                # entry là 1 đối tượng ldap3, ta truy cập field
                username   = str(entry.sAMAccountName) if 'sAMAccountName' in entry else None
                first_name = str(entry.givenName)      if 'givenName' in entry else None
                last_name  = str(entry.sn)             if 'sn' in entry else None
                email      = str(entry.mail)           if 'mail' in entry else None
                employeeid = str(entry.employeeID)     if 'employeeID' in entry else None
                phone      = str(entry.mobile)         if 'mobile' in entry else None
                title      = str(entry.title)          if 'title' in entry else None
                department = str(entry.department)     if 'department' in entry else None

                if not username:
                    continue

                # Tạo/Update user
                user_obj, created = User.objects.get_or_create(username=username)
                user_obj.first_name = first_name or ""
                user_obj.last_name  = last_name or ""
                user_obj.email      = email or ""
                user_obj.is_active  = True
                user_obj.save()

                # Tạo/Update UserProfile
                defaults_profile = {
                    'is_ldap_user': True,
                    'employee_code': employeeid or "",
                    'phone_number': phone or "",
                    'title': title or "",
                    # 'department': ...,
                }
                UserProfile.objects.update_or_create(
                    user=user_obj,
                    defaults=defaults_profile
                )

                if created:
                    count_created += 1
                else:
                    count_updated += 1

                total_processed += 1

            # 4) Lấy cookie cho trang tiếp
            cookie = conn.result.get('controls', {}) \
                        .get('1.2.840.113556.1.4.319', {}) \
                        .get('value', {}) \
                        .get('cookie', None)

            # Nếu cookie rỗng => hết data
            if not cookie:
                break

        conn.unbind()
        self.stdout.write(self.style.SUCCESS(
            f"Done. Created={count_created}, Updated={count_updated}, "
            f"Total processed={total_processed}"
        ))
