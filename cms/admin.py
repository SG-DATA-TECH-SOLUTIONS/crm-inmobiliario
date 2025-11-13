from django.contrib import admin
from teams.models import Teams
from contacts.models import Contact

@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone', 'teams', 'created_at']
    list_filter = ['teams', 'created_at']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['created_at', 'updated_at']