from django.contrib import admin
from .models import CustomUser, Branch, Schedule


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',
                    'user_type', 'is_staff', 'is_active')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Branch)
admin.site.register(Schedule)
