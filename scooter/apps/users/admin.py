from django.contrib import admin
# models
from scooter.apps.users.models import User


class CustomUserAdmin(admin.ModelAdmin):
    """ User model admin """
    list_display = ('username', 'is_staff', 'is_client', 'auth_facebook', 'last_login')
    list_filter = ('is_client', 'is_staff', 'created', 'modified')


admin.site.register(User, CustomUserAdmin)
