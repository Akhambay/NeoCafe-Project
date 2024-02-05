from django.contrib import admin
from .models import CustomUser, Branch, Schedule


class BranchAdmin(admin.ModelAdmin):
    filter_horizontal = ('schedule',)


admin.site.register(Branch, BranchAdmin)
admin.site.register(Schedule)
admin.site.register(CustomUser)
