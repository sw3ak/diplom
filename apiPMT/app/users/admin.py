from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ['username', 'position', 'teams_display']
    list_filter = ['position']
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('position',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    search_fields = ['username']
    ordering = ['username']

    def teams_display(self, obj):
        return ", ".join([team.name for team in obj.teams.all()])

    teams_display.short_description = 'Команды'


admin.site.register(User, CustomUserAdmin)
