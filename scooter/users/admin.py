from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
# models
from scooter.users.models import User, Customer


class CustomUserAdmin(admin.ModelAdmin):
    """ User model admin """
    list_display = ('email', 'is_staff', 'is_client', 'auth_facebook', 'last_login')
    list_filter = ('is_client', 'is_staff', 'created', 'modified')


@admin.register(Customer)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'last_name', 'birthdate', 'phone_number', 'reputation')
    search_fields = ('name', 'last_name', 'phone_number')


admin.site.register(User, CustomUserAdmin)
