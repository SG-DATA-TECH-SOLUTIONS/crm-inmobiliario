from django.contrib import admin
from contacts.models import Contact
from teams.models import Teams

@admin.register(Teams)
class TeamsAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']

@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = [
        'first_name',
        'last_name',
        'primary_email',
        'mobile_number',
        'teams_list',
        'created_at'
    ]
    list_filter = ['teams', 'created_at', 'is_active']
    search_fields = ['first_name', 'last_name', 'primary_email', 'mobile_number']
    readonly_fields = ['created_at', 'updated_at']

    #mestra los equipos asociados como texto ens el litado?
    def teams_list(self, obj):
        return ", ".join([t.name for t in obj.teams.all()])
    teams_list.short_description = 'Teams'
