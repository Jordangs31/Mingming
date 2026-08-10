from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import mark_safe
from .models import CustomUser,Property, PropertyImage, Review, Partner

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'user_type', 'is_verified', 'is_staff']
    list_filter = ['user_type', 'is_verified', 'is_staff', 'is_superuser']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Property)
admin.site.register(PropertyImage)
admin.site.register(Review)

@admin.register(Partner)
class PartnerAdmin(admin.ModelAdmin):
    list_display = ('name', 'website')
