import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from eventapp.models import UserProfile

# Check if admin exists
admin_user = User.objects.filter(username='admin').first()

if admin_user:
    admin_user.profile.role = 'admin'
    admin_user.profile.save()
    print(f'Admin role updated for user: {admin_user.username}')
else:
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    admin_user.profile.role = 'admin'
    admin_user.profile.save()
    print(f'Admin user created: {admin_user.username}')

print(f'Username: admin')
print(f'Password: admin123')
print(f'Role: {admin_user.profile.get_role_display()}')
