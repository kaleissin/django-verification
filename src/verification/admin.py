from __future__ import unicode_literals

from django.contrib import admin

from .models import Key, KeyGroup

class ClaimedListFilter(admin.SimpleListFilter):
    title = 'Claimed'
    parameter_name = 'claimed_by'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'Yes':
            return queryset.exclude(claimed_by=None)
        if self.value() == 'No':
            return queryset.filter(claimed_by=None)

class KeyAdmin(admin.ModelAdmin):
    model = Key
    list_display = ('key', 'group', 'pub_date', 'claimed_by', 'expires')
    list_filter = ('group', ClaimedListFilter)
    search_fields = ('key', 'claimed_by__username', 'claimed_by__email')
    date_hierarchy = 'pub_date'

class KeyGroupAdmin(admin.ModelAdmin):
    model = KeyGroup
    list_display = ('name', 'ttl', 'generator', 'has_fact')
    list_filter = ('generator', 'has_fact',)

admin.site.register(Key, KeyAdmin)
admin.site.register(KeyGroup, KeyGroupAdmin)
